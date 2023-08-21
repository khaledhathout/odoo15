odoo.define('bsi_pos_clear_cart.ClearCart', function(require) {
    'use strict';
       const PosComponent = require('point_of_sale.PosComponent');
       const ProductScreen = require('point_of_sale.ProductScreen');
       const { useListener } = require('web.custom_hooks');
       const Registries = require('point_of_sale.Registries');
       class ClearCart extends PosComponent {
           constructor() {
               super(...arguments);
               useListener('click', this.onClick);
           }  
           onClick() {
                var self = this;
                this.clear_button_fun();
           }
           clear_button_fun(){
                var order = this.env.pos.get_order();
                while(order.get_selected_orderline()) {
                    order.remove_orderline(order.get_selected_orderline())
                }   
            }
       }
       ClearCart.template = 'ClearCart';
       ProductScreen.addControlButton({
           component: ClearCart,
           condition: function() {
               return this.env.pos;
           },
       });
       Registries.Component.add(ClearCart);
       return ClearCart;
    });
