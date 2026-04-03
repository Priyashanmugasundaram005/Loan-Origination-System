# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document
from frappe.utils import validate_email_address


class Branch(Document):
	def autoname(self):
		if self.bank_name:
			self.name=f"{self.branch_name} - {self.bank_name}"

@frappe.whitelist(allow_guest=True)		
def validate(doc):
	# validate_email_address(self.branch_email, throw=True)
	pattern=pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
	if doc and not re.match(pattern,doc):
		frappe.throw("Enter a Valid IFSC Code")

