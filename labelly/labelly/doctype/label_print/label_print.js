// Copyright (c) 2025, D-codE and contributors
// For license information, please see license.txt

frappe.ui.form.on("Label Print", {
	refresh(frm) {
		// Add custom button to fetch items
		frm.add_custom_button(__('Get Items'), function() {
			frm.events.fetch_items(frm);
		});
	},

	// Trigger fetch when filters change
	item_group(frm) {
		if (frm.doc.item_group || frm.doc.brand || frm.doc.price_list) {
			frm.events.fetch_items(frm);
		}
	},

	brand(frm) {
		if (frm.doc.item_group || frm.doc.brand || frm.doc.price_list) {
			frm.events.fetch_items(frm);
		}
	},

	price_list(frm) {
		if (frm.doc.item_group || frm.doc.brand || frm.doc.price_list) {
			frm.events.fetch_items(frm);
		}
	},

	fetch_items(frm) {
		// Build filters
		let filters = {};
		
		if (frm.doc.item_group) {
			filters.item_group = frm.doc.item_group;
		}
		
		if (frm.doc.brand) {
			filters.brand = frm.doc.brand;
		}

		// Show loading indicator
		frappe.show_alert({
			message: __('Fetching items...'),
			indicator: 'blue'
		}, 2);

		// Call server method to get items
		frappe.call({
			method: 'labelly.labelly.doctype.label_print.label_print.get_items',
			args: {
				filters: filters,
				price_list: frm.doc.price_list || null
			},
			callback: function(r) {
				if (r.message) {
					// Clear existing items
					frm.clear_table('items');
					
					// Add fetched items to child table
					r.message.forEach(function(item) {
						let row = frm.add_child('items');
						row.item_code = item.item_code;
						row.item_name = item.item_name;
						row.brand = item.brand;
						row.item_group = item.item_group;
						row.barcode = item.barcode;
						row.price_list = frm.doc.price_list;
						row.selling_price = item.selling_price;
						row.buying_price = item.buying_price;
						row.offer_rate = item.offer_rate || 0;
					});
					
					// Refresh the child table
					frm.refresh_field('items');
					
					frappe.show_alert({
						message: __('Loaded {0} items', [r.message.length]),
						indicator: 'green'
					}, 3);
				}
			}
		});
	}
});
