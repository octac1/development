// Copyright (c) 2023, Riverstone and contributors
// For license information, please see license.txt

frappe.ui.form.on('Monthly Status Report', {
	onload: function(frm) {
		if (frm.is_new()) {
			frm.doc.posting_date = frappe.datetime.now_date();
			frm.doc.year = erpnext.utils.get_fiscal_year(frappe.datetime.get_today());
			var currentDate = new Date();
			var currentMonthNumber = currentDate.getMonth() + 1;
			var lastMonthNumber = currentMonthNumber - 1;
			if (lastMonthNumber === 0) {
				lastMonthNumber = 12;
			}
			var lastMonthName = new Date(currentDate.getFullYear(), lastMonthNumber - 1, 1).toLocaleString('default', { month: 'long' });
			frm.doc.month = lastMonthName
		}	
	},

	refresh: function(frm) {
		if (frm.doc.__islocal) {
            frm.set_df_property('generate_pdf_button', 'hidden', true);
        } else {
            frm.add_custom_button('Generate PDF', function () {
                generate_and_attach_pdf(frm);
            }).addClass('btn-primary');
        }
	},

	after_save: function(frm) {
		frm.set_df_property('generate_pdf_button', 'hidden', false);
    },

	project(frm){
		frappe.call({
			method: 'rit.rit.doctype.monthly_status_report.monthly_status_report.get_employees_list',
			args: {
				"project": frm.doc.project,
			},
			callback: function(r) {
				if (r.message) {
					frm.clear_table("employees_list")
					$.each(r.message,function(i, d){
						frm.add_child("employees_list", {
							"user": d.user
						})
					})
					frm.refresh_field("employees_list");
				}
			}
		});
		frappe.call({
			method: 'rit.rit.doctype.monthly_status_report.monthly_status_report.get_accomplishments',
			args: {
				"doc": frm.doc,
			},
			callback: function(r) {
				if (r.message) {
					frm.clear_table("accomplishment_details")
					$.each (r.message, function(i, list){
						frm.add_child("accomplishment_details", {
							"description": list
						})
					})
					frm.refresh_field("accomplishment_details")
				}
			}
		});
		frappe.call({
			method: 'rit.rit.doctype.monthly_status_report.monthly_status_report.get_testing_task_details',
			args: {
				"doc": frm.doc,
			},
			callback: function(r) {
				if (r.message) {
					frm.clear_table("testing_tickets_list")
					$.each (r.message, function(i, list){
						frm.add_child("testing_tickets_list", {
							"employee": list.employee,
							"issues_found": list.issues_found,
							"scenarios_covered": list.automation_count,
							"testcases_covered": list.testcase_count
						});
					})
					frm.refresh_field("testing_tickets_list")
				}
			}
		});
		frappe.call({
			method: 'rit.rit.doctype.monthly_status_report.monthly_status_report.get_development_task_details',
			args: {
				"doc": frm.doc,
			},
			callback: function(r) {
				if (r.message) {
					frm.clear_table("development_tickets_details")
					$.each (r.message, function(i, list){
						frm.add_child("development_tickets_details", {
							"employee": list.employee,
							"feature": list.feature_count,
							"issue": list.bug_count
						});
					})
					frm.refresh_field("development_tickets_details")
				}
			}
		});
	},

	month(frm) {
		frappe.call({
			method: 'rit.rit.doctype.monthly_status_report.monthly_status_report.get_accomplishments',
			args: {
				"doc": frm.doc,
			},
			callback: function(r) {
				if (r.message) {
					frm.clear_table("accomplishment_details")
					$.each (r.message, function(i, list){
						frm.add_child("accomplishment_details", {
							"description": list
						})
					})
					frm.refresh_field("accomplishment_details")
				}
			}
		});
		frappe.call({
			method: 'rit.rit.doctype.monthly_status_report.monthly_status_report.get_testing_task_details',
			args: {
				"doc": frm.doc,
			},
			callback: function(r) {
				if (r.message) {
					frm.clear_table("testing_tickets_list")
					$.each (r.message, function(i, list){
						frm.add_child("testing_tickets_list", {
							"employee": list.employee,
							"issues_found": list.issues_found,
							"scenarios_covered": list.automation_count,
							"testcases_covered": list.testcase_count
						});
					})
					frm.refresh_field("testing_tickets_list")
				}
			}
		});
		frappe.call({
			method: 'rit.rit.doctype.monthly_status_report.monthly_status_report.get_development_task_details',
			args: {
				"doc": frm.doc,
			},
			callback: function(r) {
				if (r.message) {
					frm.clear_table("development_tickets_details")
					$.each (r.message, function(i, list){
						frm.add_child("development_tickets_details", {
							"employee": list.employee,
							"feature": list.feature_count,
							"issue": list.bug_count
						});
					})
					frm.refresh_field("development_tickets_details")
				}
			}
		});
	}
});

function generate_and_attach_pdf(frm) {
    frappe.call({
        method: 'rit.rit.doctype.monthly_status_report.generate_pdf.generate_and_attach_pdf',
        args: {
            'doc': frm.doc,
        },
        callback: function (response) {
            console.log(response);
            frm.reload_doc();
        }
    });
}