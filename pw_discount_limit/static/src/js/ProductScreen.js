odoo.define('pw_discount_limit.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const models = require('point_of_sale.models');
    const { _t } = require('web.core');

    models.load_fields('product.category', 'discount_limit');
    models.load_fields('product.product', 'product_discount_limit');

    const PosDiscountLimit = (ProductScreen) =>
        class extends ProductScreen {
            _setValue(val) {
                var order = this.env.pos.get_order();
                if (order.get_selected_orderline() && this.env.pos.config.restrict_discount) {
                    var selected_orderline = order.get_selected_orderline();
                    var product_id = order.selected_orderline.product;
                    var categ = _.findWhere(this.env.pos.product_categories, {'id': product_id.categ_id[0]});
                    var discount_limit = parseFloat(product_id.product_discount_limit || categ.discount_limit)
                    if (this.currentOrder.get_selected_orderline()) {
                        if (this.state.numpadMode === 'quantity') {
                            this.currentOrder.get_selected_orderline().set_quantity(val);
                        } else if (this.state.numpadMode === 'discount') {
                            if (discount_limit && val > discount_limit){
                                this.showPopup('ErrorPopup', {
                                    title: this.env._t('Discount Restricted'),
                                    body: this.env._t('You cannot apply discount more than discount limit.'),
                                });
                                this.currentOrder.get_selected_orderline().set_discount(0);
                                NumberBuffer.reset();
                                return;
                            }
                            else {
                                this.currentOrder.get_selected_orderline().set_discount(val);
                            }
                        } else if (this.state.numpadMode === 'price') {
                            var selected_orderline = this.currentOrder.get_selected_orderline();
                            selected_orderline.price_manually_set = true;
                            selected_orderline.set_unit_price(val);
                        }
                        if (this.env.pos.config.iface_customer_facing_display) {
                            this.env.pos.send_current_order_to_customer_facing_display();
                        }
                    }
                }
                else {
                    super._setValue(val);
                }
            }
        };

    Registries.Component.extend(ProductScreen, PosDiscountLimit);

    return ProductScreen;
});
