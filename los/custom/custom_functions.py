import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,add_days,getdate

def make_unpaid():
	frappe.db.sql("""
        UPDATE `tabEMI`
        SET paid = 0
    """)

def email_emi_reminder():
	reminder=add_days(nowdate(),-7)
	emi_pending=frappe.get_all("EMI",{'due_date':reminder},['name','due_date','loan_application_id'])
	for emi in emi_pending:
		email,applicant=frappe.get_value("Loan Application",emi.loan_application_id,['applicant_email','applicant_name'])
		url="/app/emi/"+emi.name

		frappe.enqueue(
            method=frappe.sendmail,
            queue="short",  
            recipients=[email],
            subject=f"Reminder: EMI Due Soon for Loan {emi.loan_application_id}",
            message=f"""
                <p>Hello {applicant}</p>
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


def penalty_calculation_reminder():
    today = getdate(nowdate())
      
    pending=frappe.get_all("EMI",filters={"due_date": ["<", nowdate()]},fields=["name", "emi_per_month", "loan_application_id"])
    penalty_rate=frappe.get_single_value("Loan Settings",'penalty_percent')

    for pending_emi in pending:

        emi=pending_emi.emi_per_month
        loan=pending_emi.loan_application_id
        email,applicant=frappe.get_value("Loan Application",loan,['applicant_email','applicant_name'])

        penalty_amount=(emi*penalty_rate)/100
        exists=frappe.db.exists("Payment Entry",{'loan_application_id':loan})
        if exists:
            old=frappe.get_doc("Payment Entry",exists)
            if old.last_penalty_email_sent:
                last_date = getdate(old.last_penalty_email_sent)

                if last_date.month == today.month and last_date.year == today.year:
                    continue 

            old.db_set("penalty", (old.penalty or 0) + penalty_amount)
            url="/app/payment-entry/"+old.name

        else:
            new=frappe.new_doc("Payment Entry")
            new.loan_application_id=loan
            new.payment_type='Penalty'
            new.penalty=penalty_amount
            new.insert(ignore_permissions=True)
            
            url="/app/payment-entry/"+new.name

        frappe.enqueue(
            method=frappe.sendmail,
            queue="short", 
            recipients=[email],
            subject=f"Alert: Penalty for Loan {loan}",
            message=f"""
                    <p>Hello {applicant}</p>
                    <li>Loan ID: {loan}</li>
                    <li>EMI ID: {pending_emi.name}</li>
                    <li>Penalty Amount :{penalty_amount}</li>
                </ul>
                <p><a href="{url}">View EMI / Make Payment</a></p>
            """
        )
        if exists:
            old.db_set("last_penalty_email_sent", nowdate())
        else:
            new.db_set("last_penalty_email_sent", nowdate())

def log(doc,method):
    allowed=['Loan Application','Payment Entry','EMI']
    if doc.doctype in allowed:
        audit=frappe.new_doc("Audit Log")
        audit.process_type=doc.doctype
        audit.action=method

        if doc.doctype=='Loan Application':
            audit.loan_application_id=doc.name
            audit.bank_name=doc.bank_name
            audit.applicant_name=doc.applicant_name
            audit.application_status=doc.loan_process_status
            audit.remarks=doc.reason_for_rejection

        elif doc.doctype=="EMI":
            audit.loan_application_id=doc.loan_application_id
            audit.emi_status=doc.emi_status
            audit.emi_amount=doc.emi_per_month
            audit.paid_amount=doc.amount_paid
        
        elif doc.doctype=="Payment Entry":
            audit.loan_application_id=doc.loan_application_id
            audit.payment_type=doc.payment_type
            audit.paid_amount=doc.payment_amount
        audit.insert(ignore_permissions=True)
    
@frappe.whitelist(allow_guest=True)
def get_status_chart_data():
    cache_key = "loan_status_distribution"
    data = frappe.cache.get_value(cache_key)

    if not data:
        data = frappe.db.sql("""
            SELECT loan_process_status, COUNT(*) as count
            FROM `tabLoan Application`
            GROUP BY loan_process_status
        """, as_dict=True)

        frappe.cache.set_value(cache_key, data, expires_in_sec=300)
    labels = []
    values = []

    for d in data:
        labels.append(d.loan_process_status)
        values.append(d.count)

    return {
        "labels": labels,
        "datasets": [
            {"name": "Loans", "values": values}
        ],
        "type":"bar",
        
    
    }
             
             
                
            
        