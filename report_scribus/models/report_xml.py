import re
import io
import logging
from odoo.tools.safe_eval import safe_eval, time

from odoo.exceptions import RedirectWarning, UserError
from odoo import models, fields, api, http, registry
from odoo.modules import get_module_path
import unicodecsv as csv
import os
import tempfile
import base64
import traceback

_logger = logging.getLogger(__name__)

_logger.warning("loading model")

try:
    from PyPDF2 import PdfFileMerger, PdfFileReader
except:
    _logger.warning('PyPDF2 missing, sudo pip install pypdf2')


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    fake_report_type = fields.Selection(
        selection_add=[('scribus_sla', 'Scribus SLA'), ('scribus_pdf', 'Scribus PDF')],
        ondelete={'scribus_sla': 'set default', 'scribus_pdf': 'set default'}
    )

    scribus_template = fields.Binary(string="Scribus template")

    def newfilename(self):
        # Changed delete=False so the file persists until we manually delete it
        outfile = tempfile.NamedTemporaryFile(mode='w+b', suffix='.pdf', delete=False)
        filename = outfile.name
        outfile.close()  # Added () to actually call close
        return filename

    def render(self, report_id, record, template):
        """Render Scribus template with proper Odoo context"""

        try:
            # Get the actual record object
            obj = self.env[report_id.model].browse(record["id"])

            # Create evaluation context similar to QWeb reports
            eval_context = {
                'object': obj,
                'o': obj,
                'user': self.env.user,
                'time': time,
                'company': self.env.company,
                'res_company': self.env.company,
            }

            # Simple string replacement for ${expression}
            def safe_replace(match):
                expr = match.group(1).strip()
                try:
                    result = safe_eval(expr, eval_context, mode='eval', nocopy=True)
                    return str(result) if result is not None else ''
                except Exception as e:
                    _logger.warning(f"Could not evaluate '{expr}': {e}")
                    return ''

            rendered = re.sub(r'\$\{([^}]+)\}', safe_replace, template)

            # For SLA return type, use StringIO
            if report_id.fake_report_type == 'scribus_sla':
                return io.StringIO(rendered)

            # For PDF generation, Scribus needs a real file
            sla = tempfile.NamedTemporaryFile(mode='w+t', suffix='.sla', delete=False)
            sla.write(rendered)
            sla.flush()
            sla.seek(0)

            return sla

        except Exception as e:
            _logger.error(f"Error rendering Scribus template: {str(e)}")
            _logger.error(traceback.format_exc())
            raise UserError(f'Error rendering Scribus template: {str(e)}')

    def render_scribus(self, report_id, res_ids, data):
        template = base64.b64decode(report_id.scribus_template).decode("utf-8") if report_id.scribus_template else ''

        if not template:
            raise UserError('No Scribus template defined for this report')

        # Handle SLA output (no PDF generation needed)
        if report_id.fake_report_type == 'scribus_sla':
            sla_contents = []
            for p in self.env[report_id.model].browse(res_ids).read():
                sla = self.render(report_id, p, template)
                content = sla.getvalue()  # Get string from StringIO
                sla.close()
                sla_contents.append(content)

            # Return first SLA or concatenated SLAs
            final_content = sla_contents[0] if len(sla_contents) == 1 else '\n\n'.join(sla_contents)
            return (final_content.encode('utf-8'), 'sla')

        # Handle PDF output (requires Scribus processing)
        merger = PdfFileMerger()
        outfiles = []
        sla_files = []

        try:
            for p in self.env[report_id.model].browse(res_ids).read():
                outfiles.append(self.newfilename())
                sla = self.render(report_id, p, template)
                sla_files.append(sla.name)

                command = "xvfb-run -a scribus -ns -g %s -py %s -pa -o %s" % (
                    sla.name,
                    os.path.join(get_module_path('report_scribus'), 'scribus.py'),
                    outfiles[-1]
                )
                _logger.info(f"Executing: {command}")
                res = os.system(command)
                sla.close()

                if not os.path.exists(outfiles[-1]) or os.stat(outfiles[-1]).st_size == 0:
                    _logger.error(f"Scribus command failed with exit code: {res}")
                    raise UserError('Scribus failed to generate PDF. Check template and scribus installation.')

                with open(outfiles[-1], 'rb') as pdf_file:
                    merger.append(PdfFileReader(pdf_file))

            # Generate final PDF
            outfile = tempfile.NamedTemporaryFile(mode='w+b', suffix='.pdf', delete=False)
            merger.write(outfile.name)
            outfile.seek(0)
            pdf = outfile.read()

            return (pdf, 'pdf')

        finally:
            # Cleanup temporary files
            for filename in outfiles:
                try:
                    if os.path.exists(filename):
                        os.unlink(filename)
                except Exception as e:
                    _logger.warning(f"Could not delete {filename}: {e}")

            for sla_file in sla_files:
                try:
                    if os.path.exists(sla_file):
                        os.unlink(sla_file)
                except Exception as e:
                    _logger.warning(f"Could not delete {sla_file}: {e}")

            try:
                if 'outfile' in locals() and os.path.exists(outfile.name):
                    outfile.close()
                    os.unlink(outfile.name)
            except Exception as e:
                _logger.warning(f"Could not delete output file: {e}")

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        report_id = self._get_report(report_ref)
        report_type = report_id.fake_report_type.lower().replace('-', '_')
        if report_type == "scribus_sla" or report_type == "scribus_pdf":
            return self.render_scribus(report_id, res_ids, data)
        else:
            return super(IrActionsReport, self)._render_qweb_pdf(report_ref, res_ids, data)