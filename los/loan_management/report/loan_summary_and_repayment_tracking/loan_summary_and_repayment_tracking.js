// Copyright (c) 2026, los and contributors
// For license information, please see license.txt

frappe.query_reports["Loan Summary and Repayment tracking"] = {
	"filters": [
		{
			fieldname:'Loan_category',
			label:('Loan Category'),
			fieldtype:'Link',
			options:'Loan Product Categories'
		},
		{
			fieldname:'applicant_id',
			label:('Applicant ID'),
			fieldtype:'Link',
			options:'Customer'
		},
		{
			fieldname:'loan_status',
			label:('Loan Status'),
			fieldtype:'Select',
			options:['None','Active','Closed']
		},
	],

	formatter: function(value, row, column, data, default_formatter){
		value=default_formatter(value, row, column, data)

		if (column.fieldname =="loan_status" && data){
			if(data.loan_status=="Active"){
				value=`<span style="color:green">${value}</span>`;
			}
			else{
				value=`<span style="color:red">${value}</span>`;
			}
		} 
		return value;
		}
};



