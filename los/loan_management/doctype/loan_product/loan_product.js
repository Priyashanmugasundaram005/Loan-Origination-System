// Copyright (c) 2026, los and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan Product", {
	max_loan_amount : function(frm){
        if(frm.doc.min_loan_amount>frm.doc.max_loan_amount){
            frm.set_df_property("max_loan_amount","description",["Max Amount Should be greater than $",frm.doc.min_loan_amount])
            
        }
    }
});
