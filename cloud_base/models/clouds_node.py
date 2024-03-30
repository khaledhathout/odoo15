# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class clouds_node(models.AbstractModel):
    """
    This is the Abstract Model to manage jstree nodes
    It is used for tags
    """
    _name = "clouds.node"
    _description = "Clouds Node"
    _rec_names_search = ["complete_name"]

    @api.depends("name", "parent_id.name")
    def _compute_display_name(self):
        """
        Overloading to reflect id and model name
        """
        for node in self:
            names = []
            current = node
            while current:
                names.append(current.name or "")
                current = current.parent_id
            node.display_name = " / ".join(reversed(names))

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for node in self:
            if node.parent_id:
                node.complete_name = "%s / %s" % (node.parent_id.complete_name, node.name)
            else:
                node.complete_name = node.name

    @api.constrains("parent_id")
    def _check_node_recursion(self):
        """
        Constraint for recursion
        """
        if not self._check_recursion():
            raise ValidationError(_("It is not allowed to make recursions!"))
        return True

    def _inverse_active(self):
        """
        Inverse method for active. There 2 goals:
         1. If a parent is not active, we activate it. It recursively activate all its further parents
         2. Deacticate all children. It will invoke deactivation recursively of all children after
        """
        for node in self:
            if node.active:
                # 1
                if node.parent_id and not node.parent_id.active:
                    node.parent_id.active = True
            else:
                # 2
                node.child_ids.write({"active": False})

    name = fields.Char(string="Name", required=True, translate=False)
    complete_name = fields.Char("Complete Name", compute="_compute_complete_name", store=True, recursive=True)
    description = fields.Html(string="Description", translate=False)
    active = fields.Boolean(string="Active", default=True, inverse=_inverse_active)
    sequence = fields.Integer(string="Sequence", default=0)

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        """
        Re-write to add "copy" in the title
        """
        if default is None:
            default = {}
        if not default.get("name"):
            default["name"] = _("%s (copy)") % (self.name)
        return super(clouds_node, self).copy(default)
