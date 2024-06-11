import frappe
from frappe.model.document import Document

def calculate_total_salary_of_employee(self,method):
    self.custom_total_salary = (self.custom_basic_salary or 0) + (self.custom_transportation_cost or 0) + (self.custom_housing_cost or 0)