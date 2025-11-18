/** @odoo-module **/

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";
import { user } from "@web/core/user";

registry.category("ir.actions.report handlers").add("qweb_scribus", async (action, options, env) => {
    if (action.report_type !== "qweb-scribus") {
        return false;
    }

    const type = "scribus";
    let url = `/report/${type}/${action.report_name}`;

    const actionContext = action.context || {};
    if (actionContext.active_ids) {
        url += `/${actionContext.active_ids.join(",")}`;
    }

    env.services.ui.block();
    try {
        const downloadContext = { ...user.context };  // ✅ Use user.context directly, not env.services.user
        if (action.context) {
            Object.assign(downloadContext, action.context);
        }

        await download({
            url: "/report/download",
            data: {
                data: JSON.stringify([url, action.report_type]),
                context: JSON.stringify(downloadContext),
            },
        });
    } finally {
        env.services.ui.unblock();
    }

    const { onClose } = options;
    if (action.close_on_report_download) {
        return env.services.action.doAction(
            { type: "ir.actions.act_window_close" },
            { onClose }
        );
    } else if (onClose) {
        onClose();
    }

    return true;
});