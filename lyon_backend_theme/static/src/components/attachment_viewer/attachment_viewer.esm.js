/** @odoo-module **/

import {AttachmentViewer} from "@mail/components/attachment_viewer/attachment_viewer";
import {patch} from "web.utils";

const {useState} = owl.hooks;

// Patch attachment viewer to add min/max buttons capability
patch(AttachmentViewer.prototype, "lyon_backend_theme.AttachmentViewer", {
    setup() {
        this._super();
        this.state = useState({
            maximized: false,
        });
    },
    // Disable auto-close to allow to use form in edit mode.
    isCloseable() {
        return false;
    },
});
