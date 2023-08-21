odoo.define('pos_add_product_barcode_no_reload.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');

    const MultiBarcodeProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _barcodeProductAction(code) {
                  const res = await this.env.pos.check_product_barcode(code);
                  if (res) {
                     super._barcodeProductAction(...arguments);
                  }
                  else {
                     return this._barcodeErrorAction(code);
                  }
            }
        };

    Registries.Component.extend(ProductScreen, MultiBarcodeProductScreen);

    return ProductScreen;
});
