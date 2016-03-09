# -*- coding: utf-8 -*-

from openerp import models, fields, api
from pygtail import Pygtail

class RunbotLogs(models.Model):
    _name = 'runbot_logs.logs'
    _rec_name = 'build'

    #TODO: add a field build.id in order to filter properly
    build = fields.Integer()
    name = fields.Char()

    @api.model
    def load_log(self, build=None):
        for line in Pygtail("/home/oem/odoo_runbot.log"):
            self.create({'name': line,
                         'build': build})
