# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LoanApplication(Document):
	def validate(self):
		self.validate_salary()
		self.check_eligibility()
		self.validate_loan_product()


	def validate_salary(self):
		minimum_salary=frappe.get_single_value("Loan Settings",'minimum_salary')
		if self.applicant_salary<minimum_salary:
			frappe.throw(f"For Loan Salary should be greater than ${minimum_salary}")
	
	def check_eligibility(self):
		settings=frappe.get_single("Loan Settings")
		if self.occupation=="Unemployment":
			self.eligible==0

	def validate_loan_product(self):
		loan=self.loan_product
		product=frappe.get_doc("Loan Product",loan,as_dict=True)
		if self.tenure<product.min_tenure:
			frappe.throw(f"Tenure should be greater than {product.min_tenure}")

		if self.interest_rate<product.min_interest_rate:
			frappe.throw(f"Minimum Interest Rate is {product.min_interest_rate}")

		if not product.min_loan_amount<= self.requesting_amount <= product.max_amount:
			frappe.throw("Requesting Loan amount should be in a range of {product.min_loan_amount} - {product.max_amount}") 		


	def on_update(self):
		if self.loan_process_status=='Sanctioned' and self.sanctioned_amount== 0.00:
			frappe.throw("Sanction Amount Should be Filled")

 