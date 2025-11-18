from odoo.exceptions import UserError
from odoo import models, fields, api
import unicodecsv as csv
import os
import tempfile
import base64
import logging

_logger = logging.getLogger(__name__)


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
        help="One if you want to fill the sheet with new records, the count of labels of the sheet to fill each sheet with one record")
    col_name = fields.Char(string="Column", help="(Glabels rows) the name of name column for use in gLabels")
    col_value = fields.Char(string="Column", help="(Glabels rows) the name of value column for use in gLabels")
    csv_fields = fields.Text(compute="_get_csv_fields")

    def render_glabels(self, report_id, res_ids, data):
        """Render glabels - report_id is already a record"""
        if report_id.glabels_template:
            template = base64.b64decode(report_id.glabels_template)
            temp = tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv')
            outfile = tempfile.NamedTemporaryFile(mode='w+b', suffix='.pdf')
            glabels = tempfile.NamedTemporaryFile(mode='w+b', suffix='.glabels')
            glabels.write(template)
            glabels.seek(0)
            labelwriter = None

            for p in self.env[report_id.model].browse(res_ids).read():
                if not labelwriter:
                    labelwriter = csv.DictWriter(temp, p.keys())
                    labelwriter.writeheader()

                for c in range(report_id.label_count):
                    labelwriter.writerow({k: isinstance(v, str) and v or str(v) for k, v in p.items()})

            temp.seek(0)
            res = os.system("glabels-3-batch -o %s -l -C -i %s %s" % (outfile.name, temp.name, glabels.name))
            outfile.seek(0)
            pdf = outfile.read()
            outfile.close()
            temp.close()
            glabels.close()
            return (pdf, 'pdf')
        else:
            raise UserError("No glabel template has been selected.")

    @api.model
    def _render_qweb_glabels(self, report_ref, res_ids=None, data=None):
        """This is called by the controller"""
        if not data:
            data = {}
        data.setdefault('report_type', 'glabels')

        report_id = self._get_report(report_ref)
        return self.render_glabels(report_id, res_ids, data)