# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate,add_months,nowdate,now

class PaymentEntry(Document):
	def autoname(self):
		if self.loan_application_id:
			count=frappe.db.count("Payment Entry",{'loan_application_id':self.loan_application_id})+1
			secq=str(count).zfill(5)
			self.name=f"{self.loan_application_id}-PAYMENT-{secq}"


	# def validate(self):

		# if self.payment_type!='Penalty' and self.emi_for_this_month > self.payment_amount:
		# 	frappe.throw(f"Payment amount should be greater than or equal to EMI Amount {self.emi_for_this_month}")


	def on_submit(self):
		self.db_set("penalty_paid",1)
		
		if self.payment_type=='EMI':
			frappe.enqueue(
            method=self.emi_amount_validation,
            queue="long",
            timeout=600,
        )
		
		if self.payment_type=='Principal':
			self.principal_amount_validation()


	def emi_amount_validation(self):
		doc=self
		emi_name = frappe.db.get_value("EMI",{"loan_application_id": doc.loan_application_id},"name")
		emi_doc=frappe.get_cached_doc('EMI',emi_name)

		pending_emi=emi_doc.pending_emi_amount or emi_doc.emi_per_month
		frappe.log_error("pending",pending_emi)

		remaining=pending_emi- doc.payment_amount
		frappe.log_error("out_rem",remaining)
		principal=emi_doc.principal_amount

		total_paid=emi_doc.amount_paid+doc.payment_amount

		if remaining>0:
			payment_type = "Partial"
			pending_emi = remaining
			months_comp = emi_doc.payment_completed_months
			due_date = emi_doc.due_date

		elif remaining==0:
			payment_type = "Full"
			pending_emi = 0
			months_comp = emi_doc.payment_completed_months + 1
			due_date = add_months(getdate(emi_doc.due_date), 1)

		else:
			payment_type = "Excess"
			extra = abs(remaining)
			principal -= extra
			pending_emi = 0
			months_comp = emi_doc.payment_completed_months + 1
			due_date = add_months(getdate(emi_doc.due_date), 1)

		# 🔹 Add entry to child table
		pending=emi_doc.pending_amount
		emi_doc.append("emi_payment_history", {
			"payment_date": now(),
			"amount": doc.payment_amount,
			"payment_type": payment_type,
			'interest':self.emi_for_this_month,
			'principal':self.balance_principal_amount,
			'extra_payment':extra or 0,
			"reference": doc.name,
			'due_date':emi_doc.due_date,
			'pending_due_amount':pending
		})

		tenure,interest_rate=frappe.get_cached_value("Loan Application",doc.loan_application_id,['tenure','interest_rate'])
		N=tenure*12
		pending_months=N-months_comp
		if pending_months>0:
			R=interest_rate/(12*100)
			if R==0:
				emi=principal/pending_months
			else:
				emi=(principal*R*(1+R)** pending_months)/ ((1+R) ** pending_months - 1)

			emi=round(emi,2)
			total_emi=emi* pending_months
		else:
			total_emi=0
		
		if principal<=0:
			emi_doc.db_set('emi_status','Closed')
			emi_doc.db_set('paid',1)

		frappe.log_error("Pen",pending_emi)

		emi_doc.db_set({
			'payment_completed_months':months_comp,
			'due_date':due_date,
			'principal_amount':principal,
			'last_emi_paid_date':nowdate(),
			'payment_pending_months':pending_months,
			'pending_amount':total_emi,
			'amount_paid':total_paid,
			'pending_emi_amount':emi_doc.emi_per_month if pending_emi==0 else pending_emi ,
			'paid':1 if pending_emi==0 else 0
		})
		emi_doc.save(ignore_permissions=True)



	def principal_amount_validation(self):
		emi_doc=frappe.get_doc('EMI',{'loan_application_id':self.loan_application_id})
		balance=emi_doc.principal_amount-self.payment_amount
		if balance==0:
			emi_doc.db_set('emi_status','Closed')

		emi_doc.db_set('principal_amount',balance)



