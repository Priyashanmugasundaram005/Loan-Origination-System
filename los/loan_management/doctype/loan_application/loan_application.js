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
    },
    

    before_workflow_action: async function (frm) {
        console.log("yesss")

        if (frm.selected_workflow_action === "Send for Verification") {
            return;
        }

        
        if (frm.__remarks_added) {
            frm.__remarks_added = false;
            return;
        }

        
        frappe.validated = false;

        let d = new frappe.ui.Dialog({
            title: `${frm.selected_workflow_action} - Remarks`,
            fields: [
                {
                    label: "Remarks",
                    fieldname: "remarks",
                    fieldtype: "Small Text",
                    reqd: 1
                }
            ],
            primary_action_label: "Submit",
            primary_action(values) {

                if (!values.remarks || !values.remarks.trim()) {
                    frappe.msgprint("Remarks is mandatory");
                    return;
                }

                
                frm.set_value("workflow_remarks", values.remarks);

                d.hide();

                
                frm.__remarks_added = true;

                
                frm.save()
                    .then(() => {
                       
                        frm.page.btn_primary.click();
                    });
            }
        });

        d.show();
    }




});