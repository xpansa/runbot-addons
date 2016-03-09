# -*- coding: utf-8 -*-
from openerp import http

class RunbotRenderLogs(http.Controller):

    @http.route('/logs', auth='public')
    def list(self, **kw):
        logs = http.request.env['runbot_logs.logs']
        logs.load_log()
        return http.request.render('runbot_render_logs.logs', {
            'objects': logs.search([], limit=20, order='id asc'),
        })
    @http.route('/logs/<lines>', auth='public')
    def log_line(self, line, **kw):
        return "94584 | 2016-03-09 04:16:55,921 14012 INFO ? openerp: OpenERP version 9.0c "


#     @http.route('/runbot_render_logs/runbot_render_logs/objects/<model("runbot_render_logs.runbot_render_logs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('runbot_render_logs.object', {
#             'object': obj
#         })
