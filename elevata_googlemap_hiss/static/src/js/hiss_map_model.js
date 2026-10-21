/** @odoo-module **/

import { MapModel } from "@elevata_googlemap/googlemap_view/googlemap_model";

export class HissMapModel extends MapModel {
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

        if (!metaData.domain) {
            metaData.domain = [];
        }
        metaData.domain.push(["is_elevator", "=", true]);

        const fieldNames = data.groupByKey
            ? [...metaData.fieldNames, data.groupByKey.split(":")[0]]
            : metaData.fieldNames;

        const specification = this._buildFieldSpecification(metaData, fieldNames);
        const orderBy = this._buildOrderByClause(metaData);

        const result = await this.orm.webSearchRead(
            metaData.resModel,
            metaData.domain,
            {
                specification,
                limit: metaData.limit,
                offset: metaData.offset,
                order: orderBy.join(" "),
                context: metaData.context,
            }
        );

        data.records = result.records || [];
        data.count = result.length || 0;

        const partnerIds = data.records
            .map((record) => {
                const partner = record[metaData.resPartnerField];
                if (Array.isArray(partner)) {
                    return partner[0];
                } else if (partner && typeof partner === "object") {
                    return partner.id;
                }
                return partner;
            })
            .filter((id) => id)
            .map((id) => parseInt(id, 10))
            .filter((id) => !isNaN(id));

        data.partnerIds = [...new Set(partnerIds)];

        if (data.partnerIds.length) {
            data.partners = await this.orm.read(
                "res.partner",
                data.partnerIds,
                [
                    "id",
                    "name",
                    "display_name",
                    "partner_latitude",
                    "partner_longitude",
                    "complete_contact_address",
                    "commercial_company_name",
                    "parent_id",
                    "is_company",
                    "parent_name",
                ]
            );
            this._addPartnerToRecord(metaData, data);
            if (data.isGrouped) {
                data.recordGroups = await this._getRecordGroups(metaData, data);
            }
        }

        return data;
    }

    _buildFieldSpecification(metaData, fieldNames) {
        const specification = {};
        const requiredFields = [
            "name",
            "elevator_number",
            "elevator_type_id",
            "manufacturing_number",
            "mechanical_brand_id",
            "last_inspection",
            "partner_id",
        ];

        for (const fieldName of [...new Set([...fieldNames, ...requiredFields])]) {
            const field = metaData.fields[fieldName];
            if (field && field.type === "many2one") {
                specification[fieldName] = {
                    fields: { id: {}, display_name: {}, name: {} },
                };
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

    _addPartnerToRecord(metaData, data) {
        super._addPartnerToRecord(metaData, data);

        data.records = data.records.filter(
            (record) =>
                record.partner &&
                record.partner.partner_latitude &&
                record.partner.partner_longitude
        );

        data.count = data.records.length;
        data.locatedRecordsCount = data.records.length;
    }

    toggleGroupExpansion(groupId) {
        const group = this.data.recordGroups && this.data.recordGroups[groupId];
        if (group) {
            group.isExpanded = !group.isExpanded;
            this.notify();
        }
    }
}
