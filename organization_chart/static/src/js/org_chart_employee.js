odoo.define("organization_chart.employee_orgchart", function (require) {
    "use strict";

    var session = require('web.session');
    var ajax = require('web.ajax');

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');
    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

    var EmployeeOrgChart = AbstractAction.extend({
        hasControlPanel: true,
        contentTemplate: 'organization_chart.orgchart',
        events: _.extend({}, Widget.prototype.events, {
            'click .add_node': '_on_add_node',
            'click .edit_node': '_on_edit_node',
            'click .delete_node': '_on_delete_node',
            'dragstart .node': '_on_drag_node',
            'drop .node': '_on_drop_node',
        }),
        init: function (parent, context) {
            this._super(parent, context);
        },
        willStart: function () {
            var self = this;
            var def = this._rpc({
                route: '/orgchart/get_user_group',
                params: {
                    user_id: session.uid || false,
                }
            }).then(function (result) {
                if (result && result[0]) {
                    self.is_hr_user = result[0].is_hr_user;
                    self.is_hr_manager = result[0].is_hr_manager;
                }
            });
            return Promise.all([ajax.loadLibs(this), def, this._super()]).then(function () {
                return self.fetch_data();
            });
        },
        start: function () {
            var self = this;
            this._computeControlPanelProps();
            core.bus.on('resize', this, function () {
                self._onResize();
            });
            core.bus.on('DOM_updated', this, function () {
                self._onResize();
            });
            return this._super().then(function () {
                self.render_orgchart();
            });
        },
        _computeControlPanelProps: function () {
            var self = this;
            self.$searchview = $(QWeb.render("organization_chart.orgchartSearchButtons", {
                widget: this,
            }));

            self.$searchview.find('button.js_btn_search_filter').click((ev) => {
                self.clearFilterResult();
                self.filterNodes(self.$('input.js_btn_search').val().toLowerCase());
            });

            self.$searchview.find('button.js_btn_search_clear').click((ev) => {
                self.clearFilterResult();
            });

            self.$searchview.find('input.js_btn_search').keyup((ev) => {
                ev.preventDefault();
                var value = ev.target.value.toLowerCase().trim();
                if (value.length != 0) {
                    self.filterNodes(value.toLowerCase());
                } else {
                    self.clearFilterResult();
                }
            });

            self.$buttons = $(QWeb.render('organization_chart.orgchartControlButtons', {
                widget: self
            }));

            self.$buttons.find('button.js_btn_reload').click((ev) => {
                self.reload_orgchart();
            });

            self.$buttons.find('button.js_btn_export_png').click((ev) => {
                self.export_orgchart_png();
            });

            self.$buttons.find('button.js_btn_export_pdf').click((ev) => {
                self.export_orgchart_pdf();
            });

            self.$buttons.find('button.js_btn_switch').click((ev) => {
                self.switch_orgchart();
            });

            self.$buttons.find('button.js_btn_zoom_in').click((ev) => {
                self.zoom_in_orgchart();
            });

            self.$buttons.find('button.js_btn_zoom_out').click((ev) => {
                self.zoom_out_orgchart();
            });

            self.$buttons.find('button.js_btn_path').click((ev) => {
                self.report_path();
            });

            self.$buttons.find('button.js_btn_expand').click((ev) => {
                self.expand_orgchart();
            });

            this.controlPanelProps.cp_content = {
                $searchview: this.$searchview,
                $buttons: this.$buttons,
            };
        },
        update_cp: function () {
            if (!this.$buttons) {
                this.renderButtons();
            }
            this.controlPanelProps.cp_content = {
                $buttons: this.$buttons
            };
            return this.updateControlPanel();
        },
        renderButtons: function () {
            var self = this;
            this.$buttons = $(QWeb.render("organization_chart.orgchartControlButtons", {
                widget: self
            }));
            return this.$buttons;
        },
        fetch_data: function () {
            var self = this;
            var session = self.getSession();
            var company_id = session.user_context.allowed_company_ids[0];
            var prom = self._rpc({
                route: '/orgchart/getdata',
                params: {
                    company_id: company_id
                }
            });
            prom.then(function (result) {  
                console.log(result)
                if (result && result.data){
                    self.employee_data = result.data;       
                }
            });
            return prom;
        },

        loopChart: function ($hierarchy) {
            var self = this;
            var $siblings = $hierarchy.children('.nodes').children('.hierarchy');
            if ($siblings.length) {
                $siblings.filter(':not(.hidden)').first().addClass('first-shown')
                    .end().last().addClass('last-shown');
            }
            $siblings.each(function (index, sibling) {
                self.loopChart($(sibling));
            });
        },

        filterNodes: function (keyWord) {
            var self = this;
            if (!keyWord.length) {
                window.alert('Please type key word firstly.');
                return;
            } else {
                var $chart = self.$('.orgchart');
                // disalbe the expand/collapse feture
                $chart.addClass('noncollapsable');
                // distinguish the matched nodes and the unmatched nodes according to the given key word
                $chart.find('.node').filter(function (index, node) {
                    return $(node).text().toLowerCase().indexOf(keyWord) > -1;
                }).addClass('matched')
                    .closest('.hierarchy').parents('.hierarchy').children('.node').addClass('retained');
                // hide the unmatched nodes
                $chart.find('.matched,.retained').each(function (index, node) {
                    $(node).removeClass('slide-up')
                        .closest('.nodes').removeClass('hidden')
                        .siblings('.hierarchy').removeClass('isChildrenCollapsed');
                    var $unmatched = $(node).closest('.hierarchy').siblings().find('.node:first:not(.matched,.retained)')
                        .closest('.hierarchy').addClass('hidden');
                });
                // hide the redundant descendant nodes of the matched nodes
                $chart.find('.matched').each(function (index, node) {
                    if (!$(node).siblings('.nodes').find('.matched').length) {
                        $(node).siblings('.nodes').addClass('hidden')
                            .parent().addClass('isChildrenCollapsed');
                    }
                });
                // loop chart and adjust lines
                self.loopChart($chart.find('.hierarchy:first'));
            }
        },

        zoom_in_orgchart: function () {
            var self = this;
            var currentZoom = parseFloat(self.$('.chart_container').css('zoom'));
            self.$('.chart_container').css('zoom', currentZoom += 0.1);
        },

        zoom_out_orgchart: function () {
            var self = this;
            var currentZoom = parseFloat(self.$('.chart_container').css('zoom'));
            self.$('.chart_container').css('zoom', currentZoom -= 0.1);
        },

        report_path: function () {
            var self = this;
            var $selected = self.$('.chart_container').find('.node.focused');
            if ($selected.length) {
                $selected.parents('.nodes').children(':has(.focused)').find('.node:first').each(function (index, superior) {
                    if (!$(superior).find('.horizontalEdge:first').closest('table').parent().siblings().is('.hidden')) {
                        $(superior).find('.horizontalEdge:first').trigger('click');
                    }
                });
            } else {
                alert('please select the node firstly');
            }
        },

        clearFilterResult: function () {
            var self = this;
            self.$('.orgchart').removeClass('noncollapsable')
                .find('.node').removeClass('matched retained')
                .end().find('.hidden, .isChildrenCollapsed, .first-shown, .last-shown').removeClass('hidden isChildrenCollapsed first-shown last-shown')
                .end().find('.slide-up, .slide-left, .slide-right').removeClass('slide-up slide-right slide-left');
        },
        reload_orgchart: function (event) {
            var self = this;
            self.$(".chart_container").empty();
            self.fetch_data().then(function () {
                self.render_orgchart();
            });
        },
        expand_orgchart: function () {
            var self = this;
            self.$(".chart_container").empty();
            self.fetch_data().then(function () {
                self.render_orgchart();
            }).then(function () {
                self.$('.orgchart').removeClass('noncollapsable')
                    .find('.node').removeClass('matched retained')
                    .end().find('.hidden, .isChildrenCollapsed, .first-shown, .last-shown').removeClass('hidden isChildrenCollapsed first-shown last-shown')
                    .end().find('.slide-up, .slide-left, .slide-right').removeClass('slide-up slide-right slide-left');
            });
        },
        switch_orgchart: function (event) {
            var self = this;
            if (self.orgchart && self.orgchart != undefined) {
                if (self.orgchart.options.direction === "t2b") {
                    self.$('.chart_container').css('text-align', 'left');
                    self.orgchart.init({ 'direction': 'l2r' });
                } else {
                    self.$('.chart_container').css('text-align', 'center');
                    self.orgchart.init({ 'direction': 't2b' });
                }
            }
        },
        render_orgchart: function (event) {
            var self = this;
            var nodeTemplate = function (data) {
                if (data._name === 'hr.employee') {
                    return `
                        <div class="title">${data.name}</div>
                        <div class="content">
                            <span class="photo">
                                <img class="img" src="/web/image?model=hr.employee&amp;field=avatar_128&amp;id=${data.id}" style="width: 128px;height: 128px;"/>
                            </span>
                            <span style="min-height: 35px; display: flex; justify-content: center; align-items: center; background-color: #cecece47;">
                                ${data.title}
                            </span>
                        </div>
                    `;
                } else if (data._name === 'res.company') {
                    return `
                        <div class="title">${data.name}</div>
                        <div class="content">
                            <span class="photo">
                                <img class="img" src="/web/image?model=res.company&amp;field=logo&amp;id=${Math.abs(data.id)}" style="width: 128px;height: 35px;"/>
                            </span>
                            <span style="min-height: 35px; display: flex; justify-content: center; align-items: center; background-color: #cecece47;">
                                ${data.title}
                            </span>
                        </div>
                    `;
                }
            };
            console.log("=================>>",self.employee_data)
            self.orgchart = this.$('.chart_container').orgchart({
                'data': self.employee_data,
                'nodeTemplate': nodeTemplate,
                'nodeContent': 'title',
                'toggleSiblingsResp': false,
                'draggable': self.is_hr_manager ? true : false,
                'verticalLevel': 4,
                'visibleLevel': 2,
                'pan': true,
                'zoom': false,
                'direction': 't2b',
                'dropCriteria': function ($draggedNode, $dragZone, $dropZone) {
                    if ($draggedNode.find('.content').text().indexOf('manager') > -1 && $dropZone.find('.content').text().indexOf('engineer') > -1) {
                        return false;
                    }
                    return true;
                },

                'createNode': function ($node, data) {
                    var secondMenuIcon = $('<i>', {
                        'class': 'oci oci-info-circle second-menu-icon',
                        click: function () {
                            $(this).siblings('.second-menu').toggle();
                        }
                    });
                    var secondMenu = '<div class="second-menu">';
                    secondMenu += '<img class="avatar add_node" id="' + data.id + '"src="/organization_chart/static/src/img/add.png"">';
                    secondMenu += '<img class="avatar edit_node" id="' + data.id + '"src="/organization_chart/static/src/img/edit.png"">';
                    secondMenu += '<img class="avatar delete_node" id="' + data.id + '"src="/organization_chart/static/src/img/delete.png"">';
                    secondMenu += '</div>';

                    if (self.is_hr_manager && data._name === 'hr.employee') {
                        $node.append(secondMenuIcon).append(secondMenu);
                    }
                }
            });
        },
        export_orgchart_png: function (event) {
            var self = this;
            var $oContent = self.$('.o_content');
            $oContent.addClass('chart_export');
            self.orgchart.export('Employe OrgChart', 'png');
            $oContent.removeClass('chart_export');
            self.$('.mask').remove();
        },
        export_orgchart_pdf: function (event) {
            var self = this;
            var $oContent = self.$('.o_content');
            $oContent.addClass('chart_export');

            if (self.$('.spinner').length) {
                return false;
            }

            var $chartContainer = self.$('.chart_container');
            var $mask = $chartContainer.find('.mask');
            if (!$mask.length) {
                $chartContainer.append('<div class="mask"><i class="oci oci-spinner spinner"></i></div>');
            } else {
                $mask.removeClass('hidden');
            }
            var sourceChart = $chartContainer.addClass('canvasContainer').find('.orgchart:not(".hidden")').get(0);
            var flag = self.orgchart.options.direction === 'l2r' || self.orgchart.options.direction === 'r2l';
            html2canvas(sourceChart, {
                'width': flag ? sourceChart.clientHeight : sourceChart.clientWidth,
                'height': flag ? sourceChart.clientWidth : sourceChart.clientHeight,
                'onclone': function (cloneDoc) {
                    $(cloneDoc).find('.canvasContainer').css('overflow', 'visible')
                        .find('.orgchart:not(".hidden"):first').css('transform', '');

                    $(cloneDoc).find('.second-menu-icon').css('display', 'none');
                }
            }).then(function (canvas) {
                $chartContainer.find('.mask').remove('hidden');
                $oContent.removeClass('chart_export');

                var doc = {};
                var docWidth = Math.floor(canvas.width);
                var docHeight = Math.floor(canvas.height);
                if (!window.jsPDF) {
                    window.jsPDF = window.jspdf.jsPDF;
                }

                if (docWidth > docHeight) {
                    doc = new jsPDF({
                        orientation: 'landscape',
                        unit: 'px',
                        format: [docWidth, docHeight]
                    });
                } else {
                    doc = new jsPDF({
                        orientation: 'portrait',
                        unit: 'px',
                        format: [docHeight, docWidth]
                    });
                }
                var width = doc.internal.pageSize.getWidth();
                var height = doc.internal.pageSize.getHeight();
                doc.addImage(canvas.toDataURL(), 'png', 0, 0, width, height);
                doc.save('Employe OrgChart' + '.pdf');

                $chartContainer.removeClass('canvasContainer');
            }, function () {
                $chartContainer.removeClass('canvasContainer');
            });
            $chartContainer.find('.mask').remove();
            $oContent.removeClass('chart_export');
        },
        _on_add_node: function (event) {
            event.stopPropagation();
            event.preventDefault();
            var self = this;
            var parent_id = event.target.id;
            if (parent_id) {
                self.do_action({
                    name: _t("Add new Employee"),
                    type: 'ir.actions.act_window',
                    res_model: 'hr.employee',
                    view_mode: 'form',
                    view_type: 'form',
                    context: { 'parent_id': parseInt(parent_id) },
                    views: [[false, 'form']],
                    target: 'new'
                }).then(function () {
                    return self.reload_orgchart();
                });
            } else {
                return self.displayNotification({ message: _t("Something went wrong: Please contact admnistrator.") });
            }
        },
        _on_edit_node: function (event) {
            event.stopPropagation();
            event.preventDefault();
            var self = this;
            self.do_action({
                name: _t("Edit Employee"),
                type: 'ir.actions.act_window',
                res_model: 'hr.employee',
                view_mode: 'form',
                view_type: 'form',
                res_id: parseInt(event.target.id),
                views: [[false, 'form']],
                target: 'new'
            }).then(function () {
                return self.reload_orgchart();
            });
        },
        _on_delete_node: function (event) {
            var self = this;
            var employee_id = event.target.id;
            if (employee_id) {
                Dialog.confirm(this, _t("Do you Want to Delete this Employee ?"), {
                    confirm_callback: function () {
                        self._rpc({
                            model: 'hr.employee',
                            method: 'unlink',
                            args: [parseInt(employee_id)],
                        })
                            .then(function () {
                                self.reload_orgchart();
                            });
                    }
                });
            } else {
                return self.displayNotification({ message: _t("Something went wrong: Please contact admnistrator.") });
            }
        },
        _on_drag_node: function (event) {
            event.originalEvent.dataTransfer.setData('source_id', event.target.id);
        },
        _on_drop_node: function (event) {
            var self = this;
            var source_id = event.originalEvent.dataTransfer.getData("source_id");
            var target_id = event.currentTarget.id;
            
            if (source_id && target_id) {
                self._rpc({
                    route: "/orgchart/update",
                    params: {
                        source_id: parseInt(source_id),
                        target_id: parseInt(target_id),
                    },
                }).then(function (result) {
                    if (!result) {
                        return self.displayNotification({ message: _t("Something went wrong: Please contact admnistrator.") });
                    }
                });
            } else {
                return self.displayNotification({ message: _t("Something went wrong: Please contact admnistrator.") });
            }
        },
        _onResize: function () {
            var self = this;
            var width = $(window).width();
            if (width > 576) {
                self.orgchart.init({ 'verticalLevel': 4 });
            } else {
                self.orgchart.init({ 'verticalLevel': 2 });
            }

            var $container = self.$('.chart_container');
            $container.scrollLeft(($container[0].scrollWidth - $container.width()) / 2);

        }
    });

    core.action_registry.add('organization_chart.employee_orgchart', EmployeeOrgChart);
    return EmployeeOrgChart;
});