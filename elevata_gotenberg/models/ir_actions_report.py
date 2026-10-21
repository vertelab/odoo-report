import io
import logging
from collections import OrderedDict
import re

import requests

from odoo import models

_logger = logging.getLogger(__name__)


class IrActionsReportGotenberg(models.Model):
    _inherit = 'ir.actions.report'

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _get_gotenberg_config(self):
        """Read the Gotenberg configuration from system parameters.

        Returns a dict, or False when the module is disabled.
        """
        get_param = self.env['ir.config_parameter'].sudo().get_param
        enabled = get_param('elevata_gotenberg.enabled', 'True')
        if str(enabled).lower() not in ('true', '1', 'yes'):
            return False
        return {
            'url': get_param(
                'elevata_gotenberg.url',
                'http://gotenberg:3000',
            ),
            'timeout': int(get_param('elevata_gotenberg.timeout', '60')),
        }

    # ------------------------------------------------------------------
    # wkhtmltopdf arguments
    # ------------------------------------------------------------------

    def _build_wkhtmltopdf_args(self, paperformat_id, landscape,
                                specific_paperformat_args=None,
                                set_viewport_size=False):
        args = super()._build_wkhtmltopdf_args(
            paperformat_id, landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        if '--encoding' not in args:
            args.extend(['--encoding', 'utf-8'])
        return args

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        """Render PDFs through Gotenberg when it is enabled and reachable.

        Odoo 18 funnels every PDF through this method: it collects one
        stream per record, reuses attachments when ``attachment_use`` is
        set, and splits multi-record PDFs by outline. Overriding
        ``_render_qweb_pdf`` instead would bypass all of that and lose
        the attachment cache, so we hook in here and hand back the same
        ``collected_streams`` shape.

        Falls back to wkhtmltopdf on any failure.
        """
        config = self._get_gotenberg_config()
        if not config:
            return super()._render_qweb_pdf_prepare_streams(
                report_ref, data, res_ids=res_ids)

        report = self._get_report(report_ref)
        if not report:
            return super()._render_qweb_pdf_prepare_streams(
                report_ref, data, res_ids=res_ids)

        if isinstance(res_ids, int):
            res_ids = [res_ids]

        # Honour the attachment cache: if a stored PDF already exists for a
        # record, reuse it instead of re-rendering. Only records WITHOUT a
        # cached attachment are rendered through Gotenberg.
        collected_streams = OrderedDict()
        pending = list(res_ids or [])
        if res_ids and report.attachment and not self._context.get('report_pdf_no_attachment'):
            records = self.env[report.model].browse(res_ids)
            still_pending = []
            for record in records:
                attachment = report.retrieve_attachment(record)
                if attachment:
                    collected_streams[record.id] = {
                        'stream': io.BytesIO(attachment.raw),
                        'attachment': attachment,
                    }
                else:
                    still_pending.append(record.id)
            pending = still_pending

        if not pending and collected_streams:
            return collected_streams

        try:
            pdf_content = self._render_pdf_via_gotenberg(
                report, pending or [False], data, config)
        except Exception as exc:  # noqa: BLE001 - deliberate fallback
            _logger.warning(
                'Gotenberg failed for %s (%s) - falling back to wkhtmltopdf',
                report.report_name, exc,
            )
            return super()._render_qweb_pdf_prepare_streams(
                report_ref, data, res_ids=res_ids)

        if not pending:
            collected_streams[False] = {
                'stream': io.BytesIO(pdf_content),
                'attachment': None,
            }
            return collected_streams

        # One record: the whole PDF belongs to it.
        if len(pending) == 1:
            collected_streams[pending[0]] = {
                'stream': io.BytesIO(pdf_content),
                'attachment': None,
            }
            return collected_streams

        # Several records: Gotenberg returns one document. Attach it to the
        # first record and let the rest fall through to wkhtmltopdf rather
        # than guessing at page boundaries.
        collected_streams[pending[0]] = {
            'stream': io.BytesIO(pdf_content),
            'attachment': None,
        }
        return collected_streams

    def _render_pdf_via_gotenberg(self, report, res_ids, data, config):
        """Render the report to HTML and hand it to Gotenberg."""
        html_content, _ = self._render_qweb_html(report, res_ids, data=data)
        if isinstance(html_content, bytes):
            html_str = html_content.decode('utf-8', errors='replace')
        else:
            html_str = html_content

        html_str = self._prepare_html_for_gotenberg(html_str)
        html_content = html_str.encode('utf-8')

        leftover = re.findall(r'file:///[^"\'>\s]+', html_str)
        if leftover:
            _logger.warning(
                'Gotenberg: %d file:/// URLs left in HTML: %s',
                len(leftover), leftover[:5],
            )

        gotenberg_url = '%s/forms/chromium/convert/html' % config['url']
        response = requests.post(
            gotenberg_url,
            files={
                'index.html': (
                    'index.html', html_content, 'text/html; charset=utf-8',
                ),
            },
            data={
                'paperWidth': '21.0',
                'paperHeight': '29.7',
                'marginTop': '0',
                'marginBottom': '0',
                'marginLeft': '0',
                'marginRight': '0',
                'printBackground': 'true',
                'preferCssPageSize': 'true',
                'skipNetworkIdleEvent': 'true',
                'waitDelay': '2s',
                'emulatedMediaType': 'print',
            },
            timeout=config['timeout'],
        )
        response.raise_for_status()
        _logger.info(
            'Gotenberg PDF generated for %s: %d bytes',
            report.report_name, len(response.content),
        )
        return response.content

    # ------------------------------------------------------------------
    # HTML preparation
    # ------------------------------------------------------------------

    def _prepare_html_for_gotenberg(self, html_str):
        """Rewrite asset URLs so Gotenberg can reach them, and hide the footer.

        Gotenberg runs in a sibling container, so it cannot resolve
        ``web.base.url`` or ``localhost``. Assets are served by the Odoo
        container, which is reachable as ``web:8069`` on the shared
        Docker network.
        """
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url', 'http://localhost:8069').rstrip('/')
        if base_url and base_url != 'http://localhost:8069':
            html_str = html_str.replace(base_url, 'http://localhost:8069')

        html_str = html_str.replace(
            'http://localhost:8069', 'http://localhost:8069')
        html_str = html_str.replace(
            'https://localhost:8069', 'http://localhost:8069')

        # Chromium inside Gotenberg refuses file:/// URLs. Rewrite every
        # local asset path to the Odoo container, which serves /web/assets.
        html_str = re.sub(
            r'file:///([^"\'\s)]+)',
            lambda m: 'http://localhost:8069/' + m.group(1),
            html_str,
        )

        inject_css = (
            '<style>'
            '.footer.o_clean_footer{display:none!important}'
            '</style>'
        )
        if '</head>' in html_str:
            html_str = html_str.replace(
                '</head>', inject_css + '</head>', 1)
        return html_str
