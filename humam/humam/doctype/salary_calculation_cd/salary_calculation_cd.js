// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salary Calculation CD", {
		get_employee:function (frm) {
			frm.call({
				doc: frm.doc,
				method: "get_employee",
				freeze: true,
				callback: (r) => {
					if (!r.exc) {
						frm.save();
					}
				},
			});
		},
		create_jv:function (frm) {
			frm.call({
				doc: frm.doc,
				method: "create_jv",
				freeze: true,
				callback: (r) => {
					if (!r.exc) {
						frm.save();
					}
				},
			});
		}		
    });
