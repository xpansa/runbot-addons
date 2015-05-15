#from openerp.osv import fields, osv
from openerp.addons.runbot.runbot import now

from openerp import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class RunbotBranch(models.Model):
    _inherit = 'runbot.branch'

    branch_remote_name = fields.Char()
    branch_remote_pr_number = fields.Integer()
    branch_remote_state = fields.Char(size=16)
    active = fields.Boolean(default=True)


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    @api.one
    def sync_remote(self):
        _logger.debug('sync remote', self.name)
        if self.host_driver == 'github':
            github_filter = {
                'state': 'all',
            }
            github_filter_list = [
                key + '=' + github_filter[key]
                for key in github_filter.keys()
            ]
            branches = self.env['runbot.branch'].search([
                ('repo_id', '=', self.id),
                ('name', 'like', 'refs/pull/%')
            ])
            for branch in branches:
                pull_number = branch.branch_name
                info_pull = self.github(
                    '/repos/:owner/:repo/pulls/%s' % (pull_number))
                if info_pull.get('id', False):
                    branch.write({
                        'branch_remote_name': info_pull['head']['label'],
                        'branch_remote_pr_number': info_pull['number'],
                        'branch_remote_state': info_pull['state'],
                        'active': info_pull['state'] == 'closed',
                    })

