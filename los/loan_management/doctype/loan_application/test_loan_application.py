# Copyright (c) 2026, los and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

def test_bank():
    old=frappe.db.exists("Bank",{'bank_name':'SBI'})
    if old:
        return frappe.get_doc("Bank",old)
    bank=frappe.new_doc("Bank")
    bank.bank_name = "State Bank Of India"
    bank.short_name="SBI"
    bank.insert()
    return bank

def test_branch():
    old=frappe.db.exists("Branch",{'bank_name':'Tirupur'})
    if old:
        return frappe.get_doc("Branch",old)
    branch=frappe.new_doc("branch")
    branch.branch_name = "Tirupur"
    branch.bank_name="SBI"
    branch.ifsc_code = "SBIN0908765"
    branch.insert()
    return branch

def test_applicant():
    old=frappe.db.exists("Customer",{'account_number':'9087654321'})
    if old:
        return frappe.get_doc("Customer",old)
    customer=frappe.new_doc("Customer")
    customer.Customer_name = "Priyaa"
    customer.salary= 200000
    customer.account_number = "9087654321"
    customer.insert()
    return customer

# def test_loan_product():
#     old=frappe.db.exists("Loan Product",{'product_name':"Commercial"})
#     if old:
#         return frappe.get_doc("Loan Product")

def test_create_loan(bank,branch,applicant,**kwargs):
    
    loan=frappe.new_doc("Loan Application")
    loan.branch_name = branch.branch_name
    loan.bank_name=bank.short_name
    loan.applicant_id=applicant.name





class TestLoanApplication(FrappeTestCase):
    def setUp(self):
        self.bank= test_bank()
        self.branch = test_branch()
        self.applicant= test_applicant()
        self.loan = test_create_loan(self.bank,self.branch,self.applicant)

    # def test