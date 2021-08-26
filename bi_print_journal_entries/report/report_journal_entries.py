from odoo import models
from num2words import num2words


class ReportJournalEntries(models.Model):
    _inherit = "account.move"
    _description = "Customer Statement"

    def amount_in_words(self, total):
        amount_in_words = "".join(num2words(total, lang='en_IN').title().replace("-", " ")).replace(",", "")
        return amount_in_words
