/** @odoo-module **/

import { FileUploader } from "@mail/components/file_uploader/file_uploader";
import { patch } from "web.utils";


patch(FileUploader.prototype, "cloud_base/static/src/components/file_uploader/file_uploader.js", {
    /*
    * Re-write to update folder
    * We do not change _createFormData since in this case it will be needed to fully redevelop the controller
    */
    async _onAttachmentUploaded({ attachmentData, composer, thread }) {
        const _super = this._super.bind(this);
        if (thread && thread.cloudsFolderId && !composer) {
            // When we are from composer, message will be allocated to the folder in postprocess
            await this.env.services.rpc({
                model: "ir.attachment",
                method: "write",
                args: [[attachmentData.id], {"clouds_folder_id": thread.cloudsFolderId}]
            });
        }
        const res = await _super(...arguments);
        return res
    },
    /*
    * Re-write to trigger reload since attachment folder might be updated
    */
    async uploadFiles(files) {
        await this._super(...arguments);
        if (this.thread) {
            await this.thread.refreshForFolder(
                this.thread.cloudsFolderId ? [["clouds_folder_id", "in", [this.thread.cloudsFolderId]]] : [],
                this.thread.cloudsFolderId || false
            );
        }
    },
});
