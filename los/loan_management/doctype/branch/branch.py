# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document
from frappe.utils import validate_email_address


class Branch(Document):
	def validate(self):
		validate_email_address(self.customer_email, throw=True)
		pattern=pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
		if self.ifsc_code and not re.match(pattern,self.ifsc_code):
			frappe.throw("Enter a Valid IFSC Code")

