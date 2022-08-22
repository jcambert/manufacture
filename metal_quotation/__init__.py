# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api
from odoo.tools import convert_file
from . import models
from . import wizards
from . import reports

def _auto_install_workcenter_laser_speed(self):
    convert_file(
        self.cr,
        'metal_quotation',
        'data/mrp.workcenter.cutting.speed.csv',
        {},
        'init',
    )

def _quotation_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _auto_install_workcenter_laser_speed(env)