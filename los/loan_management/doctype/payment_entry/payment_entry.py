# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate,add_months

class PaymentEntry(Document):
	def validate(self):

		if self.emi_for_this_month>self.payment_amount:
			frappe.throw(f"Payment amount should be greater than or equal to EMI Amount {self.emi_for_this_month}")

	def on_submit(self):
		if self.payment_type=='EMI':
			self.emi_amount_validation()
		
		if self.payment_type=='Principal':
			self.principal_amount_validation()





	def emi_amount_validation(self):
		emi_doc=frappe.get_doc('EMI',{'loan_application_id':self.loan_application_id})
		
		months_comp=emi_doc.payment_completed_months+1
		principal=emi_doc.principal_amount

		if self.emi_for_this_month<self.payment_amount:
			extra_amount=self.payment_amount-self.emi_for_this_month
			principal=emi_doc.principal_amount-extra_amount
		tenure,interest_rate=frappe.get_value("Loan Application",self.loan_application_id,['tenure','interest_rate'])
		frappe.log_error("ten",tenure)
		N=tenure*12
		pending_months=N-months_comp	
		R=interest_rate/(12*100)

		if R==0:
			emi=principal/pending_months
		else:
			emi=(principal*R*(1+R)** pending_months)/ ((1+R) ** pending_months - 1)

		emi=round(emi,2)
		total_emi=emi* pending_months
		total_paid=emi_doc.amount_paid+self.payment_amount

		if principal==0:
			emi_doc.db_set('emi_status','Closed')
	

		due=add_months(getdate(emi_doc.due_date),1)

		emi_doc.db_set({
			'payment_completed_months':months_comp,
			'due_date':due,
			'principal_amount':principal,
			'payment_pending_months':pending_months,
			'pending_amount':total_emi,
			'amount_paid':total_paid,
			'paid':1
		})
		

	def principal_amount_validation(self):
		emi_doc=frappe.get_doc('EMI',{'loan_application_id':self.loan_application_id})
		balance=emi_doc.principal_amount-self.payment_amount
		if balance==0:
			emi_doc.db_set('emi_status','Closed')

		emi_doc.db_set('principal_amount',balance)