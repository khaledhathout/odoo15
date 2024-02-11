import json

from odoo import api, models, _


class bomstrutrue(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_mat(self, bom):
        bom_obj = self.env['mrp.bom'].browse(bom)
        material = []
        for line in bom_obj.bom_material_cost_ids:
            material.append({
                'product': line.product_id.name,
                'operation': line.operation_id,
                'qty': line.planned_qty,
                'uom': line.uom_id,
                'cost': line.cost,
                'total': line.total_cost,
            })
        return material

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        res = super(bomstrutrue, self)._get_bom(bom_id, product_id, line_qty, line_id, level)
        material = self._get_mat(bom_id)
        equipment = self._get_equipment(bom_id)
        overhead = self._get_overhead(bom_id)
        m_cost = 0.0
        m_total = 0.0
        e_cost = 0.0
        e_total = 0.0
        o_cost = 0.0
        o_total = 0.0
        for m in material:
            m_cost += m['cost']
            m_total += m['total']
        for e in equipment:
            e_cost += e['cost']
            e_total += e['total_cost']
        for o in overhead:
            o_cost += o['cost']
            o_total += o['total_cost']

        print("\n\n\n\n\nres['total']===>",res['total'])
        print("\n\n\n\n\nres['bom_cost']===>",res['bom_cost'])
        print("\n\n\n\n\nm_cost===>",m_cost)
        print("\n\n\n\n\ne_cost===>",e_cost)
        print("\n\n\n\n\no_cost===>",o_cost)
        print("\n\n\n\n\nm_total===>",m_total)
        print("\n\n\n\n\ne_total===>",e_total)
        print("\n\n\n\n\no_total===>",o_total)
        res['total'] += m_total + e_total + o_total
        # res['total'] =  m_cost + e_cost + o_cost
        # res['prod_cost'] +=  m_cost + e_cost + o_cost
        # for x in res['components']:
        #     x[0]['prod_cost'] +=  m_cost + e_cost + o_cost
        # res['components'][int(6)] +=  m_cost + e_cost + o_cost
        res['overhead'] = overhead
        res['equipment'] = equipment
        res['material'] = material
        print("\n\n\n\n\nres['total']===>",res['total'])
        print("\n\n\n\n\nres['bom_cost']===>",res['bom_cost'])

        return res

    def _get_equipment(self, bom):
        bom_obj = self.env['mrp.bom'].browse(bom)
        equipment = []
        for line in bom_obj.bom_equipment_cost_ids:
            equipment.append({
                'equipment_id': line.equipment_id.name,
                'workcenter_id': line.operation_id.name,
                'qty': line.planned_qty,
                'cost': line.cost,
                'total_cost': line.total_cost,
            })
        return equipment

    def _get_overhead(self, bom):
        bom_obj = self.env['mrp.bom'].browse(bom)
        overhead = []
        for line in bom_obj.bom_overhead_cost_ids:
            overhead.append({
                'operation_id': line.operation_id.name,
                'workcenter_id': line.workcenter_id.name,
                'uom_id': line.uom_id.name,
                'qty': line.planned_qty,
                'cost': line.cost,
                'total_cost': line.total_cost,
            })
        return overhead
