# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class PropertyDetails(models.Model):
    _name = 'property.details'
    _description = 'Property Details and for registration new Property'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Parent Property Field
    is_parent_property = fields.Boolean(string='Parent Property')
    parent_property_id = fields.Many2one('parent.property', string='Property')
    parent_amenities_ids = fields.Many2many(related='parent_property_id.amenities_ids')
    parent_specification_ids = fields.Many2many(related='parent_property_id.property_specification_ids')
    parent_landlord_id = fields.Many2one(related='parent_property_id.landlord_id', string='Landlord')
    parent_airport = fields.Char(related='parent_property_id.airport', string='Airport')
    parent_national_highway = fields.Char(related='parent_property_id.national_highway', string='National Highway')
    parent_metro_station = fields.Char(related='parent_property_id.metro_station', string='Metro Station')
    parent_metro_city = fields.Char(related='parent_property_id.metro_city', string='Metro City')
    # Address
    parent_zip = fields.Char(related='parent_property_id.zip', string='Pin Code')
    parent_street = fields.Char(related='parent_property_id.street', string='Street1')
    parent_street2 = fields.Char(related='parent_property_id.street2', string='Street2')
    parent_city = fields.Char(related='parent_property_id.city', string='City')
    parent_country_id = fields.Many2one(related='parent_property_id.country_id', string='Country')
    parent_state_id = fields.Many2one(related='parent_property_id.state_id', string='State')
    parent_website = fields.Char(related='parent_property_id.website', string='Website')

    # Common Field

    property_seq = fields.Char(string='Sequence', required=True, readonly=True, default=lambda self: ('New'))
    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string='Image')
    type = fields.Selection([('land', 'Land'),
                             ('residential', 'Residential'),
                             ('commercial', 'Commercial'),
                             ('industrial', 'Industrial')
                             ], string='Property Type', required=True)
    stage = fields.Selection([('draft', 'Draft'),
                              ('available', 'Available'),
                              ('booked', 'Booked'),
                              ('on_lease', 'On Lease'),
                              ('sale', 'Sale'),
                              ('sold', 'Sold')],
                             string='Stage', default='draft', required=True, readonly=1)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    longitude = fields.Char(string='Longitude')
    latitude = fields.Char(string='Latitude')
    sale_lease = fields.Selection([('for_sale', 'For Sale'),
                                   ('for_tenancy', 'For Tenancy')],
                                  string='Price/Rent', default='for_tenancy', required=True)
    sale_price = fields.Monetary(string='Sale Price')
    tenancy_price = fields.Monetary(string='Rent/Month')
    token_amount = fields.Monetary(string='Token Amount')
    website = fields.Char(string='Website')
    sold_invoice_id = fields.Many2one('account.move', string='Sold Invoice', readonly=True)
    sold_invoice_state = fields.Boolean(string='Sold Invoice State')
    construct_year = fields.Char(string="Construct Year", size=4)
    buying_year = fields.Char(string="Buying Year", size=4)
    property_licence_no = fields.Char(string='Licence No.')
    address = fields.Char()

    # Address
    zip = fields.Char(string='Pin Code', size=6)
    street = fields.Char(string='Street1')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one(
        "res.country.state", string='State', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")

    # Nearby Connectivity
    airport = fields.Char(string='Airport')
    national_highway = fields.Char(string='National Highway')
    metro_station = fields.Char(string='Metro Station')
    metro_city = fields.Char(string='Metro City')

    # Related Field
    landlord_id = fields.Many2one('res.partner', string='LandLord', domain=[('user_type', '=', 'landlord')])
    tenancy_ids = fields.One2many('tenancy.details', 'property_id', string='History')
    broker_ids = fields.One2many('tenancy.details', 'property_id', string='Broker',
                                 domain=[('is_any_broker', '=', True)])
    amenities_ids = fields.Many2many('property.amenities', string='Amenities')
    property_specification_ids = fields.Many2many('property.specification', string='Specification')
    property_vendor_ids = fields.One2many('property.vendor', 'property_id', string='Vendor Details')
    certificate_ids = fields.One2many('property.certificate', 'property_id', string='Certificate')
    maintenance_ids = fields.One2many('maintenance.request', 'property_id', string='Maintenance History')
    floreplan_ids = fields.One2many('floor.plan', 'property_id', string='FlorePlan')
    property_images_ids = fields.One2many('property.images', 'property_id', string='Images')
    tag_ids = fields.Many2many('property.tag', string='Tags')

    # Residential
    residence_type = fields.Selection([('apartment', 'Apartment'),
                                       ('bungalow', 'Bungalow'),
                                       ('vila', 'Vila'),
                                       ('raw_house', 'Raw House'),
                                       ('duplex', 'Duplex House'),
                                       ('single_studio', 'Single Studio')],
                                      string='Type of Residence')
    total_floor = fields.Integer(string='Total Floor', default='4')
    towers = fields.Boolean(string='Tower Building')
    no_of_towers = fields.Integer(string='No. of Towers')
    furnishing = fields.Selection([('fully_furnished', 'Fully Furnished'),
                                   ('only_kitchen', 'Only Kitchen Furnished'),
                                   ('only_bed', 'Only BedRoom Furnished'),
                                   ('not_furnished', 'Not Furnished'),
                                   ], string='Furnishing', default='fully_furnished')
    bed = fields.Integer(string='Bedroom', default=1)
    bathroom = fields.Integer(string='Bathroom', default=1)
    parking = fields.Integer(string='Parking', default=1)
    facing = fields.Selection([('N', 'North(N)'),
                               ('E', 'East(E)'),
                               ('S', 'South(S)'),
                               ('W', 'West(W)'),
                               ('NE', 'North-East(NE)'),
                               ('SE', 'South-East(SE)'),
                               ('SW', 'South-West(SW)'),
                               ('NW', 'North-West(NW)'),
                               ],
                              string='Facing', default='N')
    room_no = fields.Char(string='Flat No./House No.')
    floor = fields.Integer(string='Floor')
    total_square_ft = fields.Char(string='Total Square Feet')
    usable_square_ft = fields.Char(string='Usable Square Feet')
    facilities = fields.Text(string='Facilities')

    # Land
    land_name = fields.Char(string='Land Name')
    area_hector = fields.Char(string='Area in Hector')
    land_facilities = fields.Text(string='Facility')

    # Commercial
    commercial_name = fields.Char(string='Commercial/Shop Name')
    commercial_type = fields.Selection([('full_commercial', 'Full Commercial'),
                                        ('shops', 'Shops'),
                                        ('big_hall', 'Big Hall')],
                                       string='Commercial Type')
    used_for = fields.Selection([('offices', 'Offices'),
                                 (' retail_stores', ' Retail Stores'),
                                 ('shopping_centres', 'Shopping Centres'),
                                 ('hotels', 'Hotels'),
                                 ('restaurants', 'Restaurants'),
                                 ('pubs', 'Pubs'),
                                 ('cafes', 'Cafes'),
                                 ('sport_facilities', 'Sport Facilities'),
                                 ('medical_centres', 'Medical Centres'),
                                 ('hospitals', 'Hospitals'),
                                 ('nursing_homes', 'Nursing Homes'),
                                 ('other', 'Other Use')
                                 ],
                                string='Used For')
    floor_commercial = fields.Integer(string='Floor ')
    total_floor_commercial = fields.Char(string='Total Floor ')
    commercial_facilities = fields.Text(string='Facilities ')
    other_use = fields.Char(string='Other Use')

    # Industrial
    industry_name = fields.Char(string='Industry Name')
    industry_location = fields.Selection([('inside', 'Inside City'),
                                          ('outside', 'Outside City'),
                                          ],
                                         string='Location')
    industrial_used_for = fields.Selection([('company', 'Company'),
                                            ('warehouses', 'Warehouses'),
                                            ('factories', 'Factories'),
                                            ('other', 'Other')],
                                           string='Usage')
    other_usages = fields.Char(string='Usages ')
    industrial_facilities = fields.Text(string='Facilities  ')

    # Measurement Details
    room_measurement_ids = fields.One2many('property.room.measurement', 'room_measurement_id',
                                           string='Room Measurement')
    commercial_measurement_ids = fields.One2many('property.commercial.measurement', 'commercial_measurement_id',
                                                 string='Commercial Measurement')
    industrial_measurement_ids = fields.One2many('property.industrial.measurement', 'industrial_measurement_id',
                                                 string='Industrial Measurement')
    total_room_measure = fields.Integer(string='Total Square feet', compute='_compute_room_measure')
    total_commercial_measure = fields.Integer(string='Total Square feet', compute='_compute_commercial_measure')

    total_industrial_measure = fields.Integer(string='Total Square feet', compute='_compute_industrial_measure')

    @api.depends('room_measurement_ids')
    def _compute_room_measure(self):
        for rec in self:
            total = 0
            if rec.room_measurement_ids:
                for data in rec.room_measurement_ids:
                    total = total + data.carpet_area
                    rec.total_room_measure = total
            else:
                rec.total_room_measure = 0

    @api.depends('commercial_measurement_ids')
    def _compute_commercial_measure(self):
        for rec in self:
            total = 0
            if rec.commercial_measurement_ids:
                for data in rec.commercial_measurement_ids:
                    total = total + data.carpet_area
                    rec.total_commercial_measure = total
            else:
                rec.total_commercial_measure = 0

    @api.depends('industrial_measurement_ids')
    def _compute_industrial_measure(self):
        for rec in self:
            total = 0
            if rec.industrial_measurement_ids:
                for data in rec.industrial_measurement_ids:
                    total = total + data.carpet_area
                    rec.total_industrial_measure = total
            else:
                rec.total_industrial_measure = 0

    # Smart Button Count
    document_count = fields.Integer(string='Document Count', compute='_compute_document_count')
    request_count = fields.Integer(string='Request Count', compute='_compute_request_count')

    # Sequence Create
    @api.model
    def create(self, vals):
        if vals.get('property_seq', ('New')) == ('New'):
            vals['property_seq'] = self.env['ir.sequence'].next_by_code(
                'property.details') or ('New')
        res = super(PropertyDetails, self).create(vals)
        return res

    def name_get(self):
        data = []
        for rec in self:
            if rec.is_parent_property:
                if rec.type == 'land':
                    data.append((rec.id, '%s - %s - Land' % (rec.name, rec.parent_property_id.name)))
                elif rec.type == 'residential':
                    data.append((rec.id, '%s - %s - Residential' % (rec.name, rec.parent_property_id.name)))
                elif rec.type == 'commercial':
                    data.append((rec.id, '%s - %s - Commercial' % (rec.name, rec.parent_property_id.name)))
                elif rec.type == 'industrial':
                    data.append((rec.id, '%s - %s - Industrial' % (rec.name, rec.parent_property_id.name)))
                else:
                    data = []
            else:
                if rec.type == 'land':
                    data.append((rec.id, '%s - Land' % rec.name))
                elif rec.type == 'residential':
                    data.append((rec.id, '%s - Residential' % rec.name))
                elif rec.type == 'commercial':
                    data.append((rec.id, '%s - Commercial' % rec.name))
                elif rec.type == 'industrial':
                    data.append((rec.id, '%s - Industrial' % rec.name))
                else:
                    data = []
        return data

    # Buttons
    def action_in_available(self):
        for rec in self:
            rec.stage = 'available'
            rec.sale_lease = 'for_tenancy'
        return True

    def action_in_booked(self):
        for rec in self:
            rec.stage = 'booked'
        return True

    def action_sold(self):
        for rec in self:
            rec.stage = 'sold'
        return True

    def action_in_sale(self):
        for rec in self:
            rec.stage = 'sale'
            rec.sale_lease = 'for_sale'
        return True

    # Smart Button
    def _compute_document_count(self):
        for rec in self:
            document_count = self.env['property.documents'].search_count([('property_id', '=', rec.id)])
            rec.document_count = document_count
        return True

    def _compute_request_count(self):
        for rec in self:
            request_count = self.env['maintenance.request'].search_count([('property_id', '=', rec.id)])
            rec.request_count = request_count
        return True

    def action_maintenance_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request',
            'res_model': 'maintenance.request',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
            'view_mode': 'kanban,tree',
            'target': 'current'
        }

    def action_property_document(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Document',
            'res_model': 'property.documents',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
            'view_mode': 'tree',
            'target': 'current'
        }

    @api.model
    def get_property_stats(self):
        # Property Stages
        avail_property = self.env['property.details'].sudo().search_count([('stage', '=', 'available')])
        booked_property = self.env['property.details'].sudo().search_count([('stage', '=', 'booked')])
        lease_property = self.env['property.details'].sudo().search_count([('stage', '=', 'on_lease')])
        sale_property = self.env['property.details'].sudo().search_count([('stage', '=', 'sale')])
        sold_property = self.env['property.details'].sudo().search_count([('stage', '=', 'sold')])
        total_property = self.env['property.details'].sudo().search_count([])
        currency_symbol = self.env['res.currency'].search([]).mapped('symbol')
        draft_contract = self.env['tenancy.details'].sudo().search_count([('contract_type', '=', 'new_contract')])
        running_contract = self.env['tenancy.details'].sudo().search_count([('contract_type', '=', 'running_contract')])
        expire_contract = self.env['tenancy.details'].sudo().search_count([('contract_type', '=', 'expire_contract')])
        booked = self.env['property.vendor'].sudo().search_count([('stage', '=', 'booked')])
        sale_sold = self.env['property.vendor'].sudo().search_count([('stage', '=', 'sold')])

        # Total Tenancy and Sold Information
        sold_total = self.env['property.vendor'].search([('stage', '=', 'sold')]).mapped('sale_price')
        total = 0
        for price in sold_total:
            total = total + price
        total_str = str(total)

        full_tenancy_total = self.env['rent.invoice'].search(
            ['|', ('type', '=', 'rent'), ('type', '=', 'full_rent')]).mapped('amount')
        full_rent = self.env['rent.invoice'].search([]).mapped('rent_amount')
        final = full_tenancy_total + full_rent
        final_rent = 0
        for rent in final:
            final_rent = final_rent + rent
        final_rent_str = str(final_rent)

        data = {
            'avail_property': avail_property,
            'booked_property': booked_property,
            'lease_property': lease_property,
            'sale_property': sale_property,
            'sold_property': sold_property,
            'total_property': total_property,
            'sold_total': total_str + ' ' + currency_symbol[0] if currency_symbol else "",
            'rent_total': final_rent_str + ' ' + currency_symbol[0] if currency_symbol else "",
            'draft_contract': draft_contract,
            'running_contract': running_contract,
            'expire_contract': expire_contract,
            'booked': booked,
            'sale_sold': sale_sold,
        }
        return data

    def action_gmap_location(self):
        if self.longitude and self.latitude:
            longitude = self.longitude
            latitude = self.latitude
            http_url = 'https://maps.google.com/maps?q=loc:' + latitude + ',' + longitude
            return {
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': http_url,
            }
        else:
            raise ValidationError("! Enter Proper Longitude and Latitude Values")


