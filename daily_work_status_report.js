// Copyright (c) 2023, Riverstone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Work Status Report', {
	onload: function(frm) {
		if (frm.is_new()) {
			frm.doc.date = frappe.datetime.now_date();
			frappe.db.get_value("Employee", {'user_id': frappe.session.user} ,'name').then(d => {
				if (d.message) {
					frm.set_value("employee",d.message.name)
				}
			})
			var currentDate = new Date();
			var currentMonthNumber = currentDate.getMonth() + 1;
			var lastMonthNumber = currentMonthNumber - 1;
			if (lastMonthNumber === 0) {
				lastMonthNumber = 12;
			}
			var lastMonthName = new Date(currentDate.getFullYear(), lastMonthNumber, 1).toLocaleString('default', { month: 'long' });
			frm.doc.month = lastMonthName
		}
	},

	role_played(frm) {
        $.each(frm.doc.status_details || [], function (i, role) {
            role.role_played = frm.doc.role_played;
            frm.refresh_field("status_details")
        })
	},

	before_save: function(frm) {
		frappe.call({
			method: 'rit.rit.doctype.daily_work_status_report.daily_work_status_report.calculate_total_hours',
			args: {
				"ws_doc" : frm.doc.status_details
			},
			callback: function(r) {
				if (r.message) {
					frm.doc.total_working_hours = r.message
				}
			},
		});
	}
});

frappe.ui.form.on("Work Status Details", {
    status_details_add(frm, cdt, cdn) {
        var child = locals[cdt][cdn]
        child.role_played = frm.doc.role_played
        frm.refresh_field("status_details")
    }
});
