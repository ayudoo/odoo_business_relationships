/** @odoo-module **/

// Note, patching the mixins doesn't help. We need to patch both renderers.

import { PageListRenderer } from "@website/components/views/page_list";
import { PageKanbanRenderer } from "@website/components/views/page_kanban";
import { patch } from "@web/core/utils/patch";

var recordFilter = function(self, record, records) {
  const websiteId = record.data.website_id && record.data.website_id[0];
  const groupIds = new Set(record.data.group_ids.currentIds);
  // we need to adapt the filter part for websites without websiteID in two ways:
  // Only check for other pages belonging to all or the active website
  // and check for matching groups.
  return !self.props.activeWebsite.id ||
    self.props.activeWebsite.id === websiteId ||
    !websiteId && records.filter(rec =>
      !(rec.data.website_id && record.data.website_id[0] != self.props.activeWebsite.id) &&
      rec.data.website_url === record.data.website_url &&
      rec.data.group_ids.currentIds.length === groupIds.size &&
      [...rec.data.group_ids.currentIds].every(groupId => groupIds.has(groupId))
    ).length === 1;
}

patch(PageListRenderer.prototype, "website_user_type_page_list_patch", {
  recordFilter(record, records) {
    return recordFilter(this, record, records);
  }
});

patch(PageKanbanRenderer.prototype, "website_user_type_page_kanban_patch", {
  recordFilter(record, records) {
    return recordFilter(this, record, records);
  }
});
