# -*- coding: utf-8 -*-

from lxml import html
from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.addons.http_routing.models.ir_http import slug, slugify_one
from odoo.tools.translate import html_translate


class documentation_section(models.Model):
    """
    The model to combine articles into a documentation section
    """
    _name = "documentation.section"
    _inherit = ["mail.thread", "mail.activity.mixin", "website.published.mixin", "website.seo.metadata", 
                "image.mixin", "portal.mixin",]
    _description = "Documentation Section"

    @api.model
    def _max_header_to_parse_selection(self):
        """
        Method to generate header 
        """
        return [(str(header), str(header)) for header in range(0, 7)]

    def _compute_website_url(self):
        """
        Overwritting the compute method for portal_url to pass our pathes

        Methods:
         * super
        """
        super(documentation_section, self)._compute_website_url()
        for section in self:
            section.website_url = u"/docs/{}".format(slug(section))

    def _compute_access_url(self):
        """
        Overwritting the compute method for access_url to pass our pathes

        Methods:
         * super
        """
        for section in self:
            section.access_url = section.website_url

    def _compute_portal_has_right_to(self):
        """
        Compute method for portal_has_right_to

        To-do:
         * think of making that context dependentant
        """
        current_user = self.env.user
        parent = current_user.partner_id
        tag_ids = self.env["knowsystem.tag"]
        while parent:
            tag_ids += self.env["knowsystem.tag"].search([("partner_ids", "in", parent.ids)])
            parent = parent.parent_id
        tag_inlc_childs = self.env["knowsystem.tag"].search([("id", "child_of", tag_ids.ids)])
        section_ids = tag_inlc_childs.mapped("doc_ids")
        for section in self:
            section.portal_has_right_to = section in section_ids and [(6, 0, [current_user.id])] or False

    def search_portal_has_right_to(self, operator, value):
        """
        Search method for portal_has_right_to
        """
        current_user = self.env["res.users"].browse(value)
        self.env["res.users"].invalidate_cache(ids=[current_user.id])       
        parent = current_user.partner_id
        tag_ids = self.env["knowsystem.tag"]
        while parent:
            tag_ids += self.env["knowsystem.tag"].search([
                ("partner_ids", "in", parent.ids)
            ])
            parent = parent.parent_id
        tag_inlc_childs = self.env["knowsystem.tag"].search([
            ("id", "child_of", tag_ids.ids)
        ])
        doc_ids = tag_inlc_childs.mapped("doc_ids")
        return [("id", "in", doc_ids.ids)]

    @api.model
    def _read_group_category_id(self, stages, domain, order):
        """
        The method to open in kanban even empty columns
        """
        return self.env["documentation.category"].search([])

    name = fields.Char(
        string="Title",
        required=True,
        translate=True,
    )
    category_id = fields.Many2one(
        "documentation.category",
        string="Category",
        required=True,
        group_expand="_read_group_category_id",
    )
    article_ids = fields.One2many(
        "documentation.section.article",
        "documentation_id",
        string="Articles",
    )
    short_description = fields.Text(string="Preview Text", translate=True,)
    introduction = fields.Html(string="Introduction", translate=html_translate,)
    footer = fields.Html(string="Footer", translate=html_translate,)
    max_header_to_parse = fields.Selection(
        _max_header_to_parse_selection,
        string="Header Level for Navigation",
        help="""
            Defines article inline headers should be parsed for navigation (table of contents)
            * '0' - articles content headers would not be added to the navigation panel
            * '3' - headers till the third level (h1, h2, h3) would be parsed
            * '6' - h1, h2, h3, h4, h5, h6 article headers would be added to the navigation panel
        """,
        default="3",
    )
    tag_ids = fields.Many2many(
        "knowsystem.tag",
        "knowsystem_tag_documentation_section_r_table",
        "knowsystem_tag_r_id",
        "documentation_section_r_id",
        string="Tags",
        copy=True,
    )
    portal_has_right_to = fields.Many2many(
        "res.users",
        "res_user_knowsystem_article_rel_table_portal",
        "res_users_id",
        "knowsystem_article_id",
        string="Portal right",
        compute=_compute_portal_has_right_to,
        search="search_portal_has_right_to",
    )
    version_ids = fields.Many2many(
        "documentation.version",
        "documentation_version_documentation_section_rel_table",
        "documentation_version_rel_id",
        "documentation_section_rel_id",
        string="Versions",
    )
    sequence = fields.Integer(
        "Sequence",
        default=0,
        help="The lesser the closer to the top",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive",
    )
    color = fields.Integer(string="Color")

    _order = "sequence, id"

    def name_get(self):
        """
        Overloading the method to overcome controller access rights
        """
        if self.env.context.get("no_sudo_required") == "True":
            return super(documentation_section, self).name_get()
        else:
            return super(documentation_section, self.sudo()).name_get()

    def get_access_method(self, article, mode, website_id=False):
        """
        The method to check out security action for the article

        Args:
         * documentation.section.article object
         * mode - char: "read", "write", etc
         * website_id - website object

        Returns:
         * char - one of security action values

        Extra info:
         * Expected singleton
        """
        res = website_id.docu_default_security_action or "no_access"
        try:
            # user has the right for an article
            article.article_id.check_access_rights(mode)
            article.article_id.with_context(docu_builder=True).check_access_rule(mode)
            res = "sudo"
        except:
            res = article.security_action or res
        if not article.sudo().article_id.active:
            # not active articles are never shown
            res = "no_access"    
        return res    

    def return_add_to_documentation_wizard(self):
        """
        The method to return add to tourd view
        """
        view_id = self.sudo().env.ref("documentation_builder.add_to_documentation_form_view").id
        return view_id
    
    def return_form_view(self):
        """
        The method to open form of the documentation

        Returns:
         * action
        """
        action_id = self.sudo().env.ref("documentation_builder.documentation_section_action_form_only")
        action = action_id.read()[0]
        action["res_id"] = self.id
        return action

    def _prepare_content_and_toc(self, website_id, versioning_option, current_version):
        """
        The method to add anchors to articles and construct table of contents
        
        Args:
         * website_id - website object
         * versioning_option - bool - whether version is possible
         * current_version - int or False - currently selection version

        Methods:
         * get_access_method
         * action_get_published_name of knowsystem.article
         * _postprocess_description - for inheritance

        Returns:
         * tuple of
          ** list - of articles:
           *** article_id - knowsystem.article record
           *** security_mode - str - 'sudo' or 'warning'; ('no_access' is not shown)
           *** published_name - str (html of header with anchor inside)
           *** article_anchor - str - id of article under consideration
           *** description_arch - text - article body (with anchors inside)
          ** list (toc):
           *** level - int (8px for each header)
           *** id - str - referenced anchor
                *** text - TOC item
                *** parent - str - id of higher level header
                *** has_children - bool whether this TOC element has subentriesr
        """
        res_articles = []
        table_of_contents = []

        def prepare_anchor(article_id, title, header_level, header_index):
            """
            The method to prepared header anchor

            Args:
             * article_id - int - article ID
             * title - str - article header
             * header_level
             * header_index - int - unique index of a header in the article
            
            Returns:
             * tuple
              ** str - new header anchor
              ** dict for table of contents:
                *** level - str - ho, h1, ...
                *** id - string - referenced anchor
                *** text - TOC item
                *** parent - str - id of higher level header
                *** has_children - bool whether this TOC element has subentries
            """
            anchor_id = toc_dict = False
            if title:
                anchor_text = title and title[:150]
                anchor_id = "{}-{}-{}".format(slugify_one(anchor_text, 30), article_id, header_index)
                padding = int(header_level[1]) * 8
                parent_item = False
                if header_index and table_of_contents:
                    for prev in table_of_contents[::-1]:
                        if prev.get("level") < padding:
                            parent_item = prev.get("id")
                            prev.update({"has_children": True})
                            break
                toc_dict = {
                    "level": padding, 
                    "id": anchor_id, 
                    "text": anchor_text,
                    "parent": parent_item,
                    "has_children": False,
                }
            return anchor_id, toc_dict

        # define which headers are under consideration
        xpath_of_headers = ""
        header_level = int(self.max_header_to_parse or "0")
        if header_level:
            xpath_of_headers = "|".join(["//h{}".format(lev+1) for lev in range(header_level)])
        # go by all documentation section lines
        for doc_line in self.article_ids:
            doc_version_ids = doc_line.sudo().version_ids
            if versioning_option and doc_version_ids and current_version not in doc_version_ids.ids:
                # article does not suit the chosen version
                continue
            security_mode =  self.get_access_method(doc_line, "read", website_id)
            if security_mode == "no_access":
                # if no access, no need to parse an article
                continue
            article_id = doc_line.with_context(docu_builder=True).sudo().article_id
            article_int = article_id.id
            article_dict = {
                "article_id": article_id, 
                "security_mode": security_mode,
            }
            # parse article title and it to TOC
            article_name = article_id.action_get_published_name()
            anchor_id, toc_item = prepare_anchor(article_int, article_name, "h0", 0)
            if anchor_id:
                article_dict.update({
                    "published_name": Markup("<h2 id='{}' actheader='1'>{}</h2>".format(anchor_id, article_name)),
                    "article_anchor": anchor_id,
                })
                table_of_contents.append(toc_item)
            # go by each parsed body header (if body is shown), and parse that, and add it to TOC
            if security_mode == "sudo":
                parsed_description = html.fromstring(article_id.description_arch or "<div></div>")
                if xpath_of_headers:
                    abs_index = 1
                    for each_header in parsed_description.xpath(xpath_of_headers):
                        # need to get all tags text and remove excess spaces
                        node_text = "".join(each_header.itertext())
                        node_text = " ".join(node_text.split())
                        anchor_id, toc_item = prepare_anchor(article_int, node_text, each_header.tag, abs_index)
                        if anchor_id:
                            each_header.attrib["id"] = anchor_id
                            each_header.attrib["actheader"] = "1"
                            table_of_contents.append(toc_item)
                            abs_index += 1
                self._postprocess_article_content(parsed_description)
                # save final description
                article_description = html.tostring(parsed_description).decode("utf-8")
                if article_description.startswith("<div><p><br></p>"):
                    # remove default starting line
                    article_description = article_description[0:4] + article_description[15:]
                article_dict.update({"description_arch": Markup(article_description)})
            else:
                article_dict.update({"description_arch": ""})
            res_articles.append(article_dict)
        
        return res_articles, table_of_contents

    def _postprocess_article_content(self, parsed_description):
        """
        The method to undertake other actions to postprocess description before showing that
        Introduced for inheritance purposes

        Args:
         * parsed_description - lxml.html.HtmlElement
        """
        pass