# Room Measurement
class PropertyRoomMeasurement(models.Model):
    _name = 'property.room.measurement'
    _description = 'Room Property Measurement Details'

    type_room = fields.Selection([('hall', 'Hall'),
                                  ('bed_room', 'Bed Room'),
                                  ('kitchen', 'Kitchen'),
                                  ('drawing_room', 'Drawing Room'),
                                  ('bathroom', 'Bathroom'),
                                  ('store_room', 'Store Room'),
                                  ('balcony', 'Balcony'),
                                  ('wash_area', 'Wash Area'),
                                  ],
                                 string='House Section')
    length = fields.Integer(string='Length(ft)')
    width = fields.Integer(string='Width(ft)')
    height = fields.Integer(string='Height(ft)')
    carpet_area = fields.Integer(string='Carpet Area(ft²)', compute='_compute_carpet_area')
    measure = fields.Char(string='ft²', default='ft²', readonly=1)
    room_measurement_id = fields.Many2one('property.details', string='Room Details')

    @api.depends('length', 'width')
    def _compute_carpet_area(self):
        for rec in self:
            if rec.length and rec.width:
                total = rec.length * rec.width
                rec.carpet_area = total
            else:
                rec.carpet_area = 0


# Commercial Measurement
class PropertyCommercialMeasurement(models.Model):
    _name = 'property.commercial.measurement'
    _description = 'Commercial Property Measurement Details'

    shops = fields.Char(string='Shops')
    length = fields.Integer(string='Length(ft)')
    width = fields.Integer(string='Width(ft)')
    height = fields.Integer(string='Height(ft)')
    carpet_area = fields.Integer(string='Area(ft²)', compute='_compute_carpet_area')
    measure = fields.Char(string='ft²', default='ft²', readonly=1)
    commercial_measurement_id = fields.Many2one('property.details', string='Commercial Details')

    @api.depends('length', 'width')
    def _compute_carpet_area(self):
        for rec in self:
            if rec.length and rec.width:
                total = rec.length * rec.width
                rec.carpet_area = total
            else:
                rec.carpet_area = 0


