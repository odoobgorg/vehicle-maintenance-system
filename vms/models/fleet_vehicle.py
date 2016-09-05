# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class FleetVehicle(models.Model):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'
    _description = "Vehicle"
    _order = 'name asc'

    program_id = fields.Many2one(
        'vms.program',
        string='Maintenance Program')
    last_order_id = fields.Many2one(
        'vms.order',
        string='Last Order')
    last_cycle_id = fields.Many2one(
        'vms.vehicle.cycle',
        string='Last Cycle', default=False)
    next_cycle_id = fields.Many2one(
        'vms.vehicle.cycle',
        string='Next Cycle')
    next_service_date = fields.Datetime()
    next_service_odometer = fields.Float()
    next_service_sequence = fields.Integer()
    cycle_ids = fields.One2many(
        'vms.vehicle.cycle', 'unit_id', string="Cycles")
    sequence = fields.Integer()

    @api.multi
    def program_mtto(self):
        for vehicle in self:
            prog_ids = vehicle.cycle_ids.search([('unit_id', '=', vehicle.id)])
            if len(prog_ids):
                prog_ids.unlink()
            for cycle in vehicle.program_id.cycle_ids:
                seq = 1
                for x in range(cycle.frequency, 4000000, cycle.frequency):
                    vehicle.cycle_ids.create({
                        'cycle_id': cycle.id,
                        'schedule': x,
                        'sequence': seq,
                        'unit_id': vehicle.id,
                    })
                    seq += 1
            last_schedule = 0.00
            for cycles in vehicle.cycle_ids:
                if (last_schedule < vehicle.odometer < cycles.schedule):
                    vehicle.sequence = cycles.sequence
                    vehicle.last_cycle_id = cycles.id
                    next = cycles.search([
                        ('sequence', '=', (cycles.sequence + 1)),
                        ('unit_id', '=', vehicle.id)])
                    vehicle.next_cycle_id = next.id
                    vehicle.next_service_odometer = next.schedule
                    return True
                else:
                    last_schedule = cycles.schedule
                    cycles.unlink()
