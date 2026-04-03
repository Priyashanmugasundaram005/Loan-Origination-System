// Copyright (c) 2026, los and contributors
// For license information, please see license.txt

frappe.ui.form.on("Branch", {
	ifsc_code : function(frm){
        frappe.call({
            method:"los.loan_management.doctype.branch.branch.validate",
            args: {
                doc: frm.doc.ifsc_code
            }
        })
    }

});
