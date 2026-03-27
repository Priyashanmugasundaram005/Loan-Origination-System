frappe.ui.form.on("Loan Application", {
    bank_name: function (frm) {
        

        frappe.call({
            method: "los.loan_management.doctype.loan_application.loan_application.bank",
            args: {
                doc: frm.doc.bank_name
            },
            callback: function (r) {
                console.log("111111");

                let branch = r.message || [];
                console.log(branch);

                frm.set_query('branch_name', () => {
                    if (!branch.length) {
                        return {
                            filters: {
                                name: ["=", ""]
                            }
                        };
                    }

                    return {
                        filters: {
                            name: ['in', branch]
                        }
                    };
                });

                if (!branch.length) {
                    frappe.msgprint("No branches found for selected bank");
                }
            }
        });
    }
});