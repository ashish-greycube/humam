// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salary Calculation CD", {
	onload: function (frm) {
        if (!frm.doc.salary_date) {
			frm.set_value("salary_date", frappe.datetime.get_today());
		}
    }
});
