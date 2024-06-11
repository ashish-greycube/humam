import frappe
from frappe.model.document import Document
from frappe import _

def calculate_total_salary_of_employee(self,method):
    self.custom_total_salary = (self.custom_basic_salary or 0) + (self.custom_transportation_cost or 0) + (self.custom_housing_cost or 0)

def unlink_salary_calculation_on_cancel_on_journal_entry(self, method):
    sc_list = frappe.db.get_list('Salary Calculation CD', filters={'journal_entry': self.name}, fields=['name', 'journal_entry'])

    if len(sc_list) > 0:
        for sc in sc_list:
            frappe.db.set_value('Salary Calculation CD', sc.name, 'journal_entry', '')
            frappe.msgprint(_('Salary Calculation {0} is unlink'.format(sc.name)))