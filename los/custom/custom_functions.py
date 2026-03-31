import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,add_days,getdate,now

def make_unpaid():
	frappe.db.sql("""
        UPDATE `tabEMI`
        SET paid = 0
    """)



def email_emi_reminder():
    

    remind = frappe.get_single_value("Loan Settings", 'emi_reminder_days')
    reminder = add_days(nowdate(), remind )
    print(remind)
    print(reminder)
    emi_pending = frappe.get_all(
        "EMI",
        {'due_date': reminder},
        ['name', 'due_date', 'loan_application_id']
    )

    for emi in emi_pending:
        email, applicant = frappe.get_value(
            "Loan Application",
            emi.loan_application_id,
            ['applicant_email', 'applicant_name']
        )

        url = f"/app/emi/{emi.name}"

        frappe.enqueue(
            method=frappe.sendmail,
            queue="short",
            recipients=[email],
            subject=f"⏰ EMI Reminder | Loan {emi.loan_application_id}",
            message=get_emi_email_template(applicant, emi, url)
        )

def get_emi_email_template(applicant, emi, url):
    return f"""
    <div style="font-family: Arial, sans-serif; line-height:1.6; color:#333;">
        
        <h2 style="color:#2E86C1;">📢 EMI Payment Reminder</h2>

        <p>Dear <b>{applicant}</b>,</p>

        <p>This is a friendly reminder that your upcoming EMI payment is scheduled soon.</p>

        <div style="background:#F4F6F7; padding:15px; border-radius:8px;">
            <p><b>📅 Due Date:</b> {emi.due_date}</p>
            <p><b>📄 Loan ID:</b> {emi.loan_application_id}</p>
            <p><b>💳 EMI Reference:</b> {emi.name}</p>
        </div>

        <p style="margin-top:15px;">
            To avoid any late fees or penalties, we recommend completing your payment on or before the due date.
        </p>

        <p style="text-align:center; margin:25px 0;">
            <a href="{url}" 
               style="background:#28B463; color:white; padding:12px 20px; 
                      text-decoration:none; border-radius:5px; font-weight:bold;">
               👉 View EMI & Pay Now
            </a>
        </p>

        <p>If you have already made the payment, please ignore this message.</p>

        <hr>


        <p>Regards,<br><b>Loan Team</b></p>

    </div>
    """
        

def permission_query_conditions(user):

    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    user_bank = frappe.db.get_value("User", user, "bank_name")
    user_branch = frappe.db.get_value("User", user, "branch_name")

    user_bank = frappe.db.escape(user_bank) if user_bank else None
    user_branch = frappe.db.escape(user_branch) if user_branch else None

    if "Bank Manager" in roles and user_bank:
        return f"`tabLoan Application`.bank_name = {user_bank}"

    branch_condition = ""
    if user_branch:
        branch_condition = f"`tabLoan Application`.branch_name = {user_branch}"

    if "Maker" in roles:
        return branch_condition

    elif "Checker" in roles:
        return f"""
            {branch_condition}
            AND `tabLoan Application`.loan_process_status = 'Pending Verification'
        """

    elif "Sanctioner" in roles:
        return f"""
            {branch_condition}
            AND `tabLoan Application`.loan_process_status IN ('Verified', 'Sanctioned')
        """

    return "1=0"


def has_permission(doc,user):
    if not user:
        user=frappe.session.user

    if user=='Administrator':
         return ""
    
    roles = frappe.get_roles(user)

    user_bank = frappe.db.get_value("User", user, "bank_name")
    user_branch = frappe.db.get_value("User", user, "branch_name")

    if "Bank Manager" in roles:
        if doc.bank_name == user_bank:
            return True

    if any(role in roles for role in ["Maker", "Checker", "Sanctioner"]):
        if doc.branch_name == user_branch:
            return True

    return False


def penalty_calculation_reminder():
    today = getdate(nowdate())
      
    pending=frappe.get_all("EMI",filters={"due_date": ["<", nowdate()]},fields=["name", "emi_per_month", "loan_application_id",'last_penalty_email_sent'])
    penalty_rate=frappe.get_single_value("Loan Settings",'penalty_percent')

    for pending_emi in pending:

        emi=pending_emi.emi_per_month
        loan=pending_emi.loan_application_id
        email,applicant=frappe.get_value("Loan Application",loan,['applicant_email','applicant_name'])

        penalty_amount=(emi*penalty_rate)/100
        exists=frappe.db.exists("Payment Entry",{'loan_application_id':loan})
        if exists:
            old=frappe.get_doc("Payment Entry",exists)
            if pending_emi.get("last_penalty_email_sent"):
                last_date = getdate(pending_emi.get("last_penalty_email_sent")) 

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
        subject=f"⚠️ Penalty Alert | Loan {loan}",
        message=f"""
        <div style="font-family: Arial, sans-serif; color:#333; line-height:1.6;">

            <h3 style="color:#C0392B;">Penalty Notification ⚠️</h3>

            <p>Dear {applicant},</p>

            <p>
                A penalty has been applied to your loan due to delayed payment.
            </p>

            <div style="background:#FDEDEC; padding:12px; border-radius:6px;">
                <ul style="list-style:none; padding-left:0;">
                    <li><b>Loan ID:</b> {loan}</li>
                    <li><b>EMI ID:</b> {pending_emi.name}</li>
                    <li><b>Penalty Amount:</b> ₹{penalty_amount}</li>
                </ul>
            </div>

            <p style="margin-top:15px;">
                Please clear the penalty at the earliest to avoid further charges.
            </p>

            <p style="text-align:center; margin:20px 0;">
                <a href="{url}" 
                style="background:#E74C3C; color:white; padding:10px 18px; 
                        text-decoration:none; border-radius:5px;">
                    View Penalty Details & Pay Now
                </a>
            </p>

            <p>
                Regards,<br>
                <b>Loan Processing Team</b>
            </p>

        </div>
        """)
        frappe.db.set_value("EMI",pending_emi.name,"last_penalty_email_sent",today)

def log(doc,method):
    allowed=['Loan Application','Payment Entry','EMI']
    if doc.doctype in allowed:
        audit=frappe.new_doc("Audit Log")
        audit.process_type=doc.doctype
        audit.action=method
        audit.date=now()

        if doc.doctype=='Loan Application':
            audit.loan_application_id=doc.name
            audit.bank_name=doc.bank_name
            audit.applicant_name=doc.applicant_name
            audit.application_status=doc.loan_process_status
            audit.remarks=doc.workflow_remarks

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

  
    data = frappe.db.sql("""
        SELECT loan_process_status, COUNT(*) as count
        FROM `tabLoan Application`
        GROUP BY loan_process_status
    """, as_dict=True)


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

@frappe.whitelist()
def get_loan_type_chart():
    data = frappe.db.sql("""
        SELECT loan_category_type, COUNT(*) as count
        FROM `tabLoan Application`
        GROUP BY loan_category_type
    """, as_dict=True)
    labels=[]
    values=[]

    for d in data:
        category=frappe.db.get_value("Loan Product Category",d.loan_category_type,'category_name')
        
        labels.append(category)
        values.append(d.count)

    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Loan Type Distribution",
                "values": values
            }
        ]
    }     

@frappe.whitelist(allow_guest=True)
def bank(doc):
    
    branch_names=frappe.get_all("Branch",{'bank_name':doc},pluck="name")
    
    return branch_names      
                
            
        