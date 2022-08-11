odoo.define('search_panel_toggle.SPanel',function (require) {
"use strict";
	var core = require("web.core");
	var QWeb = core.qweb;
	var view_registry = require('web.view_registry');
	var select_create_controllers_registry = require('web.select_create_controllers_registry');
	var _t = core._t;
	const utils = require('web.utils');	
	const SearchPanel = require("web.searchPanel");

    utils.patch(SearchPanel.prototype,"Dmmsys.search.panel", {
        mounted() {
			this._super(...arguments);
			let self = this;
			let $el = $(this.el);
			let $toggleButton = $el.siblings('div.btn-search-panel-toggle');
			if('width' in this.props){
				$el.css('flex-basis',this.props.width+"px");
			}
			if($toggleButton.length){
				return;
			}
	       	let $hideButton = QWeb.render("SearchPanel.HideButton",this);
	       	let $buttonEl = $(document.createDocumentFragment());
	       	$buttonEl.append($hideButton);	       	       
	       	$buttonEl.find('div.btn-search-panel-toggle').click(function(){
				if($el.hasClass('o_hidden')){
					self.do_show();
					$(this).removeClass('fa-caret-right show-panel').addClass('fa-caret-left hide-panel');;
				}else{
					self.do_hide();
					$(this).addClass('fa-caret-right show-panel').removeClass('fa-caret-left hide-panel');
				}
			 }); 
	       $el.after($buttonEl);
		},
		
		do_hide(){
			if (this.el) {
            	$(this.el).addClass('o_hidden');
        	}

		},
		do_show() {
			if (this.el) {
				$(this.el).removeClass('o_hidden');
			}
    	},
        
    });

});