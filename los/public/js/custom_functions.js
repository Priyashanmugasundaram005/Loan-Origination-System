

frappe.ui.form.on("User",{
    bank_name :function(frm){
        console.log("111111")
        frappe.call({
            method: "los.custom.custom_functions.bank",
            args: {
                doc: frm.doc.bank_name
            },
            callback: function (r) {

                let branch = r.message || [];
                

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
})