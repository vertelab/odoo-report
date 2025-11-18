from odoo import http
from odoo.http import request, content_disposition
from odoo.addons.web.controllers.report import ReportController
from odoo.tools.safe_eval import safe_eval, time
import json
import logging

_logger = logging.getLogger(__name__)


class ReportControllerExtended(ReportController):

    @http.route([
        '/report/<converter>/<reportname>',
        '/report/<converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True, readonly=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'scribus':
            report = request.env['ir.actions.report']
            context = dict(request.env.context)

            if docids:
                docids = [int(i) for i in docids.split(',') if i.isdigit()]

            if data.get('context'):
                context.update(json.loads(data['context']))

            content, ext = report.with_context(context)._render_qweb_scribus(reportname, docids, data=data)

            content_type = 'application/x-scribus' if ext == 'sla' else 'application/pdf'
            return request.make_response(content, headers=[
                ('Content-Type', content_type),
                ('Content-Length', len(content))
            ])

        return super().report_routes(reportname, docids=docids, converter=converter, **data)

    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, context=None, token=None, readonly=True):
        requestcontent = json.loads(data)
        url, type_ = requestcontent[0], requestcontent[1]

        if type_ == 'qweb-scribus':
            reportname = url.split('/report/scribus/')[1].split('?')[0]
            docids = None

            if '/' in reportname:
                reportname, docids = reportname.split('/', 1)

            report = request.env['ir.actions.report']._get_report_from_name(reportname)

            if docids:
                ids = [int(x) for x in docids.split(",") if x.isdigit()]
                content, ext = report.render_scribus(report, ids, {})

                if isinstance(content, str):
                    content = content.encode('utf-8')

                obj = request.env[report.model].browse(ids)
                filename = f"{report.name}.{ext}"

                if report.print_report_name and len(obj) == 1:
                    filename = f"{safe_eval(report.print_report_name, {'object': obj, 'time': time})}.{ext}"

                content_type = 'application/x-scribus' if ext == 'sla' else 'application/pdf'

                response = request.make_response(content, headers=[
                    ('Content-Type', content_type),
                    ('Content-Disposition', content_disposition(filename))
                ])
                return response

        return super().report_download(data, context=context, token=token, readonly=readonly)