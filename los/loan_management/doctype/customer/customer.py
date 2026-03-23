# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import validate_email_address




class Customer(Document):
	def validate(self):
		validate_email_address(self.customer_email, throw=True)
		self.validate_account_number()
		self.validate_credit_score()
		self.validate_salary()
	
	def validate_account_number(self):
		if not self.account_number.isdigit():
			frappe.throw("Account Number must contain only digits")
		if not 9 <= len(self.account_number) <= 18:
			frappe.throw("Account Number must be 9 to 18 digits long")

	def validate_credit_score(self):
		if not 300<= self.credit_score <=900:
			frappe.throw("Credit Score Should be between 300 and 900")
	
	def validate_salary(self):
		min=frappe.get_single_value("Loan Settings",'minimum_salary')
		if self.salary < min:
			frappe.throw(f"salary should be greater than $ {min}")
	
