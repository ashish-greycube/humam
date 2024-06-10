# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe.utils import getdate,flt,cstr,add_days,get_first_day,get_last_day

class DailyOrderCD(Document):
	def validate(self):
		self.date = today()
