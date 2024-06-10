import frappe
from frappe.model.document import Document

def calculate_total_salary_of_employee(self,method):
    self.custom_total_salary = self.custom_basic_salary + self.custom_transportation_cost + self.custom_housing_cost