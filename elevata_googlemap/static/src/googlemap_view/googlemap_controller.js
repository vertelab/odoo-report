/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useModelWithSampleData } from "@web/model/model";
import { standardViewProps } from "@web/views/standard_view_props";
import { Layout } from "@web/search/layout";
import { usePager } from "@web/search/pager_hook";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { useSearchBarToggler } from "@web/search/search_bar/search_bar_toggler";
import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { useSetupAction } from "@web/search/action_hook";
import { loadJS, loadCSS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillUnmount, onWillStart, useRef } from "@odoo/owl";

export class MapController extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.notificationService = useService('notification');
        
        const Model = this.props.Model;
        const model = useModelWithSampleData(Model, this.props.modelParams);
        this.model = model;

        onWillStart(async () => {
            const key = await this._getGmapAPIKey();
            if (key) {
                try {
                    // Create the script loader
                    const loader = new Promise((resolve, reject) => {
                        const script = document.createElement('script');
                        script.async = true;
                        script.src = `https://maps.googleapis.com/maps/api/js?key=${key}&libraries=maps,places,geometry,marker&callback=initMap&loading=async`;
                        
                        // Define the callback function
                        window.initMap = () => {
                            resolve(window.google);
                        };
                        
                        script.onerror = () => reject(new Error('Failed to load Google Maps API'));
                        document.head.appendChild(script);
                    });
                    
                    // Wait for the API to load
                    await loader;
                    return true;
                } catch (e) {
                    return false;
                }
            } else {
                this.notificationService.add(_t("Please verify your Google Maps API key or check your internet connection.."), { type: "danger" });
                return false;
            }
        });

        onWillUnmount(() => {
            if (window.initMap) {
                delete window.initMap;
            }
        });

        useSetupAction({
            rootRef: useRef("root"),
            getLocalState: () => {
                return { metaData: this.model.metaData };
            },
        });

        usePager(() => {
            return {
                offset: this.model.metaData.offset,
                limit: this.model.metaData.limit,
                total: this.model.data.count,
                onUpdate: ({ offset, limit }) => this.model.load({ offset, limit }),
            };
        });
        this.searchBarToggler = useSearchBarToggler();
    }

    async _getGmapAPIKey() {
        if (!this._gmp_api_key_prom) {
            this._gmp_api_key_prom = new Promise(async resolve => {
                const data = await this.rpc('/elevata_googlemap/_get_googlemap_api_key');
                resolve(JSON.parse(data).googlemap_api_key || '');
            });
        }
        return this._gmp_api_key_prom;
    }

    get rendererProps() {
        return {
            model: this.model,
            onMarkerClick: this.openRecordsView.bind(this),
        };
    }

    openRecordsView(ids) {
        if (ids.length > 1) {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: this.env.config.getDisplayName() || _t("Untitled"),
                views: [
                    [false, "form"],
                    [false, "list"],
                ],
                res_model: this.props.resModel,
                domain: [["id", "in", ids]],
            });
        } else {
            this.action.switchView("form", { resId: ids[0] });
        }
    }
}

MapController.template = "elevata_googlemap.MapView";

MapController.components = {
    Layout,
    SearchBar,
    CogMenu,
};

MapController.props = {
    ...standardViewProps,
    Model: Function,
    modelParams: Object,
    Renderer: Function,
    buttonTemplate: String,
};
