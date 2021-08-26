# -*- coding: utf-8 -*-

from odoo import models, fields

class change_passwd(models.TransientModel):
    _name = 'aa.change_passwd'
    
    def _default_get_login(self):
        return self.env['res.users'].browse(self._uid).login
    
    login=fields.Char('Login', default=_default_get_login,readonly=True)
    passwd = fields.Char('Password', required=True)
    
    def change_passwd_buttonn(self):
#         print('________change_passwd_button____')
        self.ensure_one()
        encrypted = self.env['res.users']._crypt_context().encrypt(self.passwd)
        self.env.cr.execute("UPDATE res_users SET password=%s WHERE id=%s",(encrypted, self._uid))
        self.env.cr.commit()
        return {
          'type': 'ir.actions.client',
          'tag': 'logout',
          }
