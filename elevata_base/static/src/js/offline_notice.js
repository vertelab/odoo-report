/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";

const offlineNoticeService = {
    start(env) {
        let notificationId = null;

        function showOffline() {
            if (notificationId) return;
            notificationId = env.services.notification.add(
                "Ingen nätverksanslutning. Dina ändringar kanske inte sparas.",
                { type: "danger", sticky: true, title: "Offline" }
            );
        }

        function hideOffline() {
            if (notificationId) {
                env.services.notification.remove(notificationId);
                notificationId = null;
                env.services.notification.add(
                    "Anslutningen är återställd.",
                    { type: "success", title: "Online" }
                );
            }
        }

        browser.addEventListener("offline", showOffline);
        browser.addEventListener("online", hideOffline);

        if (!browser.navigator.onLine) {
            showOffline();
        }
    },
};

registry.category("services").add("elevata_offline_notice", offlineNoticeService);
