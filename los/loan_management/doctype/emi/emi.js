// Copyright (c) 2026, los and contributors
// For license information, please see license.txt

frappe.ui.form.on("EMI", {
	refresh(frm) {
        if( frm.doc.emi_status=='Active' & frm.doc.paid==0)
        {
            frm.add_custom_button("Pay",function(){
                frappe.new_doc("Payment Entry",{
                    payment_type:'EMI',
                    loan_application_id:frm.doc.loan_application_id,
                    emi_for_this_month:frm.doc.emi_per_month,
                    balance_principal_amount:frm.doc.principal_amount,
                    pending_emi_amount:frm.doc.pending_emi_amount
                })

            })
        }

        if( frm.doc.emi_status=='Active' )
        {
            frm.add_custom_button("Pay Principal",function(){
                frappe.new_doc("Payment Entry",{
                    payment_type:'Principal',
                    loan_application_id:frm.doc.loan_application_id,
                    emi_for_this_month:frm.doc.emi_per_month,
                    balance_principal_amount:frm.doc.principal_amount
                })

            })
        }

	},
});
