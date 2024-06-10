# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,getdate,flt,cstr,add_days,get_first_day,get_last_day
from datetime import datetime


class SalaryCalculationCD(Document):
	def validate(self):
		self.date = today()

		date = getdate(self.date)
		month_list = ["January","February","March","April","May","June","July","August","September","October","November","December"]

		month = ""
		for i in range(len(month_list)):
			if i == (date.month -1):
				month = month_list[i]
				
		year = date.year
		self.payroll_for = month + ", " + str(year)