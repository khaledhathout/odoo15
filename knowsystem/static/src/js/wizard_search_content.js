/** @odoo-module **/

import basicFields from "web.basic_fields";
import fieldRegistry from "web.field_registry";

var wizardSearchContent = basicFields.FieldChar.extend({
    /*
     * The method to process the enter key up
    */
    _onKeydown: function(event) {
        this._super.apply(this, arguments);
        if (event.keyCode === 13) {
            this._doAction();            
        };
    },

});

fieldRegistry.add("wizardSearchContent", wizardSearchContent);

export default wizardSearchContent;
