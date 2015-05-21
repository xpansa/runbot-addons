
import logging

from openerp import api, fields, models


_logger = logging.getLogger(__name__)
INACTIVE_STATE = 'closed'


class RunbotBranch(models.Model):
    _inherit = 'runbot.branch'

    branch_remote_name = fields.Char()
    branch_remote_pr_number = fields.Integer()
    branch_remote_state = fields.Char(size=16)

    def write(self, cr, uid, ids, vals, context=None):
        if 'branch_remote_state' in vals:
            if vals['branch_remote_state'] == INACTIVE_STATE:
                rb_pool = self.pool.get('runbot.build')
                rbl_pool = self.pool.get('runbot.build.line')
                build_ids = []
                if rbl_pool:
                    rbls = rbl_pool.search_read(cr, uid, [
                        ('branch_id', 'in', ids),
                    ], [('build_id')])
                    build_ids = [
                        rbl.get('build_id')[0] for rbl in rbls
                    ]
                else:
                    rb_list = rb_pool.search(cr, uid, [
                        ('branch_id', 'in', ids),
                    ], context=context)
                    build_ids = [rb.id for rb in rb_list]
                build_ids = rb_pool.search(cr, uid, [
                    ('state', '<>', 'done'),
                    ('id', 'in', build_ids),
                ], context=context)
                rb_pool.kill(
                    cr, uid, build_ids,
                    result='Inactived branch',
                    context=context)
        return super(RunbotBranch, self).write(
            cr, uid, ids, vals, context=context)


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    @api.multi
    def sync_remote(self):
        _logger.debug('sync remote %s', self.name)
        if self.host_driver == 'github':
            branches = self.env['runbot.branch'].search([
                ('repo_id', 'in', self.ids),
                ('name', 'like', 'refs/pull/%'),
                '|', ('branch_remote_state', '<>', INACTIVE_STATE),
                ('branch_remote_state', '=', False),
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
                    })

    @api.model
    def sync_remote_cron(self):
        _logger.debug('START: sync remote cron')
        repos = self.search([('active', '=', True)])
        for repo in repos:
            repo.sync_remote()
        _logger.debug('STOP: sync remote cron')
