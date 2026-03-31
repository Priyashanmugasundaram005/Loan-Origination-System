frappe.ui.form.on("Loan Application", {

    // bank_name: function (frm) {
    //     frappe.call({
    //         method: "los.loan_management.doctype.loan_application.loan_application.bank",
    //         args: {
    //             doc: frm.doc.bank_name
    //         },
    //         callback: function (r) {

    //             let branch = r.message || [];

    //             frm.set_query('branch_name', () => {
    //                 if (!branch.length) {
    //                     return {
    //                         filters: {
    //                             name: ["=", ""]
    //                         }
    //                     };
    //                 }
    //                 return {
    //                     filters: {
    //                         name: ['in', branch]
    //                     }
    //                 };
    //             });

    //             if (!branch.length) {
    //                 frappe.msgprint("No branches found for selected bank");
    //             }
    //         }
    //     });
    // },
    refresh(frm) {

        frm.add_custom_button("View History", () => {
            show_history_dialog(frm);
        });

        frappe.call({
            method: "los.loan_management.doctype.loan_application.loan_application.bank_details",
            callback: function (r) {
                if (r.message) {
                    frm.set_value("bank_name", r.message.bank_name);
                    frm.set_value("branch_name", r.message.branch_name);
                }
            }
        });

    },

    onload(frm) {
        frm.set_df_property('loan_process_status', 'read_only', 1)
        list = [
            "bank_name",
            "branch_name",
            "loan_process_status",
            "loan_disbursement_date",
            "workflow_remarks",
            "applicant_details_section",
            "applicant_id",
            "applicant_name",
            "applicant_address",
            "occupation",
            "account_number",
            "applicant_email",
            "applicant_salary",
            "credit_score",
            "loan_product",
            "loan_category_type",
            "interest_rate",
            "tenure",
            "eligible",
            "loan_status",
            "requesting_amount",
            "sanction",
            "primary_securities_section",
            "security_type",
            "security_description",
            "estimated_value",
            "document_proofs",
            "nominees"]


        if (frappe.user.has_role("Checker") && frappe.session.user !== "Administrator") {
            frm.set_read_only();

        }

        if (frappe.user.has_role("Sanctioner") && frappe.session.user !== "Administrator") {
            for (let field of list) {
                frm.set_df_property(field, 'read_only', 1)
            }
            frm.set_df_property('sanction_amount', 'read_only', 0)
        }

        // {
        //     const roles = frappe.user_roles || [];
        //     const is_system_manager = roles.includes("System Manager");

        //     if (roles.includes("Checker") && !is_system_manager) {
        //         frm.set_read_only();
        //         return;
        //     }

        //     if (roles.includes("Sanctioner") && !is_system_manager) {
        //         (list || []).forEach(field => frm.set_df_property(field, 'read_only', 1));
        //         frm.set_df_property('sanction_amount', 'read_only', 0);
        //     }
        // }
    },


    before_workflow_action: function (frm) {
        if (frm.selected_workflow_action === "Send for Verification") {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            let submitted = false;

            let d = new frappe.ui.Dialog({
                title: `${frm.selected_workflow_action} - Remarks`,
                fields: [
                    {
                        label: "Remarks",
                        fieldname: "remarks",
                        fieldtype: "Small Text",
                        reqd: 1,
                    },
                ],
                primary_action_label: "Submit",
                primary_action(values) {
                    if (!values.remarks || !values.remarks.trim()) {
                        frappe.msgprint("Remarks is mandatory");
                        return;
                    }
                    submitted = true;
                    frm.set_value("workflow_remarks", values.remarks);
                    d.hide();
                    frm.save(
                        undefined,
                        (r) => {
                            if (r && r.exc) {
                                reject(new Error("Save failed"));
                                return;
                            }
                            resolve();
                        },
                        null,
                        () => reject(new Error("Save aborted"))
                    );
                },
                secondary_action_label: __("Cancel"),
                secondary_action() {
                    d.hide();
                },
            });

            d.onhide = function () {
                if (!submitted) {
                    reject(new Error("cancelled"));
                }
            };

            frappe.dom.unfreeze();
            d.show();
        });
    }



});

function show_history_dialog(frm) {

    let d = new frappe.ui.Dialog({
        title: "Workflow History",
        size: "large",
        fields: [
            {
                fieldname: "history",
                fieldtype: "Table",
                label: "History",
                cannot_add_rows: true,
                cannot_delete_rows: true,

                fields: [

                    {
                        fieldname: "action",
                        label: "Action",
                        fieldtype: "Data",
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        fieldname: "user",
                        label: "User",
                        fieldtype: "Data",
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        fieldname: "remarks",
                        label: "Remarks",
                        fieldtype: "Small Text",
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        fieldname: "date",
                        label: "Date",
                        fieldtype: "Datetime",
                        in_list_view: 1,
                        read_only: 1
                    }
                ]
            }
        ]
    });

    fetch_history(frm, d);
    d.show();

}

function fetch_history(frm, dialog) {

    frappe.call({
        method: "los.loan_management.doctype.loan_application.loan_application.get_workflow_history",
        args: {
            doctype: frm.doc.doctype,
            docname: frm.doc.name
        },
        callback: function (r) {

            dialog.fields_dict.history.df.data = r.message || [];
            dialog.fields_dict.history.grid.refresh();
        }
    });
}