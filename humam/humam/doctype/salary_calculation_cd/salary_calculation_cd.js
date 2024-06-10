// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salary Calculation CD", {
	onload: function (frm) {
        if (!frm.doc.date) {
			frm.set_value("date", frappe.datetime.get_today());
		}
    }
});
