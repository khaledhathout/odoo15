/** @odoo-module **/

import { Chatter } from "@mail/components/chatter/chatter";
import { AttachmentBox } from "@mail/components/attachment_box/attachment_box";
import { patch } from "web.utils";
import { cloudFolderTree } from "@cloud_base/components/cloud_folder_tree/cloud_folder_tree";

AttachmentBox.components.CloudFolderTree = cloudFolderTree;

patch(AttachmentBox.prototype, "cloud_base/static/src/components/attachment_box/attachment_box.js", {
    /* 
    * @private
    * The method to trigger reload based on selected folder
    */
    _reloadBasedOnFolders(domain, existing_domain, checked_folder) {
        var self = this;
        this.checkedFolder = checked_folder;
        this.chatter.thread.refreshForFolder(domain, checked_folder);
    },
});
