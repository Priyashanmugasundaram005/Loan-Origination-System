frappe.ui.form.on("Loan Application", {
    

    // setup :function(frm){
    //     roles=frappe.get_roles(frm.doc.owner)

    //     if('Checker' in roles )
    //     {
    //         frm.set_read_only(true)
    //     }


    // },



    bank_name: function (frm) {


        frappe.call({
            method: "los.loan_management.doctype.loan_application.loan_application.bank",
            args: {
                doc: frm.doc.bank_name
            },
            callback: function (r) {

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
    refresh(frm){
        console.log("eee")
        frm.add_custom_button("View History", () => {
            console.log("dde")
            show_history_dialog(frm);
        });

    },

    onload(frm) {
        list=[
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

        

        
        if(frappe.user_roles.includes("Checker") )
        {
            frm.set_read_only();
            
        }
        if(frappe.user_roles.includes("Sanctioner"))
        {

            for (let field of list){
                frm.set_df_property(field,'read_only',1)
            }
            frm.set_df_property('sanction_amount','read_only',0)
        //     console.log("sa")
        //     frm.set_read_only();
        //     setTimeout(()=>{
        //         let field = frm.fields_dict['sanction_amount'];

        // if (field) {
        //     field.df.read_only = 0;
        //     field.refresh();
        // }
        //     },200)
            
            
            
        }
    },
    

    before_workflow_action: async function (frm) {

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
                cannot_delete_rows:true,
                
                fields: [
                    
                    {
                        fieldname: "action",
                        label: "Action",
                        fieldtype: "Data",
                        in_list_view: 1,
                        read_only:1
                    },
                    {
                        fieldname: "user",
                        label: "User",
                        fieldtype: "Data",
                        in_list_view: 1,
                        read_only:1
                    },
                    {
                        fieldname: "remarks",
                        label: "Remarks",
                        fieldtype: "Small Text",
                        in_list_view: 1,
                        read_only:1
                    },
                    {
                        fieldname: "date",
                        label: "Date",
                        fieldtype: "Datetime",
                        in_list_view: 1,
                        read_only:1
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
        callback: function(r) {

            dialog.fields_dict.history.df.data = r.message || [];
            dialog.fields_dict.history.grid.refresh();
        }
    });
}