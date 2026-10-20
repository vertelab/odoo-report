/** @odoo-module **/

import { unique } from "@web/core/utils/arrays";
import { visitXML } from "@web/core/utils/xml";

// Odoo 18 dropped archParseBoolean from @web/views/utils.
const archParseBoolean = (value) => value === "1" || value === "true";

// need to check below options
// res_partner
// default_order
// hide_name
// hide_address
// panel_title
// hide_title
// limit

export class MapArchParser {
    parse(arch) {
        const archInfo = {
            fieldNames: [],
            fieldNamesInfowindow: [],
        };

        visitXML(arch, (node) => {
            switch (node.tagName) {
                case "googlemap":
                    this.visitMap(node, archInfo);
                    break;
                case "field":
                    this.visitField(node, archInfo);
                    break;
            }
        });

        archInfo.fieldNames = unique(archInfo.fieldNames);
        archInfo.fieldNamesInfowindow = unique(archInfo.fieldNamesInfowindow);
        return archInfo;
    }

    visitMap(node, archInfo) {
        archInfo.resPartnerField = node.getAttribute("res_partner");
        archInfo.fieldNames.push(archInfo.resPartnerField);

        if (node.hasAttribute("hide_title")) {
            archInfo.hideTitle = archParseBoolean(node.getAttribute("hide_title"));
        }
        if (node.hasAttribute("hide_address")) {
            archInfo.hideAddress = archParseBoolean(node.getAttribute("hide_address"));
        }
        if (node.hasAttribute("hide_name")) {
            archInfo.hideName = archParseBoolean(node.getAttribute("hide_name"));
        }
        if (!archInfo.hideName) {
            archInfo.fieldNames.push("display_name");
        }
        
        if (node.hasAttribute("limit")) {
            archInfo.limit = parseInt(node.getAttribute("limit"), 10);
        }
        if (node.hasAttribute("panel_title")) {
            archInfo.panelTitle = node.getAttribute("panel_title");
        }
        if (node.hasAttribute("hide_partner_list")) {
            archInfo.hidePartnerList = archParseBoolean(node.getAttribute("hide_partner_list"));
        }
        if (node.hasAttribute("default_order")) {
            archInfo.defaultOrder = {
                name: node.getAttribute("default_order"),
                asc: true,
            };
        }
    }
    visitField(node, params) {
        params.fieldNames.push(node.getAttribute("name"));
        params.fieldNamesInfowindow.push({
            fieldName: node.getAttribute("name"),
            string: node.getAttribute("string"),
        });
    }
}
