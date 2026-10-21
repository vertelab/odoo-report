/** @odoo-module **/

import { MapRenderer } from "@elevata_googlemap/googlemap_view/googlemap_renderer";

export class OrderMapRenderer extends MapRenderer {
    _createOrderInfoContent(markerData) {
        const records = markerData.records || [];
        const partner = markerData.partner;
        const address = partner ? partner.complete_contact_address || "" : "";
        const encodedAddress = encodeURIComponent(address);

        const recordsHtml = records
            .map((record) => {
                const name = record.name || record.display_name || "";
                const equipment = record.equipment_id
                    ? record.equipment_id.display_name ||
                      record.equipment_id.name ||
                      record.equipment_id[1]
                    : "";
                const reporter = record.reporter
                    ? record.reporter.display_name ||
                      record.reporter.name ||
                      record.reporter[1]
                    : "";
                const phone = record.reporter_phone || "";
                const stage = record.stage_id
                    ? record.stage_id.display_name ||
                      record.stage_id.name ||
                      record.stage_id[1]
                    : "";
                const planned = record.planned_start_datetime || "";
                const description = record.description || "";

                return `
                <div class="o_map_popup_record" style="padding: 10px; min-width: 300px; ${
                    records.length > 1
                        ? "border-bottom: 1px solid #dee2e6; margin-bottom: 10px;"
                        : ""
                }">
                    <div style="border-bottom: 2px solid #00529b; margin-bottom: 10px;">
                        <h3 style="color: #00529b; margin: 0 0 5px 0; font-size: 16px;">
                            <a href="#" class="order-link" data-record-id="${record.id}" style="color: #00529b; text-decoration: none;">${name}</a>
                        </h3>
                    </div>
                    <div style="display: grid; grid-template-columns: auto 1fr; gap: 5px; margin-bottom: 10px;">
                        ${equipment ? `<div style="font-weight: bold; color: #666;">Lift:</div><div>${equipment}</div>` : ""}
                        ${reporter ? `<div style="font-weight: bold; color: #666;">Reporter:</div><div>${reporter}</div>` : ""}
                        ${phone ? `<div style="font-weight: bold; color: #666;">Phone:</div><div>${phone}</div>` : ""}
                        ${stage ? `<div style="font-weight: bold; color: #666;">Stage:</div><div>${stage}</div>` : ""}
                        ${planned ? `<div style="font-weight: bold; color: #666;">Planned start:</div><div>${planned}</div>` : ""}
                    </div>
                    ${description ? `<div style="color: #333; font-size: 13px;">${description}</div>` : ""}
                </div>`;
            })
            .join("");

        return `
            <div class="o_map_popup_container" style="max-height: 600px; overflow-y: auto;">
                ${address ? `<div style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 15px;">
                    <div style="font-weight: bold; color: #666; margin-bottom: 8px;">Address</div>
                    <a href="https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}" target="_blank" style="color: #00529b; text-decoration: none;">${address}</a>
                </div>` : ""}
                ${records.length > 1 ? `<div style="margin-bottom: 15px; padding: 0 15px;"><strong>${records.length} orders at this address</strong></div>` : ""}
                ${recordsHtml}
            </div>`;
    }

    async popupInfowindow(event, marker) {
        const markerData = marker.markerData;
        const infoContent = this._createOrderInfoContent(markerData);

        if (this.infowindow) {
            this.infowindow.close();
        }

        this.infowindow = new google.maps.InfoWindow({
            content: infoContent,
            maxWidth: 400,
            pixelOffset: new google.maps.Size(-10, -25),
        });

        this.infowindow.setPosition(marker.getPosition());
        this.infowindow.open(this.state.googlemap);

        google.maps.event.addListener(this.infowindow, "domready", () => {
            document.querySelectorAll(".order-link").forEach((link) => {
                link.addEventListener("click", (ev) => {
                    ev.preventDefault();
                    const recordId = parseInt(ev.currentTarget.dataset.recordId, 10);
                    if (recordId) {
                        this.props.onMarkerClick([recordId]);
                    }
                });
            });
        });
    }
}
