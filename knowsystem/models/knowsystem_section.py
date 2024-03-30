# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

MAXSECTIONSIZE = 150
MAXARTICLESIZE = 125

class knowsystem_section(models.Model):
    """
    The model to structure articles in sections and subsections
    """
    _name = "knowsystem.section"
    _inherit = ["knowsystem.node"]
    _description = "Section"

    def _compute_has_right_to(self):
        """
        Compute method for has_right_to

        Methods:
         * _get_all_access_sections
        """
        current_user = self.env.user
        available_sections = self._get_all_access_sections("user_group_ids")
        for section in self.sudo():
            section.has_right_to = section.id in available_sections and [(6, 0, [current_user.id])] or False

    def _compute_has_edit_right_to(self):
        """
        Compute method for has_edit_right_to

        Methods:
         * _get_all_access_sections
        """
        current_user = self.env.user
        available_sections = self._get_all_access_sections("edit_user_group_ids")
        for section in self.sudo():
            section.has_edit_right_to = section.id in available_sections and [(6, 0, [current_user.id])] or False

    def search_has_right_to(self, operator, value):
        """
        Search method for has_right_to

        Methods:
         * _get_search_access_groups
        """
        return self._get_search_access_groups(value, "user_group_ids")

    def search_has_edit_right_to(self, operator, value):
        """
        Search method for has_edit_right_to

        Methods:
         * _get_search_access_groups
        """
        return self._get_search_access_groups(value, "edit_user_group_ids")

    name = fields.Char(
        string="Section Title",
        required=True,
        translate=False,
    )
    description = fields.Html(
        string="Section Description",
        translate=False,
    )
    parent_id = fields.Many2one(
        "knowsystem.section",
        string="Parent Section",
    )
    child_ids = fields.One2many(
        "knowsystem.section",
        "parent_id",
        string="Sub Sections"
    )
    article_ids = fields.One2many(
        "knowsystem.article",
        "section_id",
        string="Articles",
    )
    user_group_ids = fields.Many2many(
        "res.groups",
        "res_groups_knowsystem_section_rel_table",
        "res_groups_id",
        "knowsystem_section_id",
        string="Read access groups",
        help="""If selected, a user should belong to one of those groups to access this section and ALL ITS ARTICLES
Besides, a user should have rights to the parent sections hierarchically
The exceptions are (1) KnowSystem administrators; (2) Authors of the articles""",
    )
    has_right_to = fields.Many2many(
        "res.users",
        "res_user_knowsystem_section_rel_table_access",
        "res_user_id",
        "knowsystem_section_id",
        string="Current user has right to this section",
        compute=_compute_has_right_to,
        search="search_has_right_to",
    )
    edit_user_group_ids = fields.Many2many(
        "res.groups",
        "res_groups_knowsystem_section_edit_rel_table",
        "res_groups_id",
        "knowsystem_section_id",
        string="Update access groups",
        help="""If selected, a user should belong to one of the groups to update this section and ALL ITS ARTICLES
Besides, a user should have rights to the parent sections hierarchically
The exceptions is KnowSystem administrators who can edit any section and article""",
    )
    has_edit_right_to = fields.Many2many(
        "res.users",
        "res_user_knowsystem_section_rel_table_access_edit",
        "res_user_id",
        "knowsystem_section_id",
        string="Current user has update right to this section",
        compute=_compute_has_edit_right_to,
        search="search_has_edit_right_to",
    )

    _order = "sequence, id"

    def return_edit_form(self):
        """
        The method to return tag editing form
        """
        view_id = self.sudo().env.ref("knowsystem.knowsystem_section_view_form").id
        return view_id

    def _get_all_access_sections(self, field_group):
        """
        The method to calculate sections available for this user

        Args:
         * field_group - char - the field from where to get groups. It is either "user_group_ids" (read) or 
           "edit_user_group_ids" (create, write, delete)

        Returns:
         * knowsystem.section recordset
        """
        current_user = self.env.user
        groups = current_user.groups_id
        self = self.sudo()
        sections = self.search([("parent_id", "=", False)])
        available_sections = []
        for section in sections:
            available_sections += section._check_rights_recursively(field_group=field_group, groups=groups)
        return available_sections

    def _get_search_access_groups(self, value, field_group):
        """
        The method to calculate domain to search sections available for this group

        Args:
         * value - inserted search value
         * field_group - char - the field from where to get groups. It is either "user_group_ids" (read) or 
           "edit_user_group_ids" (create, write, delete)

        Returns:
         * list - RPR representation of domain to search sections
        """
        current_user = self.env["res.users"].browse(value)
        self.env["res.users"].invalidate_cache(ids=[current_user.id])
        groups = current_user.groups_id
        self = self.sudo()
        sections = self.search([
            ("parent_id", "=", False),
            "|",
                ("active", "=", True),  
                ("active", "=", False),
        ])
        res = []
        for section in sections:
            res += section._check_rights_recursively(field_group=field_group, groups=groups)
        return [("id", "in", res)]

    def _check_rights_recursively(self, field_group, groups):
        """
        The method to check rights for this section and go to childs for the next check

        Principles:
         * a user should belong at least to a single group to have rights for this section
         * if the section doesn't have groups --> it is global, everybody has rights for it
         * if a user doesn't have an access to this section --> this user doesn't have rights for all its children

        Args:
         * field_group - char - the field from where to get groups. It is either "user_group_ids" (read) or 
          "edit_user_group_ids" (create, write, delete)
         * groups - res.group recordset

        Returns:
         * list of ints - section ids

        Extra info:
         * Expected Singleton
        """
        self.ensure_one()
        res = []
        section_groups = self[field_group]
        if not section_groups or (groups & section_groups):
            res.append(self.id)
            for child in self.child_ids:
                res += child._check_rights_recursively(field_group=field_group, groups=groups)
        return res

    @api.model
    def action_check_option(self, ttype):
        """
        The method to check whether a quick link should be placed

        Args:
         * ttype - "composer", "form"

        Returns:
         * bool
        """
        Config = self.env["ir.config_parameter"].sudo()
        need = False
        if ttype == "composer":
            need = safe_eval(Config.get_param("knowsystem_composer_option", "False"))
        elif ttype == "form":
            need = safe_eval(Config.get_param("knowsystem_models_option", "False"))
        elif ttype == "activity":
            need = safe_eval(Config.get_param("knowsystem_activity_option", "False"))
        return need