class PropertyIndustrialMeasurement(models.Model):
    _name = 'property.industrial.measurement'
    _description = 'Industrial Property Measurement Details'

    asset = fields.Char(string='industrial Asset')
    length = fields.Integer(string='Length(ft)')
    width = fields.Integer(string='Width(ft)')
    height = fields.Integer(string='Height(ft)')
    carpet_area = fields.Integer(string='Area(ft²)', compute='_compute_carpet_area')
    measure = fields.Char(string='ft²', default='ft²', readonly=1)
    industrial_measurement_id = fields.Many2one('property.details', string='Industrial Details')

    @api.depends('length', 'width')
    def _compute_carpet_area(self):
        for rec in self:
            if rec.length and rec.width:
                total = rec.length * rec.width
                rec.carpet_area = total
            else:
                rec.carpet_area = 0


class PropertyDocuments(models.Model):
    _name = 'property.documents'
    _description = 'Document related to Property'
    _rec_name = 'doc_type'

    property_id = fields.Many2one('property.details', string='Property Name', readonly=True)
    document_date = fields.Date(string='Date', default=fields.Date.today())
    doc_type = fields.Selection([('photos', 'Photo'),
                                 ('brochure', 'Brochure'),
                                 ('certificate', 'Certificate'),
                                 ('insurance_certificate', 'Insurance Certificate'),
                                 ('utilities_insurance', 'Utilities Certificate')],
                                string='Document Type', required=True)
    document = fields.Binary(string='Documents', required=True)
    file_name = fields.Char(string='File Name')


