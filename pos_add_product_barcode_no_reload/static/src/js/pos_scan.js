odoo.define('pos_add_product_barcode_no_reload.pos_scan', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var models = require('point_of_sale.models');
    var utils = require('web.utils');
    const { Gui } = require('point_of_sale.Gui');

    var posmodel_super = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        async check_product_barcode (parsed_code){
            const self = this;
            const done = $.Deferred();
            const product = this.env.pos.db.get_product_by_barcode(parsed_code.base_code)
            if(!product){
                var product_index = _.findIndex(this.models, function (model) {
                    return model.model === "product.product";
                });

                var product_model = this.models[product_index];
                var context = typeof product_model.context === 'function' ? product_model.context(self,{}) : product_model.context;

                var domain = product_model.domain (self);
                var domain_barcode = ['barcode', '=', parsed_code.base_code];
                domain = ['&'].concat(domain);
                domain = domain.concat([domain_barcode]);

                await rpc.query({
                        model: product_model.model,
                        method: 'search_read',
                        domain: domain,
                        fields: product_model.fields,
                        context: context,
                        order_by: product_model.order,
                }).then(function (products) {
                    if (products && products.length > 0){
                        var using_company_currency = self.config.currency_id[0] === self.company.currency_id[0];
                        var conversion_rate = self.currency.rate / self.company_currency.rate;
                        self.db.update_products(_.map(products, function (product) {
                            if (!using_company_currency) {
                                product.lst_price = round_pr(product.lst_price * conversion_rate, self.currency.rounding);
                            }
                            product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                            product.pos = self;
                            return new models.Product({}, product);
                        }));
                        return done.resolve(true);
                    }
                    else {
                        return done.resolve(false);
                    }
                });
            }
            return done.resolve(true);
        },

        scan_product: function(parsed_code){
            var self = this;
            var done = $.Deferred();

            var res = posmodel_super.scan_product.apply(this, arguments);
            if (res){
                done.resolve(true);
            }else if (!res){
                 var product_index = _.findIndex(this.models, function (model) {
                    return model.model === "product.product";
                });

                var product_model = this.models[product_index];
                var context = typeof product_model.context === 'function' ? product_model.context(self,{}) : product_model.context;
                var domain = product_model.domain (self);
                var domain_barcode = ['barcode', '=', parsed_code.base_code];
                domain = ['&'].concat(domain);
                domain = domain.concat([domain_barcode]);

                var records = rpc.query({
                    model: product_model.model,
                    method: 'search_read',
                    domain: domain,
                    fields: product_model.fields,
                    context: context,
                    order_by: product_model.order,
                });

                records.then(function (products) {
                    if (products && products.length > 0){
                        var using_company_currency = self.config.currency_id[0] === self.company.currency_id[0];
                        var conversion_rate = self.currency.rate / self.company_currency.rate;
                        self.db.update_products(_.map(products, function (product) {
                            if (!using_company_currency) {
                                product.lst_price = round_pr(product.lst_price * conversion_rate, self.currency.rounding);
                            }
                            product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                            product.pos = self;
                            return new models.Product({}, product);
                        }));

                        // do scan again
                        self.scan_product(parsed_code);
                        done.resolve(true);
                    }
                    else {
                        Gui.showPopup("ErrorBarcodePopup", { code: parsed_code.code});

                        done.resolve(false);
                        return done;
                    }
                });
            }
            return done.resolve(true);
        },

    });

});