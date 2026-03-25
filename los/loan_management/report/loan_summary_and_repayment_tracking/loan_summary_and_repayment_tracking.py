# Copyright (c) 2026, los and contributors
# For license information, please see license.txt

import frappe
from collections import defaultdict


def execute(filters=None):
	status=filters.get('loan_status')
	applicant=filters.get('applicant_id')
	cat=filters.get('loan_category')

	
	base_filter={}

	if status=='Active' or status=='Closed':
		base_filter['loan_status']=status
	if applicant:
		base_filter['applicant_id']=applicant

	if cat:
		base_filter['loan_category']=cat

	columns=[
		{
			'fieldname': 'loan_application_id',
			'label': ('Loan Application ID'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'applicant_name',
			'label': ('Applicant Name'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'applicant_id',
			'label': ('Applicant ID'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'loan_category',
			'label': ('Loan Category'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'loan_requested_amount',
			'label': ('Loan Requested Amount'),
			'fieldtype': 'Currency'
		},
		{
			'fieldname': 'loan_sanctioned_amount',
			'label': ('Loan Sanctioned Amount'),
			'fieldtype': 'Currency'
		},
		{
			'fieldname': 'loan_status',
			'label': ('Loan Status'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'total_emis_paid',
			'label': ('Total EMIs Paid'),
			'fieldtype': 'Data'
		},
		{
			'fieldname': 'pending_amount',
			'label': ('Pending payment Amount'),
			'fieldtype': 'Data'
		}	

	]
	data=[]

	doc_loans=frappe.get_all("Loan Application",filters=base_filter)
	frappe.log_error("loans",doc_loans)
	for docs in doc_loans:
		# frappe.log_error("doc",doc)
		# frappe.log_error("doc_name",doc.applicant_name)
		doc=frappe.get_doc("Loan Application",docs.name)
		
		emi=frappe.db.get_value("EMI",{'loan_application_id':docs.name},['pending_amount','amount_paid'],as_dict=True) or {}
		pending=emi.get('pending_amount', 0)
		paid=emi.get('amount_paid',0)
		data.append(
			{
				'loan_application_id':doc.name,
				'applicant_name':doc.applicant_name,
				'applicant_id':doc.applicant_id,
				'loan_category':doc.loan_category_type,
				'loan_requested_amount':doc.requesting_amount,
				'loan_sanctioned_amount':doc.sanction_amount,
				'loan_status':doc.loan_status,
				'total_emis_paid':paid,
				'pending_amount':pending
			}
		)

	category_map = defaultdict(lambda: {"total": 0, "closed": 0})
	labels=[]
	total=[]
	closed=[]


	for d in data:
		cat = d.get("loan_category")
		status = d.get("loan_status")

		category_map[cat]["total"] += 1

		if status == "Closed":
			category_map[cat]["closed"] += 1

	
	for cat, values in category_map.items():
		labels.append(cat)
		total.append(values["total"])
		closed.append(values["closed"])
		

	chart = {
		'title': "Total vs Closed Loans per Category",
		'data':{
			'labels':labels,
			'datasets':[
				{
					'name':"Total Loans",
					'values':total
				},
				{
					'name':"Closed Loans",
					'values':closed
				}
			]
		},
		'type': 'bar',
		'height': 300,
	}


	return columns, data ,None, chart
