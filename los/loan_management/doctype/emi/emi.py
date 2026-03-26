# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,add_days,getdate

class EMI(Document):
	def validate(self):
		self.db_set("paid_card",self.amount_paid)
		self.db_set("pend_card",self.pending_amount)