class PropertyAmenities(models.Model):
    _name = 'property.amenities'
    _description = 'Details About Property Amenities'
    _rec_name = 'title'

    image = fields.Binary(string='Image')
    title = fields.Char(string='Title')


class PropertySpecification(models.Model):
    _name = 'property.specification'
    _description = 'Details About Property Specification'
    _rec_name = 'title'

    image = fields.Image(string='Image')
    title = fields.Char(string='Title')
    description_line1 = fields.Char(string='Description')
    description_line2 = fields.Char(string='Description Line 2')
    description_line3 = fields.Char(string='Description Line 3')


class CertificateType(models.Model):
    _name = 'certificate.type'
    _description = 'Type Of Certificate'
    _rec_name = 'type'

    type = fields.Char(string='Type')


class PropertyCertificate(models.Model):
    _name = 'property.certificate'
    _description = 'Property Related All Certificate'
    _rec_name = 'type_id'

    type_id = fields.Many2one('certificate.type', string='Type')
    expiry_date = fields.Date(string='Expiry Date')
    responsible = fields.Char(string='Responsible')
    note = fields.Char(string='Note')
    property_id = fields.Many2one('property.details', string='Property')


class ParentProperty(models.Model):
    _name = 'parent.property'
    _description = 'Parent Property Details'

    name = fields.Char(string='Name')
    image = fields.Binary(string='Image')
    amenities_ids = fields.Many2many('property.amenities', string='Amenities')
    property_specification_ids = fields.Many2many('property.specification', string='Specification')
    zip = fields.Char(string='Pin Code', size=6)
    street = fields.Char(string='Street1')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one(
        "res.country.state", string='State', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    landlord_id = fields.Many2one('res.partner', string='LandLord', domain=[('user_type', '=', 'landlord')])
    website = fields.Char(string='Website')
    airport = fields.Char(string='Airport')
    national_highway = fields.Char(string='National Highway')
    metro_station = fields.Char(string='Metro Station')
    metro_city = fields.Char(string='Metro City')


class FloorPlan(models.Model):
    _name = 'floor.plan'
    _description = 'Details About Floor Plan'

    image = fields.Image(string='Image')
    title = fields.Char(string='Title')
    property_id = fields.Many2one('property.details', string='Property')


class PropertyImages(models.Model):
    _name = 'property.images'
    _description = 'Property Images'

    property_id = fields.Many2one('property.details', string='Property Name', readonly=True)
    title = fields.Char(string='Title')
    image = fields.Image(string='Images')


class PropertyTag(models.Model):
    _name = 'property.tag'
    _description = 'Property Tags'
    _rec_name = 'title'

    title = fields.Char(string='Title')
    color = fields.Integer(string='Color')
