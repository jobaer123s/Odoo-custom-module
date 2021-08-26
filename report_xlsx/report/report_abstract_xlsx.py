import logging
from io import BytesIO

from odoo import models

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug("Can not import xlsxwriter`.")


class ReportXlsxAbstract(models.AbstractModel):
    _name = "report.report_xlsx.abstract"
    _description = "Abstract XLSX Report"

    def _get_objs_for_report(self, docids, data):

        if docids:
            ids = docids
        elif data and "context" in data:
            ids = data["context"].get("active_ids", [])
        else:
            ids = self.env.context.get("active_ids", [])
        return self.env[self.env.context.get("active_model")].browse(ids)

    def create_xlsx_report(self, docids, data):
        objs = self._get_objs_for_report(docids, data)
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data, self.get_workbook_options())
        self.generate_xlsx_report(workbook, data, objs)
        workbook.close()
        file_data.seek(0)
        return file_data.read(), "xlsx"

    def get_workbook_options(self):
        return {}

    def generate_xlsx_report(self, workbook, data, objs):
        raise NotImplementedError()
