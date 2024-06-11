# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,getdate,flt,cstr,add_days,get_first_day,get_last_day,nowdate
from datetime import datetime
from erpnext import get_default_company

class SalaryCalculationCD(Document):
	def validate(self):

		salary_date = getdate(self.salary_date)
		month_list = ["January","February","March","April","May","June","July","August","September","October","November","December"]

		month = ""
		for i in range(len(month_list)):
			if i == (salary_date.month -1):
				month = month_list[i]

		year = salary_date.year
		self.payroll_for = month + ", " + str(year)

	@frappe.whitelist()
	def create_jv(self):
		# return
		if len(self.salary_calculation_details)>0 and not self.journal_entry:
			company = get_default_company()
			humam_doc = frappe.get_doc('Humam Settings', 'Humam Settings')
			je = frappe.new_doc("Journal Entry")
			je.posting_date = nowdate()
			# je.company = self.company
			je.user_remark = "jv created from {0}".format(self.name)
			# if not cost_center:
			cost_center =  frappe.db.get_value('Company', company, 'cost_center')
			amount=self.total_salary_to_pay
			accounts=[]
			accounts.append(
					{
						"account": humam_doc.salary_debit_account,
						"cost_center": cost_center,
						"debit_in_account_currency": amount if amount > 0 else 0,
						"credit_in_account_currency": abs(amount) if amount < 0 else 0,
					},
			)
			for employee in self.salary_calculation_details:
					accounts.append(
					{
						"account": humam_doc.salary_credit_account,
						"cost_center": cost_center,
						"party_type":'Employee',
						"party":employee.employee,
						"credit_in_account_currency": employee.to_be_paid if employee.to_be_paid > 0 else 0,
						"debit_in_account_currency": abs(employee.to_be_paid) if employee.to_be_paid < 0 else 0,
					}
					)				
			je.set("accounts",accounts)
			je.run_method('set_missing_values')
			je.save(ignore_permissions=True)
			# self.journal_entry=je.name
			frappe.db.set_value('Salary Calculation CD', self.name, 'journal_entry', je.name)
			# self.save()	
		else:
			return	
	@frappe.whitelist()
	def get_employee(self):
		self.salary_calculation_details=[]
		total_salary_to_pay=0
		humam_doc = frappe.get_doc('Humam Settings', 'Humam Settings')
		print(humam_doc,'--',humam_doc.order_slot_1_to_399)
		print('-'*10,self.name)
		first_day=get_first_day(self.salary_date)
		last_day=get_last_day(self.salary_date)
		filters=frappe._dict({'date': ['between', [first_day,last_day]]})
		if self.employee_group:
					filters['employee_group']=self.employee_group	
		print(filters)	
		if self.employee_group:
			daily_orders=frappe.db.get_list('Daily Order CD', filters={'docstatus':1,'order_date': ['between', [first_day,last_day]],'employee_group':self.employee_group},fields=['employee','employee_group','sum(no_of_orders) as no_of_orders'],order_by='employee',group_by='employee')	
		else:
			daily_orders=frappe.db.get_list('Daily Order CD', filters={'docstatus':1,'order_date': ['between', [first_day,last_day]]},fields=['employee','employee_group','sum(no_of_orders) as no_of_orders'],order_by='employee',group_by='employee')	
		print(daily_orders,'daily_orders',len(daily_orders))
		for daily_order in daily_orders:
			print(daily_order)
			salary_components=frappe.get_doc('Employee',daily_order.employee)
			print(salary_components.custom_total_salary,'daily_order.no_of_orders>=1 ',daily_order.no_of_orders>=1 ,daily_order.employee_group)
			# custom_home_allowance_required,custom_transportation_required,custom_basic_salary,custom_housing_cost,custom_transportation_cost,custom_total_salary
			salary_details=frappe._dict({})
			salary_details.employee=daily_order.employee
			salary_details.employee_group=daily_order.employee_group
			salary_details.no_of_orders=daily_order.no_of_orders			
			if daily_order.employee_group=='Company':
				if daily_order.no_of_orders>=1 and daily_order.no_of_orders<=399:
					salary_details.salary=salary_components.custom_total_salary
					salary_details.calculated_salary=flt(daily_order.no_of_orders*humam_doc.order_slot_1_to_399)
					print('salary_details.calculated_salary',salary_details.calculated_salary)
					salary_details.deduction= (salary_components.custom_housing_cost if salary_components.custom_home_allowance_required=='Yes' else 0) + (salary_components.custom_transportation_cost if salary_components.custom_transportation_required=='Yes' else 0)
					salary_details.extra=0
					salary_details.to_be_paid=flt(salary_details.calculated_salary-salary_details.deduction+salary_details.extra)
				elif daily_order.no_of_orders>=400 and daily_order.no_of_orders<=449:
					salary_details.salary=salary_components.custom_total_salary
					salary_details.calculated_salary=salary_components.custom_total_salary
					shortage=humam_doc.company_target-daily_order.no_of_orders
					salary_details.deduction= flt(shortage*humam_doc.order_slot_400_to_449)
					salary_details.extra=0
					salary_details.to_be_paid=flt(salary_details.calculated_salary-salary_details.deduction+salary_details.extra)
				elif daily_order.no_of_orders>=450:
					salary_details.salary=salary_components.custom_total_salary
					salary_details.calculated_salary=salary_components.custom_total_salary
					excess=daily_order.no_of_orders-humam_doc.company_target
					salary_details.deduction= 0
					salary_details.extra=flt(excess*humam_doc.order_slot_more_than_450)
					salary_details.to_be_paid=flt(salary_details.calculated_salary-salary_details.deduction+salary_details.extra)					
			
			elif daily_order.employee_group=='Outside':
				if daily_order.no_of_orders>=1 and daily_order.no_of_orders<=399:
					salary_details.salary=salary_components.custom_total_salary
					salary_details.calculated_salary=flt(daily_order.no_of_orders*humam_doc.order_slot_1_to_399)
					salary_details.deduction=0
					salary_details.extra=0
					salary_details.to_be_paid=flt(salary_details.calculated_salary-salary_details.deduction+salary_details.extra)				
				elif daily_order.no_of_orders>=400 and daily_order.no_of_orders<=449:
					salary_details.salary=salary_components.custom_total_salary
					salary_details.calculated_salary=salary_components.custom_total_salary
					shortage=humam_doc.company_target-daily_order.no_of_orders
					salary_details.deduction= flt(shortage*humam_doc.order_slot_400_to_449)
					salary_details.extra=0
					salary_details.to_be_paid=flt(salary_details.calculated_salary-salary_details.deduction+salary_details.extra)				
				elif daily_order.no_of_orders>=450:		
					salary_details.salary=salary_components.custom_total_salary
					salary_details.calculated_salary=salary_components.custom_total_salary
					excess=daily_order.no_of_orders-humam_doc.company_target
					salary_details.deduction= 0
					salary_details.extra=flt(excess*humam_doc.order_slot_more_than_450)
					salary_details.to_be_paid=flt(salary_details.calculated_salary-salary_details.deduction+salary_details.extra)							

			elif daily_order.employee_group=='Dabbab':
				if daily_order.no_of_orders>=1 and daily_order.no_of_orders<=449:
					salary_details.salary=salary_components.custom_total_salary
					salary_details.calculated_salary=salary_components.custom_total_salary
					shortage=humam_doc.company_target-daily_order.no_of_orders
					salary_details.deduction= flt(shortage*humam_doc.dabbab_group_order_amount)
					salary_details.extra=0
					salary_details.to_be_paid=flt(salary_details.calculated_salary-salary_details.deduction+salary_details.extra)						
				elif daily_order.no_of_orders>=450:				
					salary_details.salary=salary_components.custom_total_salary
					salary_details.calculated_salary=salary_components.custom_total_salary
					excess=daily_order.no_of_orders-humam_doc.company_target
					salary_details.deduction= 0
					salary_details.extra=flt(excess*humam_doc.order_slot_more_than_450)
					salary_details.to_be_paid=flt(salary_details.calculated_salary-salary_details.deduction+salary_details.extra)	
			print('salary_details',salary_details)	
			total_salary_to_pay=total_salary_to_pay+salary_details.to_be_paid		
			self.append('salary_calculation_details',salary_details)
		self.total_salary_to_pay=total_salary_to_pay
			# self.save()