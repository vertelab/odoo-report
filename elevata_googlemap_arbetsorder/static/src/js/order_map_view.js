/** @odoo-module **/

import { registry } from "@web/core/registry";
import { mapView } from "@elevata_googlemap/googlemap_view/googlemap_view";
import { OrderMapController } from "./order_map_controller";
import { OrderMapModel } from "./order_map_model";
import { OrderMapRenderer } from "./order_map_renderer";

registry.category("views").add("order_map", {
    ...mapView,
    Controller: OrderMapController,
    Model: OrderMapModel,
    Renderer: OrderMapRenderer,
});
