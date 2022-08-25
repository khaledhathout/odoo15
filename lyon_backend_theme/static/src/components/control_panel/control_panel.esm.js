/** @odoo-module **/

import LegacyControlPanel from "web.ControlPanel";
import {ControlPanel} from "@web/search/control_panel/control_panel";
import {SearchBar} from "@web/search/search_bar/search_bar";
import {deviceContext} from "@lyon_backend_theme/components/ui_context.esm";
import {patch} from "web.utils";

const {useState, useContext} = owl.hooks;

// In v15.0 there are two ControlPanel's. They are mostly the same and are used in legacy and new owl views.
// We extend them two mostly the same way.

// Patch legacy control panel to add states for mobile quick search
patch(LegacyControlPanel.prototype, "lyon_backend_theme.LegacyControlPanelMobile", {
    setup() {
        this._super();
        this.state = useState({
            mobileSearchMode: this.props.withBreadcrumbs ? "" : "quick",
        });
        this.ui = useContext(deviceContext);
    },
    setMobileSearchMode(ev) {
        this.state.mobileSearchMode = ev.detail;
    },
});

// Patch control panel to add states for mobile quick search
patch(ControlPanel.prototype, "lyon_backend_theme.ControlPanelMobile", {
    setup() {
        this._super();
        this.state = useState({
            mobileSearchMode: "",
        });
        this.ui = useContext(deviceContext);
    },
    setMobileSearchMode(ev) {
        this.state.mobileSearchMode = ev.detail;
    },
});
patch(SearchBar, "lyon_backend_theme.SearchBarMobile", {
    template: "lyon_backend_theme.SearchBar",
});
