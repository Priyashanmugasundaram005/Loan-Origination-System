# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,add_days

class EMI(Document):
	pass





def make_unpaid():
	frappe.db.sql("""
        UPDATE `tabEMI`
        SET paid = 0
    """)

def email_emi_reminder():
	reminder=add_days(nowdate(),-7)
	emi_pending=frappe.get_all("EMI",{'due_date':reminder},['name','due_date','loan_application_id'])
	for emi in emi_pending:
		email=frappe.get_value("Loan Application",emi.loan_application_id)
		url="/app/emi/"+emi.name

		frappe.enqueue(
            method=frappe.sendmail,
            queue="short",  # or "default", "long"
            timeout=300,
            recipients=[email],
            subject=f"Reminder: EMI Due Soon for Loan {emi.loan_application_id}",
            message=f"""
                <h3>EMI Payment Reminder ⏰</h3>
                <p>Your EMI is due on {emi.due_date}.</p>
                <ul>
                    <li>Loan ID: {emi.loan_application_id}</li>
                    <li>EMI ID: {emi.name}</li>
                </ul>
                <p><a href="{url}">View EMI / Make Payment</a></p>
            """
        )
        

def permission_query_conditions(user):
    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    if "Maker" in roles:
        return f"""
            `tabLoan Application`.owner = {frappe.db.escape(user)}
        """

    elif "Checker" in roles:
        return """
            `tabLoan Application`.loan_process_status = 'Pending Verification'
        """

    elif "Sanctioner" in roles:
        return """
            `tabLoan Application`.loan_process_status = 'Verified'
        """

    return "1=0"