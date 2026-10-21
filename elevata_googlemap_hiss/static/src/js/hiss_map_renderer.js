/** @odoo-module **/

import { MapRenderer } from "@elevata_googlemap/googlemap_view/googlemap_renderer";

export class HissMapRenderer extends MapRenderer {
    _createElevatorInfoContent(markerData) {
        const records = markerData.records || [];
        const partner = markerData.partner;
        const address = partner ? partner.complete_contact_address || "" : "";
        const encodedAddress = encodeURIComponent(address);

        const recordsHtml = records
            .map((record) => {
                const elevatorNumber = record.elevator_number || "";
                const elevatorType = record.elevator_type_id
                    ? record.elevator_type_id.display_name ||
                      record.elevator_type_id.name ||
                      record.elevator_type_id[1]
                    : "";
                const mfgNumber = record.manufacturing_number || "";
                const brand = record.mechanical_brand_id
                    ? record.mechanical_brand_id.display_name ||
                      record.mechanical_brand_id.name ||
                      record.mechanical_brand_id[1]
                    : "";
                const lastInspection = record.last_inspection || "";
                const name = record.name || record.display_name || "";

                return `
                <div class="o_map_popup_record" style="padding: 10px; min-width: 300px; ${
                    records.length > 1
                        ? "border-bottom: 1px solid #dee2e6; margin-bottom: 10px;"
                        : ""
                }">
                    <div style="border-bottom: 2px solid #00529b; margin-bottom: 10px;">
                        <h3 style="color: #00529b; margin: 0 0 5px 0; font-size: 16px;">${name}</h3>
                    </div>
                    <div style="display: grid; grid-template-columns: auto 1fr; gap: 5px; margin-bottom: 10px;">
                        ${
                            elevatorNumber
                                ? `<div style="font-weight: bold; color: #666;">Elevator no:</div>
                                   <div><a href="#" class="elevator-link" data-record-id="${record.id}" style="color: #00529b; text-decoration: none;">${elevatorNumber}</a></div>`
                                : ""
                        }
                        ${elevatorType ? `<div style="font-weight: bold; color: #666;">Type:</div><div>${elevatorType}</div>` : ""}
                        ${brand ? `<div style="font-weight: bold; color: #666;">Brand:</div><div>${brand}</div>` : ""}
                        ${mfgNumber ? `<div style="font-weight: bold; color: #666;">Manufacturing no:</div><div>${mfgNumber}</div>` : ""}
                        ${lastInspection ? `<div style="font-weight: bold; color: #666;">Last inspection:</div><div>${lastInspection}</div>` : ""}
                    </div>
                </div>`;
            })
            .join("");

        return `
            <div class="o_map_popup_container" style="max-height: 600px; overflow-y: auto;">
                <div style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 15px;">
                    <div style="font-weight: bold; color: #666; margin-bottom: 8px;">Address</div>
                    ${
                        address
                            ? `<a href="https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}" target="_blank" style="color: #00529b; text-decoration: none;">${address}</a>`
                            : ""
                    }
                </div>
                ${
                    records.length > 1
                        ? `<div style="margin-bottom: 15px; padding: 0 15px;"><strong>${records.length} elevators at this address</strong></div>`
                        : ""
                }
                ${recordsHtml}
            </div>`;
    }

    async popupInfowindow(event, marker) {
        const markerData = marker.markerData;
        const infoContent = this._createElevatorInfoContent(markerData);

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
            document.querySelectorAll(".elevator-link").forEach((link) => {
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
