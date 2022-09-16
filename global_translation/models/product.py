from googletrans import Translator
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
import re


class ProductProduct(models.Model):
    _inherit = 'product.product'

    translated_product = fields.Char('Translated Product Name')

    def write(self, vals):
        if vals.get('translated_product'):
            translator = Translator()
            translations = translator.translate(vals['translated_product'], dest='en')
            vals['name'] = translations.text
            # print(translator.translate(vals['product_in_arabic'],dest='en'))

        elif vals.get('name'):
            translator = Translator()
            translations = translator.translate(vals['name'], dest=self.env.user.lang)
            # for translation in translations:
            vals['translated_product'] = translations.text

        return super(ProductProduct, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('translated_product'):
            translator = Translator()
            translations = translator.translate(vals['translated_product'], dest='en')
            vals['name'] = translations.text

        elif vals.get('name'):
            translator = Translator()

            translations = translator.translate(vals['name'], dest=self.env.user.lang)
            # for translation in translations:
            vals['translated_product'] = translations.text

        return super(ProductProduct, self).create(vals)

    def name_get(self):
        # TDE: this could be cleaned a bit I think

        def _name_get(d):
            name = d.get('name', '')
            translated_product = d.get('translated_product', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if code:
                name = '[%s] %s/%s' % (code, name, translated_product)
            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []
        company_id = self.env.context.get('company_id')

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []

        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        self.sudo().read(['name', 'default_code', 'product_tmpl_id'], load=False)

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product in self.sudo():
            variant = product.product_template_attribute_value_ids._get_combination_name()

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
                # Filter out sellers based on the company. This is done afterwards for a better
                # code readability. At this point, only a few sellers should remain, so it should
                # not be a performance issue.
                if company_id:
                    sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                            variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                        'translated_product': product.translated_product,
                    }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                    'translated_product': product.translated_product,
                }
                result.append(_name_get(mydict))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if operator in positive_operators:
                product_ids = self._search([('default_code', '=', name)] + args, limit=limit,
                                           access_rights_uid=name_get_uid)
                if not product_ids:
                    product_ids = self._search([('barcode', '=', name)] + args, limit=limit,
                                               access_rights_uid=name_get_uid)
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                product_ids = self._search(args + [('default_code', operator, name)], limit=limit)
                if not limit or len(product_ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(
                        args + ['&', '|', ('translated_product', operator, name), ('name', operator, name),
                                ('id', 'not in', product_ids)],
                        limit=limit2, access_rights_uid=name_get_uid)
                    product_ids.extend(product2_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                product_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = self._search([('default_code', '=', res.group(2))] + args, limit=limit,
                                               access_rights_uid=name_get_uid)
            # still no results, partner in context: search on supplier info as last hope to find something
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)], access_rights_uid=name_get_uid)
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit,
                                               access_rights_uid=name_get_uid)
        else:
            product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(product_ids).with_user(name_get_uid))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    translated_product = fields.Char('Translated Product Name')

    def write(self, vals):
        if vals.get('translated_product'):
            translator = Translator()
            translations = translator.translate(vals['translated_product'], dest='en')
            vals['name'] = translations.text
            # print(translator.translate(vals['product_in_arabic'],dest='en'))

        elif vals.get('name'):
            translator = Translator()
            translations = translator.translate(vals['name'], dest=self.env.user.lang)
            # for translation in translations:
            vals['translated_product'] = translations.text

        return super(ProductTemplate, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('translated_product'):
            translator = Translator()
            translations = translator.translate(vals['translated_product'], dest='en')
            vals['name'] = translations.text
            # print(translator.translate(vals['product_in_arabic'],dest='en'))

        elif vals.get('name'):
            translator = Translator()
            translations = translator.translate(vals['name'], dest=self.env.user.lang)
            # for translation in translations:
            vals['translated_product'] = translations.text

        return super(ProductTemplate, self).create(vals)

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['name', 'default_code', 'translated_product'])
        return [(template.id, '%s%s' % (template.default_code and '[%s] ' % template.default_code or '',
                                        template.name + '/' + str(
                                            template.translated_product and template.translated_product or template.name)))
                for template in self]
