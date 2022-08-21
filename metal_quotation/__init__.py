# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api
from odoo.tools import convert_file
from . import models
from . import wizards
from . import reports

def _auto_install_workcenter_laser_speed(self):
    convert_file(
        'metal_quotation',
        'data/Laser_3015_cutting_speed.xlsx',
        {},
        'update',
    )

def _quotation_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _auto_install_workcenter_laser_speed(env)