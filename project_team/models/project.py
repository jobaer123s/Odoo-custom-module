from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    project_detail = fields.Text(string='Project Detail', translate=True)
    technology = fields.Char(string='Technologies', translate=True)
    project_start_date = fields.Date(string='Project Start Date')
    project_closing_forecast_date = fields.Date(string='Project Closing Date (Forecast)')
    project_closing_actual_date = fields.Date(string='Project Closing Date (Actual)')
    git_repo = fields.Char(string='Git Repository')
    dev_instance = fields.Char(string='Dev Instance Link')
    live_instance = fields.Char(string='Live Instance Link')
    skype = fields.Char(string='Skype Group Details')

    project_deliverable = fields.One2many('project.deliverable', 'project_deli_id', string='Project Deliverable', copy=True, auto_join=True)
    dev_team_com = fields.One2many('dev.team.composition', 'dev_team_id', string='Dev Team Composition', copy=True, auto_join=True)
    client_team_com = fields.One2many('client.team.composition', 'client_team_id', string='Client Team Composition', copy=True, auto_join=True)


class Deliverable(models.Model):
    _name = 'project.deliverable'

    project_deli_id = fields.Many2one('project.project', string='Project Deliverable', ondelete='cascade', index=True, copy=False)
    name = fields.Char(string='Module Name')
    technology = fields.Char(string='Technology')
    deadline = fields.Date(string='Deadline')
    remarks = fields.Char(string='Remarks')


class DevTeamComposition(models.Model):
    _name = 'dev.team.composition'

    dev_team_id = fields.Many2one('project.project', string='Dev Team Composition', ondelete='cascade', index=True, copy=False)
    name = fields.Char(string='Member Name')
    designation = fields.Char(string='Designation')
    role = fields.Char(string='Role')
    contact_no = fields.Char(string='Contact No.')
    email = fields.Char(string='Email')
    remarks = fields.Char(string='Remarks')


class ClientTeamComposition(models.Model):
    _name = 'client.team.composition'

    client_team_id = fields.Many2one('project.project', string='Client Team Composition', ondelete='cascade', index=True, copy=False)
    name = fields.Char(string='Member Name')
    designation = fields.Char(string='Designation')
    role = fields.Char(string='Role')
    contact_no = fields.Char(string='Contact No.')
    email = fields.Char(string='Email')
    remarks = fields.Char(string='Remarks')
