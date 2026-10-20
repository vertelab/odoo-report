/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Model } from "@web/model/model";
import { browser } from "@web/core/browser/browser";
import { formatDateTime, parseDate, parseDateTime } from "@web/core/l10n/dates";
import { KeepLast } from "@web/core/utils/concurrency";
import { useService } from "@web/core/utils/hooks";

export class MapModel extends Model {
    setup(params, { notification, http }) {
        this.notification = notification;
        this.orm = useService("orm");
        this.http = http;

        this.metaData = {
            ...params,
        };

        this.data = {
            count: 0,
            locatedRecordsCount: 0,
            isFetchingCoordinates: false,
            coordinateFetchRequired: true,
            groupByKey: false,
            isGrouped: false,
            partnerIds: [],
            partners: [],
            partnerToCache: [],
            recordGroups: [],
            records: [],
        };
        this.keepLast = new KeepLast();
    }

    async load(params) {
        const metaData = {
            ...this.metaData,
            ...params,
        };

        metaData.groupBy = (metaData.groupBy || []).filter((groupBy) => {
            const [fieldName] = groupBy.split(".");
            const field = metaData.fields[fieldName];
            return field?.type !== "properties";
        });
        this.data = await this._fetchData(metaData);
        this.metaData = metaData;

        this.notify();
    }

    async _fetchData(metaData) {
        const data = {
            count: 0,
            locatedRecordsCount: 0,
            isFetchingCoordinates: false,
            coordinateFetchRequired: true,
            groupByKey: metaData.groupBy.length ? metaData.groupBy[0] : false,
            isGrouped: metaData.groupBy.length > 0,
            partnerIds: [],
            partners: [],
            partnerToCache: [],
            recordGroups: [],
            records: [],
        };

        if (!metaData.resPartnerField) {
            return data;
        }

        try {
            const response = await this._fetchRecordData(metaData, data);
            
            if (response && response.records) {
                const datetimeTypeFields = metaData.fieldNames.filter(
                    (name) => metaData.fields[name].type === "datetime"
                );
                
                response.records.forEach(record => {
                    datetimeTypeFields.forEach(field => {
                        if (record[field]) {
                            const dateUTC = luxon.DateTime.fromFormat(record[field], "yyyy-MM-dd HH:mm:ss", { zone: "UTC" });
                            record[field] = formatDateTime(dateUTC, { format: "yyyy-MM-dd HH:mm:ss" });
                        }
                    });
                });

                data.records = response.records;
                data.count = response.length || 0;

                if (data.isGrouped) {
                    data.recordGroups = await this._getRecordGroups(metaData, data);
                }

                // Handle partner IDs
                if (metaData.resModel === "res.partner" && metaData.resPartnerField === "id") {
                    data.partnerIds = response.records.map(record => {
                        record.partner_id = [record.id];
                        return record.id;
                    });
                } else {
                    // Get partner IDs from the related field
                    const partnerIds = response.records
                        .map((record) => record[metaData.resPartnerField])
                        .filter((id) => id);
                    data.partnerIds = [...new Set(partnerIds.flat())];
                }

                // Fetch partner information
                if (data.partnerIds.length) {
                    const partners = await this.orm.read("res.partner", data.partnerIds, [
                        "id",
                        "name",
                        "display_name",
                        "partner_latitude",
                        "partner_longitude",
                        "complete_contact_address",
                        "commercial_company_name",
                        "parent_id",
                        "is_company",
                        "parent_name"
                    ]);
                    data.partners = partners;
                }

                this._addPartnerToRecord(metaData, data);
            }
        } catch (error) {
            console.error("Error in _fetchData:", error);
            this.notification.add(_t("Error fetching map data"), {
                type: "danger",
                sticky: false,
            });
        }

        return data;
    }

    _addPartnerToRecord(metaData, data) {
        for (const record of data.records) {
            for (const partner of data.partners) {
                let partnerRecordId;
                if (metaData.resModel === "res.partner" && metaData.resPartnerField === "id") {
                    partnerRecordId = record.id;
                } else {
                    partnerRecordId = record[metaData.resPartnerField]?.id;
                }
                if (partnerRecordId == partner.id) {
                    record.partner = partner;
                    data.locatedRecordsCount++;
                }
            }
        }
    }

    async _fetchRecordData(metaData, data) {
        const fieldNames = data.groupByKey 
            ? [...metaData.fieldNames, data.groupByKey.split(":")[0]] 
            : metaData.fieldNames;

        const specification = this._buildFieldSpecification(metaData, fieldNames);
        const orderBy = this._buildOrderByClause(metaData);

        const result = await this.orm.webSearchRead(metaData.resModel, metaData.domain, {
            specification,
            limit: metaData.limit,
            offset: metaData.offset,
            order: orderBy.join(" "),
            context: metaData.context,
        });

        return {
            records: result.records || [],
            length: result.length || 0
        };
    }

    _buildFieldSpecification(metaData, fieldNames) {
        const specification = {};
        for (const fieldName of fieldNames) {
            const field = metaData.fields[fieldName];
            specification[fieldName] = {};
            
            // For many2one fields, ensure we get both id and display_name
            if (field && field.type === "many2one") {
                specification[fieldName] = {
                    fields: {
                        id: {},
                        display_name: {},
                    }
                };
            }
            // For other relational fields
            else if (field && ["one2many", "many2many"].includes(field.type)) {
                specification[fieldName] = {
                    fields: { 
                        display_name: {} 
                    }
                };
            }
        }
        return specification;
    }

    _buildOrderByClause(metaData) {
        const orderBy = [];
        if (metaData.defaultOrder) {
            orderBy.push(metaData.defaultOrder.name);
            if (metaData.defaultOrder.asc) {
                orderBy.push("ASC");
            }
        }
        return orderBy;
    }

    async _fetchRecordsPartner(metaData, data, ids) {
        try {
            const domain = [
                ["complete_contact_address", "!=", "False"],
                ["id", "in", ids],
            ];
            const fields = ["complete_contact_address", "partner_latitude", "partner_longitude"];
            const records = await this.orm.searchRead("res.partner", domain, fields);
            return records || [];
        } catch (error) {
            console.error("Error in _fetchRecordsPartner:", error);
            return [];
        }
    }

    _retrievePartnerIds(metaData, data) {
        for (const record of data.records) {
            const partnerId = record[metaData.resPartnerField];
            if (partnerId && partnerId.id) {
                data.partnerIds.push(partnerId.id);
            }
        }
    }

    async _getRecordGroups(metaData, data) {
        const recordGroups = {};
        const [groupByFieldName] = data.groupByKey.split(":");
        const groupByField = metaData.fields[groupByFieldName];
        const fieldLabel = groupByField.string || groupByFieldName;

        for (const record of data.records) {
            const groupValue = record[groupByFieldName];
            let groupId;
            let groupName;

            if (!groupValue) {
                groupId = "undefined";
                groupName = _t("Undefined");
            } else if (typeof groupValue === 'object') {
                // Handle many2one object format {id: X, display_name: "Name"}
                groupId = groupValue.id;
                groupName = groupValue.display_name;
            } else {
                groupId = groupValue;
                groupName = String(groupValue);
            }

            if (!recordGroups[groupId]) {
                recordGroups[groupId] = {
                    name: fieldLabel + ": " + groupName,
                    records: [],
                };
            }
            recordGroups[groupId].records.push(record);
        }

        return recordGroups;
    }
}

MapModel.services = ["notification", "http"];
MapModel.COORDINATE_FETCH_TIMEOUT = 1000;