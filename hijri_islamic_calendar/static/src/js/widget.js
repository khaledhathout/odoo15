odoo.define('hijri_islamic_calendar.HijriWidget', function(require) { "use strict";

    var field_registry = require('web.field_registry');
    var fields = require('web.basic_fields');

    var FieldHijriWidget = fields.FieldChar.extend({
        template: 'FieldHijriWidget',

        format_hijri: function (day, month, year) {
             if(!day | !month | !year ){
               return ""
            }

            return "".concat(day, " / ", month, " / ", year);
        },

        split_hijri: function (value) {
            if(value){
                var day = value.split("/")[0].trim();
                var month = value.split("/")[1].trim();
                var year = value.split("/")[2].trim();
            }else{
                var day = "";
                var month = "";
                var year = "";
            }



            return {day:day, month:month, year:year}
        },

        _renderReadonly: function () {
            this.$el.text( this.value || "");
        },

        _getValue: function () {
            var $input_day = this.$el.find('.day');
            var $input_month = this.$el.find('.month');
            var $input_year = this.$el.find('.year');
            var val = this.format_hijri($input_day.val(), $input_month.val(), $input_year.val())
            return val || "";
        },

        _renderEdit: function () {
            var hijri = this.split_hijri(this.value)

             var $input_day = this.$el.find('.day');
             $input_day.val(hijri.day);
             this.$input = $input_day  // Adjustment

             this.$('.day').val(hijri.day)
             this.$('.month').val(hijri.month)
             this.$('.year').val(hijri.year)


//             this.$el.find('.day') = $input_day




        },

    });

    field_registry
        .add('date_hijri', FieldHijriWidget);

return {
    FieldHijriWidget: FieldHijriWidget
};

});
