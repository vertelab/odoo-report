/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { renderToString } from "@web/core/utils/render";
import { renderToElement } from "@web/core/utils/render";
import { useService } from "@web/core/utils/hooks";
import { debounce } from "@web/core/utils/timing";
import { Component, onWillUnmount, onWillUpdateProps, useEffect, useRef, useState } from "@odoo/owl";

export class MapRenderer extends Component {
    setup() {
        this.orm = useService("orm");
        this.markers = [];
        this.mapContainerRef = useRef("mapContainer");
        this.state = useState({
            googlemap: null,
            closedGroupIds: [],
            expendedPartnerList: false,
        });
        this.nextId = 1;
        this.infowindow = null;

        useEffect(
            () => {
                if (typeof google === 'object' && typeof google.maps === 'object') {
                    this.state.googlemap = new google.maps.Map(this.mapContainerRef.el, {
                        center: { lat: 57.7089, lng: 11.9746 },
                        mapTypeId: google.maps.MapTypeId.ROADMAP,                
                        fullscreenControl: true,
                        mapTypeControl: true,
                        gestureHandling: 'greedy',
                        mapTypeControlOptions: {
                            mapTypeIds: ['satellite', 'hybrid', 'terrain'],
                            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
                        },
                        zoom: 12,
                        minZoom: 3,
                        maxZoom: 20,
                        disableDefaultUI: true, // Disable all default UI
                        zoomControl: true, // Explicitly enable zoom control
                        fullscreenControl: true, // Keep fullscreen control
                        mapTypeControl: true, // Keep map type control
                    });

                    if(this.state.googlemap){
                        this.addMarkers();
                        this.mapFitbounds();
                    }
                }
            },
            () => []
        );

        useEffect(
            () => {
                if (this.state.googlemap) {
                    this.removeMarkers();
                    this.addMarkers();
                    this.mapFitbounds();
                }
            },
            () => [this.props.model.data]
        );

        onWillUpdateProps(this.onWillUpdateProps);
        onWillUnmount(this.onWillUnmount);
    }

    mapFitbounds(){
        if (this.props.model.data.records.length > 0) {
            const initialCoords = this.getLatLng();
            if (initialCoords && initialCoords.length > 0) {
                var bounds = new google.maps.LatLngBounds();
                for (var i = 0, initialCoord; initialCoord = initialCoords[i]; i++) {
                    bounds.extend(initialCoord);
                }
                this.state.googlemap.fitBounds(bounds);

                // If only one location, zoom out a bit
                if (initialCoords.length === 1) {
                    this.state.googlemap.setZoom(12);
                }
            }
        }
    }

    async onWillUpdateProps(nextProps) {
        if (this.props.model.data.groupByKey !== nextProps.model.data.groupByKey) {
            this.state.closedGroupIds = [];
        }
    }

    onWillUnmount() {
        this.removeMarkers();
    }

    addMarkers() {
        var self = this;
        this.removeMarkers();

        const markersData = {};
        let records = this.props.model.data.records;
        
        // Clear all existing markers first
        this.markers.forEach(marker => {
            marker.setMap(null);
        });
        this.markers = [];

        if (this.props.model.data.isGrouped) {
            records = Object.entries(this.props.model.data.recordGroups)
                .filter(([key]) => !this.state.closedGroupIds.includes(key))
                .flatMap(([groupId, value]) => value.records.map((elem) => ({ ...elem, groupId })));
        }

        // Group records by coordinates
        for (const record of records) {
            const partner = record.partner;
            if (partner && partner.partner_latitude && partner.partner_longitude) {
                const coordKey = `${partner.partner_latitude},${partner.partner_longitude}`;
                if (!(coordKey in markersData)) {
                    markersData[coordKey] = {
                        records: [record],
                        ids: [record.id],
                        partner: partner,
                    };
                } else {
                    markersData[coordKey].records.push(record);
                    markersData[coordKey].ids.push(record.id);
                }
            }
        }

        // Create markers for each unique location
        for (const [coordKey, markerData] of Object.entries(markersData)) {
            const [lat, lng] = coordKey.split(',').map(Number);
            var latLng = new google.maps.LatLng(lat, lng);
            
            // Add label for multiple contacts
            const label = markerData.records.length > 1 ? {
                text: markerData.records.length.toString(),
                color: '#00529b',  // Elevata blue
                fontSize: '12px',
                fontWeight: 'bold'
            } : null;

            var marker = new google.maps.Marker({
                map: self.state.googlemap,
                position: latLng,
                draggable: false,  // Set to false to prevent dragging
                label: label
            });
            
            marker.markerData = markerData;

            google.maps.event.addListener(marker, 'click', function(event) {
                if (self.infowindow) {
                    self.infowindow.close();
                }
                self.popupInfowindow(event, this);
            });
            this.markers.push(marker);
        }
    }

