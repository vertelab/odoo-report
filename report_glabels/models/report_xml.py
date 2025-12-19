# -*- coding: utf-8 -*-
import os
import tempfile
import base64
import logging
import gzip
import subprocess
import xml.etree.ElementTree as ET
from io import BytesIO
from PIL import Image
from odoo.exceptions import UserError
from odoo import models, fields, api
import unicodecsv as csv

_logger = logging.getLogger(__name__)

# http://jamesmcdonald.id.au/it-tips/using-gnubarcode-to-generate-a-gs1-128-barcode
# https://github.com/zint/zint

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _get_csv_fields(self):
        self.csv_fields = ','.join(sorted(self.env[self.model]._fields.keys()))

    report_type = fields.Selection(
        selection_add=[('qweb-glabels', 'Glabels')],
        ondelete={'qweb-glabels': 'set default'}
    )
    glabels_template = fields.Binary(string="Glabels template")
    label_count = fields.Integer(
        string="Count", default=1,
        help="One if you want to fill the sheet with new records")
    col_name = fields.Char(string="Column")
    col_value = fields.Char(string="Column")
    csv_fields = fields.Text(compute="_get_csv_fields")

    def _process_image_field(self, field_name, field_value, record_id, temp_dir):
        try:
            # Decode the image data
            if isinstance(field_value, bytes):
                # Check if it's base64 text stored as bytes
                try:
                    v_str = field_value.decode('utf-8')
                    img_data = base64.b64decode(v_str)
                except (UnicodeDecodeError, base64.binascii.Error):
                    # It's raw binary data
                    img_data = field_value
            elif isinstance(field_value, str):
                img_data = base64.b64decode(field_value)
            else:
                _logger.warning(f"Unexpected image data type for {field_name}: {type(field_value)}")
                return ''

            # Open and process image with PIL
            img = Image.open(BytesIO(img_data))
            _logger.info(f"Processing image: {field_name} - {img.format} {img.size} {img.mode}")

            # Convert palette mode to RGBA to preserve transparency
            if img.mode == 'P':
                img = img.convert('RGBA')

            # Save as PNG
            png_buffer = BytesIO()
            img.save(png_buffer, format='PNG', optimize=True)
            final_img_data = png_buffer.getvalue()

            # Create image file with unique name
            img_filename = f"{field_name}_{record_id}.png"
            img_path = os.path.join(temp_dir, img_filename)

            # Write image file
            with open(img_path, 'wb') as img_file:
                img_file.write(final_img_data)

            # Set permissions
            os.chmod(img_path, 0o666)

            # Verify file was created
            if os.path.exists(img_path):
                _logger.info(f"Image saved: {img_path} ({len(final_img_data)} bytes)")
                return img_path
            else:
                _logger.error(f"Failed to create image file: {img_path}")
                return ''

        except Exception as e:
            _logger.error(f"Failed to process image field {field_name}: {e}")
            return ''

    def render_glabels(self, report_ref, res_ids, data):
        report = self._get_report(report_ref)

        if not report.glabels_template:
            raise UserError("No glabel template has been selected.")

        # Create a persistent directory for images
        TEMP_IMG_DIR = '/tmp/odoo_glabels_images'
        if not os.path.exists(TEMP_IMG_DIR):
            os.makedirs(TEMP_IMG_DIR, mode=0o777)

        # Decompress the glabels template
        template_data = base64.b64decode(report.glabels_template)

        # Create temporary files
        glabels_temp = tempfile.NamedTemporaryFile(mode='w+b', suffix='.glabels', delete=False)
        glabels_temp.write(template_data)
        glabels_temp.close()

        csv_temp = tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False)
        outfile = tempfile.NamedTemporaryFile(mode='w+b', suffix='.pdf', delete=False)

        temp_image_files = []

        try:
            # Process records and prepare data
            records_data = []
            for p in self.env[report.model].browse(res_ids).read():
                record_id = p.get('id')

                processed_data = {}
                for k, v in p.items():
                    # Handle image fields
                    field_obj = self.env[report.model]._fields.get(k)

                    if field_obj and field_obj.type in ('binary', 'image') and v:
                        # Process image field using the dedicated method
                        img_path = self._process_image_field(k, v, record_id, TEMP_IMG_DIR)
                        processed_data[k] = img_path
                        if img_path:
                            temp_image_files.append(img_path)
                    else:
                        # Handle regular fields
                        if isinstance(v, bool):
                            processed_data[k] = str(v)
                        elif isinstance(v, (int, float)):
                            processed_data[k] = str(v)
                        elif isinstance(v, str):
                            processed_data[k] = v
                        elif v is None or v is False:
                            processed_data[k] = ''
                        else:
                            processed_data[k] = str(v)

                # Add record multiple times based on label_count
                for _ in range(report.label_count):
                    records_data.append(processed_data.copy())

            # Write CSV file
            if records_data:
                fieldnames = records_data[0].keys()
                writer = csv.DictWriter(csv_temp, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records_data)
                csv_temp.close()

            # Modify the glabels template to use our CSV
            # Read glabels file (gzipped XML)
            with gzip.open(glabels_temp.name, 'rb') as f:
                xml_content = f.read().decode('utf-8')

            # Parse and modify XML
            root = ET.fromstring(xml_content)

            # Find and update Merge element
            ns = {'gl': 'http://glabels.org/xmlns/3.0/'}
            merge_elem = root.find('.//gl:Merge', ns)

            if merge_elem is not None:
                merge_elem.set('src', csv_temp.name)

            # Write modified template
            modified_glabels = tempfile.NamedTemporaryFile(mode='w+b', suffix='.glabels', delete=False)
            modified_xml = ET.tostring(root, encoding='utf-8', xml_declaration=True)

            with gzip.open(modified_glabels.name, 'wb') as f:
                f.write(modified_xml)
            modified_glabels.close()

            # Run glabels-3-batch
            cmd = [
                'glabels-3-batch',
                '-o', outfile.name,
                '-l',
                '-C',
                '-i', csv_temp.name,
                modified_glabels.name
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                _logger.error(f"glabels-3-batch failed: {result.stderr}")

            # Check PDF
            if not os.path.exists(outfile.name) or os.path.getsize(outfile.name) == 0:
                raise UserError("Failed to generate PDF. Check Odoo logs for details.")

            # Read PDF
            with open(outfile.name, 'rb') as f:
                pdf = f.read()

            return (pdf, 'pdf')

        except Exception as e:
            _logger.error(f"Error: {e}", exc_info=True)
            raise UserError(f"Failed to generate report: {str(e)}")

        finally:
            # Cleanup temp files
            for temp_file in [glabels_temp.name, csv_temp.name, outfile.name]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
            try:
                if 'modified_glabels' in locals():
                    os.unlink(modified_glabels.name)
            except:
                pass

    @api.model
    def _render_qweb_glabels(self, report_ref, res_ids=None, data=None):
        if not data:
            data = {}
        data.setdefault('report_type', 'glabels')
        return self.render_glabels(report_ref, res_ids, data)
