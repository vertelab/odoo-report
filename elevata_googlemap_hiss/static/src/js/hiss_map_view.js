/** @odoo-module **/

import { registry } from "@web/core/registry";
import { mapView } from "@elevata_googlemap/googlemap_view/googlemap_view";
import { HissMapController } from "./hiss_map_controller";
import { HissMapModel } from "./hiss_map_model";
import { HissMapRenderer } from "./hiss_map_renderer";

registry.category("views").add("hiss_map", {
    ...mapView,
    Controller: HissMapController,
    Model: HissMapModel,
    Renderer: HissMapRenderer,
});
