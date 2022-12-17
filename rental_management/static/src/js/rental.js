odoo.define('rental_management.PropertyDashboard', function (require) {
    'use strict';
    const AbstractAction = require('web.AbstractAction');
    const ajax = require('web.ajax');
    const core = require('web.core');
    const rpc = require('web.rpc');
    const session = require('web.session')
    const web_client = require('web.web_client');
    const _t = core._t;
    const QWeb = core.qweb;

    const ActionMenu = AbstractAction.extend({

        template: 'rentalDashboard',

        events: {
            'click .avail-property': 'view_avail_property',
            'click .total-property': 'view_total_property',
            'click .booked-property': 'view_booked_property',
            'click .lease-property': 'view_lease_stats',
            'click .sale-property': 'view_sale_stats',
            'click .sold-property': 'view_sold_stats',
            'click .sold-total': 'view_property_sold',
            'click .rent-total': 'view_property_rent',
            'click .draft-contract': 'view_draft_rent',
            'click .running-contract': 'view_running_rent',
            'click .expire-contract': 'view_expire_rent',
            'click .booked-property-sale': 'view_booked_sale',
            'click .sale-sold': 'view_sale_sold',
        },
        renderElement: function (ev) {
            const self = this;
            $.when(this._super())
                .then(function (ev) {
                    rpc.query({
                        model: "property.details",
                        method: "get_property_stats",
                    }).then(function (result) {
                        $('#avail_property').empty().append(result['avail_property']);
                        $('#booked_property').empty().append(result['booked_property']);
                        $('#lease_property').empty().append(result['lease_property']);
                        $('#sale_property').empty().append(result['sale_property']);
                        $('#sold_property').empty().append(result['sold_property']);
                        $('#total_property').empty().append(result['total_property']);
                        $('#sold_total').empty().append(result['sold_total']);
                        $('#rent_total').empty().append(result['rent_total']);
                        $('#draft_contract').empty().append(result['draft_contract']);
                        $('#running_contract').empty().append(result['running_contract']);
                        $('#expire_contract').empty().append(result['expire_contract']);
                        $('#booked').empty().append(result['booked']);
                        $('#sale_sold').empty().append(result['sale_sold']);
                    });
                });
        },
        view_avail_property : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Available Property'),
                type: 'ir.actions.act_window',
                res_model: 'property.details',
                domain: [['stage', '=', 'available']],
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_total_property : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Total Property'),
                type: 'ir.actions.act_window',
                res_model: 'property.details',
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_booked_property : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Booked Property'),
                type: 'ir.actions.act_window',
                res_model: 'property.details',
                domain: [['stage', '=', 'booked']],
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_lease_stats : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Property On Lease'),
                type: 'ir.actions.act_window',
                res_model: 'property.details',
                domain: [['stage', '=', 'on_lease']],
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_sale_stats : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Property On Sale'),
                type: 'ir.actions.act_window',
                res_model: 'property.details',
                domain: [['stage', '=', 'sale']],
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_sold_stats : function (ev){
             ev.preventDefault();
            return this.do_action({
                name: _t('Sold Property'),
                type: 'ir.actions.act_window',
                res_model: 'property.details',
                domain: [['stage', '=', 'sold']],
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_property_sold : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Property Sold'),
                type: 'ir.actions.act_window',
                res_model: 'property.vendor',
                domain: [['stage', '=', 'sold']],
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_property_rent : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Property Rent'),
                type: 'ir.actions.act_window',
                res_model: 'rent.invoice',
                domain: ['|', ['type', '=', 'rent'],['type', '=', 'full_rent']],
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
         view_draft_rent : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Draft Contract'),
                type: 'ir.actions.act_window',
                res_model: 'tenancy.details',
                domain: [['contract_type', '=', 'new_contract']],
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_running_rent : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Running Contract'),
                type: 'ir.actions.act_window',
                res_model: 'tenancy.details',
                domain: [['contract_type', '=', 'running_contract']],
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_expire_rent : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Expire Contract'),
                type: 'ir.actions.act_window',
                res_model: 'tenancy.details',
                domain: [['contract_type', '=', 'expire_contract']],
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
         view_booked_sale : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Booked Property'),
                type: 'ir.actions.act_window',
                res_model: 'property.vendor',
                domain: [['stage', '=', 'booked']],
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_sale_sold : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Sold Property'),
                type: 'ir.actions.act_window',
                res_model: 'property.vendor',
                domain: [['stage', '=', 'sold']],
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },

        get_action: function (ev, name, res_model){
            ev.preventDefault();
            return this.do_action({
                name: _t(name),
                type: 'ir.actions.act_window',
                res_model: res_model,
                views: [[false, 'kanban'],[false, 'tree'],[false, 'form']],
                target: 'current'
            });
        },

        willStart: function () {
            const self = this;
            self.drpdn_show = false;
            return Promise.all([ajax.loadLibs(this), this._super()]);
        },
    });
    core.action_registry.add('property_dashboard', ActionMenu);

});
