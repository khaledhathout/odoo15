odoo.define('global_discount.GlobalDiscountList', function (require) {
    "use strict";
    
    var core = require('web.core');
    var ListRenderer = require('web.ListRenderer');
    var _t = core._t;
    
    ListRenderer.include({
        _renderRow: function (record) {
            var $row = this._super(record);
            if (record.data.global_discount!=undefined && record.data.global_discount===true){
                if (this.state.fieldsInfo.list.product_id.invisible==undefined){
                    $row.css("display", "none")
                }
            }
            return $row;
            },
    }); 
    
    });
    