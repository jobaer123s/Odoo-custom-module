from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = "report.report_xlsx.partner_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Partner XLSX Report"

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            sheet = workbook.add_worksheet("Report")
            bold = workbook.add_format({"bold": True})
            sheet.write(0, 0, obj.name, bold)
