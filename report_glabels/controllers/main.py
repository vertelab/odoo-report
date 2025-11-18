from odoo import http
from odoo.http import request, content_disposition
from odoo.addons.web.controllers.report import ReportController
from odoo.tools.safe_eval import safe_eval, time
import json


class ReportControllerExtended(ReportController):

    @http.route([
        '/report/<converter>/<reportname>',
        '/report/<converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True, readonly=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'glabels':
            report = request.env['ir.actions.report']
            context = dict(request.env.context)

            if docids:
                docids = [int(i) for i in docids.split(',') if i.isdigit()]

            if data.get('context'):
                context.update(json.loads(data['context']))

            content, ext = report.with_context(context)._render_qweb_glabels(reportname, docids, data=data)

            return request.make_response(content, headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(content))
            ])

        return super().report_routes(reportname, docids=docids, converter=converter, **data)

    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, context=None, token=None, readonly=True):
        requestcontent = json.loads(data)
        url, type_ = requestcontent[0], requestcontent[1]

        if type_ == 'qweb-glabels':
            reportname = url.split('/report/glabels/')[1].split('?')[0]
            docids = None

            if '/' in reportname:
                reportname, docids = reportname.split('/', 1)

            report = request.env['ir.actions.report']._get_report_from_name(reportname)

            if docids:
                ids = [int(x) for x in docids.split(",") if x.isdigit()]
                content, ext = report.render_glabels(report, ids, {})

                if isinstance(content, str):
                    content = content.encode('utf-8')

                obj = request.env[report.model].browse(ids)
                filename = f"{report.name}.{ext}"

                if report.print_report_name and len(obj) == 1:
                    filename = f"{safe_eval(report.print_report_name, {'object': obj, 'time': time})}.{ext}"

                return request.make_response(content, headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', content_disposition(filename))
                ])

        return super().report_download(data, context=context, token=token, readonly=readonly)