/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { MapArchParser } from "./googlemap_arch_parser";
import { MapModel } from "./googlemap_model";
import { MapController } from "./googlemap_controller";
import { MapRenderer } from "./googlemap_renderer";

export const mapView = {
    type: "googlemap",
    display_name: _t("Google Map"),
    icon: "fa fa-map-marker",
    multiRecord: true,
    ArchParser: MapArchParser,
    Controller: MapController,
    Model: MapModel,
    Renderer: MapRenderer,
    buttonTemplate: "elevata_googlemap.MapView.Buttons",
    props: (genericProps, view, config) => {
        let modelParams = genericProps.state;
        if (!modelParams) {
            const { arch,  resModel, fields, context} = genericProps;
            const parser = new view.ArchParser();
            const archInfo = parser.parse(arch);
            const views = config.views || [];
            modelParams = {
                context: context,
                hasFormView: views.some((view) => view[1] === "form"),
                fields: fields,
                resModel: resModel,
                defaultOrder: archInfo.defaultOrder,
                fieldNames: archInfo.fieldNames,
                fieldNamesInfowindow: archInfo.fieldNamesInfowindow,
                hideAddress: archInfo.hideAddress || false,
                hideName: archInfo.hideName || false,
                hideTitle: archInfo.hideTitle || false,
                hidePartnerList: archInfo.hidePartnerList || false,
                limit: archInfo.limit || 80,
                offset: 0,
                panelTitle: archInfo.panelTitle || config.getDisplayName() || _t("Items"),
                resPartnerField: archInfo.resPartnerField,
            };
        }

        return {
            ...genericProps,
            modelParams,
            Model: view.Model,
            Renderer: view.Renderer,
            buttonTemplate: view.buttonTemplate,
        };
    },
};

registry.category("views").add("googlemap", mapView);