    removeMarkers() {
        // Properly remove all markers from the map
        if (this.markers) {
            this.markers.forEach(marker => {
                marker.setMap(null);
                google.maps.event.clearInstanceListeners(marker);
            });
        }
        this.markers = [];
    }

    async popupInfowindow(event, data) {
        var self = this;
        var lat = data.getPosition().lat();
        var lng = data.getPosition().lng();
        if (!lat || !lng) {
            return;
        }

        if (self.infowindow) {
            self.infowindow.close();
        }

        self.infowindow = new google.maps.InfoWindow({
            maxWidth: 350,
            pixelOffset: new google.maps.Size(-10,-25)
        });

        const infoFields = [];
        const records = data.markerData.records;

        // First add names (if they are persons)
        records.forEach((record) => {
            const partner = record.partner;
            if (partner.is_company === false) {
                infoFields.push({
                    id: this.nextId++,
                    value: partner.name || partner.display_name,
                    string: _t("Name"),
                    recordId: record.id
                });
            }
        });

        // Then add companies
        records.forEach((record) => {
            const partner = record.partner;
            if (partner.is_company === true || partner.commercial_company_name || partner.parent_name) {
                const companyName = partner.commercial_company_name || partner.parent_name || (partner.is_company ? partner.name : null);
                if (companyName && !infoFields.some(f => f.value === companyName)) {
                    infoFields.push({
                        id: this.nextId++,
                        value: companyName,
                        string: _t("Company"),
                        recordId: record.id
                    });
                }
            }
        });

        // Finally add address
        infoFields.push({
            id: this.nextId++,
            value: data.markerData.partner.complete_contact_address,
            string: _t("Address"),
        });

        const partner = data.markerData.partner;
        const encodedAddress = encodeURIComponent(partner.complete_contact_address);
        const content = renderToString("elevata_googlemap.markerPopup", {
            fields: infoFields,
            hasFormView: self.props.model.metaData.hasFormView,
            url: `https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}`,
            isMultiContact: data.markerData.records.length > 1
        });

        self.infowindow.setContent(content);
        self.infowindow.open(self.state.googlemap);
        self.infowindow.setPosition(new google.maps.LatLng(lat,lng));

        google.maps.event.addListener(self.infowindow, 'domready', function() {
            // Add click handlers for contact links
            document.querySelectorAll('.contact-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const recordId = parseInt(e.currentTarget.dataset.recordId);
                    if (recordId) {
                        self.props.onMarkerClick([recordId]);
                    }
                });
            });
        });
    }

    centerAndOpenPartner(event, record) {
        const partner = record.partner;
        if (partner && partner.partner_latitude && partner.partner_longitude) {
            const position = {
                lat: parseFloat(partner.partner_latitude),
                lng: parseFloat(partner.partner_longitude)
            };
            
            this.state.googlemap.setCenter(position);
            this.state.googlemap.setZoom(15);

            // Find the marker for this partner using coordinates
            const coordKey = `${partner.partner_latitude},${partner.partner_longitude}`;
            const marker = this.markers.find(m => {
                const markerLat = m.getPosition().lat();
                const markerLng = m.getPosition().lng();
                return Math.abs(markerLat - position.lat) < 0.0000001 && 
                       Math.abs(markerLng - position.lng) < 0.0000001;
            });
            
            if (marker) {
                this.popupInfowindow(null, marker);
            }
        }
    }

    getInfowindowFields(markerData) {
        const infoFields = [];
        const metaData = this.props.model.metaData;
        
        // Show how many contacts are at this location
        if (markerData.records.length > 1) {
            infoFields.push({
                id: this.nextId++,
                value: `${markerData.records.length} contacts at this location`,
                string: _t("Contacts"),
            });
        }

        // Add each contact's information
        markerData.records.forEach((record, index) => {
            const partner = record.partner;
            
            // Add separator if not first contact
            if (index > 0) {
                infoFields.push({
                    id: this.nextId++,
                    value: "───────────────",
                    string: "",
                });
            }

            // Add name if available
            if (partner && partner.name) {
                infoFields.push({
                    id: this.nextId++,
                    value: partner.name,
                    string: index === 0 ? _t("Name") : "",
                });
            }
            
            // Add company information if available
            if (partner && (partner.commercial_company_name || (partner.parent_id && partner.parent_id[1]))) {
                infoFields.push({
                    id: this.nextId++,
                    value: partner.commercial_company_name || partner.parent_id[1],
                    string: index === 0 ? _t("Company") : "",
                });
            }
        });

        // Add address (only once since it's the same for all contacts at this location)
        if (!metaData.hideAddress && markerData.partner.complete_contact_address) {
            infoFields.push({
                id: this.nextId++,
                value: markerData.partner.complete_contact_address,
                string: _t("Address"),
            });
        }

        return infoFields;
    }

    createInfowindow(markerData){
        var self = this;
        return function (e) {
            if (self.infowindow ) {
                self.infowindow .close();
            }
            self.infowindow = new google.maps.InfoWindow({
                maxWidth: 350,
                pixelOffset: new google.maps.Size(-10,-25)
            });
            const infoFields = self.getInfowindowFields(markerData);
            const partner = markerData.record.partner;
            const encodedAddress = encodeURIComponent(partner.complete_contact_address);
            const content = renderToString("elevata_googlemap.markerPopup", {
                fields: infoFields,
                hasFormView: self.props.model.metaData.hasFormView,
                url: `https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}`,
            });

            self.infowindow.setContent(content);
            self.infowindow.open(self.state.googlemap);
            self.infowindow.setPosition(new google.maps.LatLng(markerData.record.partner.partner_latitude, markerData.record.partner.partner_longitude));

            google.maps.event.addListener(self.infowindow, 'domready', function() {
                document.querySelector("button.o-googlemap-renderer--popup-buttons-open").addEventListener("click", () => {
                    self.props.onMarkerClick(markerData.ids);
                });                   
            });
        }
    }

    getLatLng() {
        const LatLng = [];
        for (const record of this.props.model.data.records) {
            const partner = record.partner;
            if (partner && partner.partner_latitude && partner.partner_longitude) {
                LatLng.push(new google.maps.LatLng(partner.partner_latitude, partner.partner_longitude));
            }
        }
        if (!LatLng.length) {
            return false;
        }
        return LatLng;
    }

    toggleGroup(id) {
        if (this.state.closedGroupIds.includes(id)) {
            const index = this.state.closedGroupIds.indexOf(id);
            this.state.closedGroupIds.splice(index, 1);
        } else {
            this.state.closedGroupIds.push(id);
        }
    }

    togglePartnerList() {
        this.state.expendedPartnerList = !this.state.expendedPartnerList;
    }

    get expendedPartnerList() {
        return this.env.isSmall ? this.state.expendedPartnerList : false;
    }

    get canDisplayPartnerList() {
        return !this.env.isSmall || this.expendedPartnerList;
    }
}

MapRenderer.template = "elevata_googlemap.MapRenderer";
MapRenderer.props = {
    model: Object,
    onMarkerClick: Function,
};
