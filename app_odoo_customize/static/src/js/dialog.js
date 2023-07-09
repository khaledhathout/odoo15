/** @odoo-module **/

import {Dialog} from "@web/core/dialog/dialog";
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";

patch(Dialog.prototype, "app_odoo_customize.Dialog", {
    setup() {
        this._super.apply(this, arguments);
        const app_system_name = session.app_system_name || "odooApp";
        this.title = app_system_name;
    },
    mounted() {
        //todo: 不生效
        this._super.apply(this, arguments);
        let self = this;
        var $dl = $('#' + self.id + ' .modal-dialog .modal-content');
        if ($dl)
            setTimeout(function () {
                $dl.draggable({
                    handle: ".modal-header"
                });
            }, 800);
    },
});

