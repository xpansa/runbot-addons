# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
    This file is used to add the field lang in runbot.build and the function
      that install and assign the language to the users in the instance
      generated.
'''
from openerp.osv import fields, osv
from openerp import tools
import logging
from openerp.addons.runbot.runbot import run

_logger = logging.getLogger(__name__)


class RunbotRepo(osv.osv):

    '''
    Inherit class runbot_repo to add field to select the language that must
      be assigned to builds
      that generate the repo.
    '''
    _inherit = "runbot.repo"

    _columns = {
        'lang': fields.selection(tools.scan_languages(), 'Language',
                                 help='Language to change '
                                 'instance after of run test.', copy=True),
    }


class RunbotBuild(osv.osv):

    '''
    Inherit class runbot_build to add field to select the language &
      the function with a job
      to install and assign the language to users if this is captured
      too is added with an super the
      function create to assign the language from repo in the builds.
    '''
    _inherit = "runbot.build"

    _columns = {
        'lang': fields.selection(tools.scan_languages(), 'Language',
                                 help='Language to change '
                                 'instance after of run test.', copy=True),
    }

    # comment this line. only to test faster.
    # job_10_test_base = lambda self, cr, uid, build, lock_path,\
    #                           log_path, args=None: build.checkout()

    def cmd(self, cr, uid, ids, context=None):
        """Return a list describing the command to start the build"""
        cmd, modules = super(RunbotBuild, self).cmd(cr, uid, ids,
                                                    context=context)
        for build in self.browse(cr, uid, ids, context=context):
            if build.lang and build.job == 'job_30_run':
                cmd.append("--load-language=%s" % (build.lang))
        return cmd, modules

    def update_lang(self, cr, uid, build, context=None):
        """Set lang to all users into '-all' database"""
        # TODO: read version of odoo
        if build.lang:
            db_name = "%s-all" % build.dest
            try:
                # update odoo version >=7.0
                run(['psql', db_name, '-c', "UPDATE res_partner SET lang='%s' "
                     "WHERE id IN (SELECT partner_id FROM res_users);" %
                     (build.lang)])
            except:
                pass
            try:
                # update odoo version <7.0
                run(['psql', db_name, '-c', "UPDATE res_users SET lang='%s';" %
                     (build.lang)])
            except:
                pass
        return True

    def job_30_run(self, cr, uid, build, lock_path, log_path):
        res = super(RunbotBuild, self).job_30_run(cr, uid, build,
                                                  lock_path, log_path)
        self.update_lang(cr, uid, build)
        return res

    def create(self, cr, uid, values, context=None):
        """
        This method set language from repo in the build.
        """
        if values.get('branch_id', False) and 'lang' not in values.keys():
            branch_id = self.pool.get('runbot.branch').browse(
                cr, uid, values['branch_id'])
            values.update({
                'lang': branch_id.repo_id and branch_id.repo_id.lang or False,
            })
        return super(RunbotBuild, self).create(cr, uid, values,
                                               context=context)
    # TODO: Force build or rebuild function not get lang of old build
