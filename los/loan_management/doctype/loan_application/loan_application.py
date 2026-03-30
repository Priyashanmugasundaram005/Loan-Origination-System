# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,add_months


class LoanApplication(Document):
    def validate(self):
        self.validate_salary()
        self.check_eligibility()
        self.validate_loan_product()
        self.db_set("sanction",self.sanction_amount)


    def validate_salary(self):
        minimum_salary=frappe.get_single_value("Loan Settings",'minimum_salary')
        if self.applicant_salary<minimum_salary:
            frappe.throw(f"For Loan Salary should be greater than ${minimum_salary:,}")
    
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

        if not product.min_loan_amount<= self.requesting_amount <= product.max_loan_amount:
            frappe.throw(f"Requesting Loan amount should be in a range of ${product.min_loan_amount:,} - ${product.max_loan_amount:,}") 		


    def on_update(self):
        if self.loan_process_status=='Sanctioned' and self.sanction_amount== 0.00:
            frappe.throw("Sanction Amount Should be Filled")
        if self.loan_process_status=='Closed':
            self.db_set("loan_status",'Closed')
        if self.loan_process_status=='Disbursed':
            self.db_set("loan_disbursement_date",nowdate())
        
        if self.loan_process_status=='Disbursed':
            self.emi_log_creation()

    def emi_log_creation(self):

        
        paid_total_amount=0
        completed_payments=0
        P=self.sanction_amount
        R=self.interest_rate/(12*100)
        N=self.tenure*12
        if R==0:
            emi=P/N
        else:
            emi=(P*R*(1+R)**N)/ ((1+R) ** N - 1)
        emi=round(emi,2)

        due=add_months(self.loan_disbursement_date,1)



        emi_log=frappe.db.exists("EMI",{'loan_application_id':self.name})
        if not emi_log:
            new_emi=frappe.new_doc("EMI")
            new_emi.loan_application_id=self.name
            new_emi.loan_amount=self.sanction_amount
            new_emi.principal_amount=self.sanction_amount
            new_emi.due_date=due
            new_emi.emi_per_month=emi
            new_emi.payment_completed_months=completed_payments
            new_emi.payment_pending_months=N
            new_emi.amount_paid=paid_total_amount
            new_emi.pending_amount=emi*N
            new_emi.paid=0
            new_emi.emi_status='Active'
            new_emi.insert(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def bank(doc):
    
    branch_names=frappe.get_all("Branch",{'bank_name':doc},pluck="name")
    
    return branch_names

# import json

# @frappe.whitelist(allow_guest=True)
# def bank(doc):
#     doc = json.loads(doc)  # convert string to dict
    
#     frappe.log_error("Full Doc", str(doc))
#     frappe.log_error("Bank Name", doc.get("bank_name"))


@frappe.whitelist()
def get_workflow_history(doctype, docname):

    history = []

    all_action = frappe.get_all(
        "Audit Log",
        filters={
            "loan_application_id": docname,
            "process_type": doctype
        },
        fields=["application_status", "date", "remarks", "owner"],
        order_by="date desc"   
    )

    last_state = None

    for action in all_action:
        to_state = action.application_status

        if not to_state:
            continue

        if last_state == to_state:
            continue

        from_state = last_state or "Draft"

        history.append({
            "user": action.owner,
            "action": f"{from_state} → {to_state}",
            "remarks": action.remarks or "",
            "date": action.date
        })

        last_state = to_state
    

    return history