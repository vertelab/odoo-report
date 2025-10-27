odoo.define('web.ReportActionManagerGlabels', function (require) {
"use strict";
var core = require('web.core');
var framework = require('web.framework');
var session = require('web.session');
var ActionManager = require('web.ActionManager');
var _t = core._t;
var _lt = core._lt;

// Messages that might be shown to the user dependening on the state of wkhtmltopdf
var link = '<br><br><a href="http://wkhtmltopdf.org/" target="_blank">wkhtmltopdf.org</a>';
var WKHTMLTOPDF_MESSAGES = {
    broken: _lt('Your installation of Wkhtmltopdf seems to be broken. The report will be shown ' +
                'in html.') + link,
    install: _lt('Unable to find Wkhtmltopdf on this system. The report will be shown in ' +
                 'html.') + link,
    upgrade: _lt('You should upgrade your version of Wkhtmltopdf to at least 0.12.0 in order to ' +
                 'get a correct display of headers and footers as well as support for ' +
                 'table-breaking between pages.') + link,
    workers: _lt('You need to start Odoo with at least two workers to print a pdf version of ' +
                 'the reports.'),};

ActionManager.include({
    _executeReportAction: function (action, options) {
        var self = this;
        console.log("javascript running")
        console.log(action.report_type)
        if (action.report_type !== 'scribus_pdf' && action.report_type !== 'scribus_sla') {
            return this._super.apply(this, arguments);
        }
        return this.call('report', 'checkWkhtmltopdf').then(function (state) {
                // display a notification according to wkhtmltopdf's state
                if (state in WKHTMLTOPDF_MESSAGES) {
                    self.do_notify(_t('Report'), WKHTMLTOPDF_MESSAGES[state], true);
                }

                if (state === 'upgrade' || state === 'ok') {
                    // trigger the download of the PDF report
                    return self._triggerDownload(action, options, 'pdf');
                } else {
                    // open the report in the client action if generating the PDF is not possible
                    return self._executeReportClientAction(action, options);
                }
            });
    }
    })
})
