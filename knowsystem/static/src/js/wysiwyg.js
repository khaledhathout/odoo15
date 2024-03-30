/** @odoo-module **/

import Wysiwyg from "web_editor.wysiwyg";
import rpc from "web.rpc";
import { _lt } from "web.core";
import { preserveCursor } from "@web_editor/../lib/odoo-editor/src/OdooEditor";

Wysiwyg.include({
    /*
     * Re-write to add KnowSystem quick search if it is required
    */  
    _getCommands: function () {
        const commands = this._super.apply(this, arguments);
        if (this.options.knowsystemTurn) {
            commands.push({
                groupName: "KnowSystem",
                title: _lt("KnowSystem"),
                description: _lt("Apply to knowledge base"),
                fontawesome: "fa-superpowers",
                callback: () => {
                    this.onOpenKnowSystem({forceDialog: true});
                },                
            })
        }
        return commands;
    },
    _getSnippetsCommands: function () {
        if (this.options.know_snippets) {
            return []
        }
        const commands = this._super.apply(this, arguments);
        return commands;
    },
    /* 
     * @private
     * @param {MouseEvent} ev
     * The method to open quick article search and if necessary apply changes to the parent field_html / attachments
    */
    onOpenKnowSystem: async function() {
        // import here since on website they are not available
        import dialogs from "web.view_dialogs";
        import Context from "web.Context";
        var self = this,
            parentField = this.getParent(),
            resModel = parentField.record.data["model"],
            restoreSelection = preserveCursor(this.odooEditor.document);
        if (this.options.knowSystemOptionKey == "activity") {
            resModel = parentField.record.data["res_model"];
        };
        var defaultTags = await rpc.query({
            model: "knowsystem.tag",
            method: "action_return_tags_for_document",
            args: [resModel, [parseInt(parentField.record.data["res_id"])]],
        });
        var KnowSystemContext = {
            default_tag_ids: defaultTags,
            default_no_selection: false,
        };
        var context = new Context(parentField.record.context, KnowSystemContext).eval();
        var knowSystemButtons = [
            {
                text: (_lt("Update Body")),
                classes: "btn-primary",
                click: function () {
                    dialog._save().then(function() {
                        restoreSelection();
                        parentField._onApplyArticleAction(dialog, "add_to_body").then(function (insertedBlock) {
                            self.odooEditor.execCommand("insertHTML", insertedBlock)
                        });
                    });
                },
            },
            {
                text: (_lt("Share URL")),
                classes: "btn-primary",
                click: function () {
                    dialog._save().then(function() {
                        restoreSelection();
                        parentField._onApplyArticleAction(dialog, "share_url", restoreSelection).then(function (insertedBlock) {
                            self.odooEditor.execCommand("insertHTML", insertedBlock)
                        });
                    });
                },
            },
        ];
        if (this.options.knowSystemOptionKey == "composer") {
            knowSystemButtons.push(            {
                text: (_lt("Attach PDF")),
                classes: "btn-primary",
                click: function () {
                    dialog._save().then(function() {
                        restoreSelection();
                        parentField._onApplyArticleAction(dialog, "add_pdf");
                    });
                },
            })
        }
        knowSystemButtons.push({
            text: (_lt("Close")),
            classes: "btn-secondary o_form_button_cancel",
            close: true,
        })
        var dialog = new dialogs.FormViewDialog(parentField, {
            res_model: "article.search",
            title: _lt("Articles quick search"),
            context: context,
            readonly: false,
            shouldSaveLocally: false,
            buttons: knowSystemButtons,
        });
        dialog.on("closed", this, function () {
            if (dialog.destroyAction !== "save") {
                restoreSelection();
            };
        });
        dialog.open();
    },
});
