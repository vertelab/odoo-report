/** @odoo-module **/

import { MapModel } from "@elevata_googlemap/googlemap_view/googlemap_model";

export class OrderMapModel extends MapModel {
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

        const domain = [...(metaData.domain || [])];
        // Closed orders have no reason to sit on the map.
        domain.push(["stage_id.is_closed", "=", false]);

        const fieldNames = data.groupByKey
            ? [...metaData.fieldNames, data.groupByKey.split(":")[0]]
            : metaData.fieldNames;

        const specification = this._buildFieldSpecification(metaData, fieldNames);
        const orderBy = this._buildOrderByClause(metaData);

        const result = await this.orm.webSearchRead(metaData.resModel, domain, {
            specification,
            limit: metaData.limit,
            offset: metaData.offset,
            order: orderBy.join(" "),
            context: metaData.context,
        });

        data.records = result.records || [];
        data.count = result.length || 0;

        // res_partner on the googlemap view is partner_id, so the base
        // MapModel already attaches record.partner. Nothing to re-map here;
        // only count what actually has coordinates.
        for (const record of data.records) {
            if (
                record.partner &&
                record.partner.partner_latitude &&
                record.partner.partner_longitude
            ) {
                data.locatedRecordsCount++;
            }
        }

        if (!data.isGrouped) {
            data.records = data.records.filter((record) => record.partner);
        } else {
            data.recordGroups = await this._getRecordGroups(metaData, data);
        }

        data.count = data.records.length;
        return data;
    }

    _buildFieldSpecification(metaData, fieldNames) {
        const specification = {};
        const requiredFields = [
            "name",
            "product_type",
            "description",
            "reporter",
            "reporter_phone",
            "requested_employee_ids",
            "equipment_id",
            "partner_id",
            "stage_id",
        ];

        for (const fieldName of [...new Set([...fieldNames, ...requiredFields])]) {
            const field = metaData.fields[fieldName];
            if (!field) {
                specification[fieldName] = {};
            } else if (field.type === "many2one") {
                if (fieldName === "product_type") {
                    specification[fieldName] = {
                        fields: { id: {}, display_name: {}, name: {}, color: {} },
                    };
                } else {
                    specification[fieldName] = {
                        fields: { id: {}, display_name: {}, name: {} },
                    };
                }
            } else {
                specification[fieldName] = {};
            }
        }
        return specification;
    }

    _buildOrderByClause(metaData) {
        const orderBy = [];
        if (metaData.orderBy) {
            for (const field of metaData.orderBy) {
                const [fieldName, order] = field.split(":");
                orderBy.push(`${fieldName} ${order}`);
            }
        } else if (metaData.defaultOrder) {
            orderBy.push(metaData.defaultOrder.name);
            if (metaData.defaultOrder.asc) {
                orderBy.push("ASC");
            }
        }
        return orderBy;
    }

    async _getRecordGroups(metaData, data) {
        const recordGroups = {};
        const [groupByFieldName] = data.groupByKey.split(":");

        for (const record of data.records) {
            const groupValue = record[groupByFieldName];
            let groupId;
            let groupName;
            let groupColor = "#00529b";

            if (!groupValue) {
                groupId = "undefined";
                groupName = "Unassigned";
                groupColor = "#6c757d";
            } else if (typeof groupValue === "object") {
                groupId = groupValue.id;
                groupName = groupValue.display_name || groupValue.name;
                if (groupValue.color) {
                    groupColor = groupValue.color;
                }
            } else {
                groupId = groupValue;
                groupName = String(groupValue);
            }

            if (!recordGroups[groupId]) {
                recordGroups[groupId] = {
                    id: groupId,
                    name: groupName,
                    color: groupColor,
                    records: [],
                    hasLocatedRecords: false,
                    isExpanded: true,
                };
            }

            recordGroups[groupId].records.push(record);
            if (record.partner) {
                recordGroups[groupId].hasLocatedRecords = true;
            }
        }

        const filtered = {};
        for (const [groupId, group] of Object.entries(recordGroups)) {
            if (group.hasLocatedRecords) {
                filtered[groupId] = group;
            }
        }
        return filtered;
    }
}
