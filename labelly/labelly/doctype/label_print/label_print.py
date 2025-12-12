# Copyright (c) 2025, D-codE and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabelPrint(Document):
	pass


@frappe.whitelist()
def get_items(filters, price_list=None):
	"""
	Fetch items based on filters and get their prices
	
	Args:
		filters: dict with item_group, brand filters
		price_list: Price List name to fetch prices from
	
	Returns:
		List of items with details
	"""
	# Convert filters from JSON string if needed
	if isinstance(filters, str):
		filters = frappe.parse_json(filters)
	
	# Build the query
	item_fields = [
		"name as item_code",
		"item_name",
		"brand",
		"item_group"
	]
	
	# Get items based on filters
	items = frappe.get_all(
		"Item",
		filters=filters,
		fields=item_fields,
		order_by="item_name"
	)
	
	# Enrich items with barcode and prices
	for item in items:
		# Get barcode
		barcode = frappe.db.get_value(
			"Item Barcode",
			{"parent": item.item_code},
			"barcode"
		)
		item.barcode = barcode or ""
		
		# Get selling price from Item Price
		if price_list:
			selling_price = frappe.db.get_value(
				"Item Price",
				{
					"item_code": item.item_code,
					"price_list": price_list,
					"selling": 1
				},
				"price_list_rate"
			)
			item.selling_price = selling_price or 0
		else:
			item.selling_price = 0
		
		# Get buying price (standard_rate from Item or from Item Price)
		buying_price = frappe.db.get_value(
			"Item Price",
			{
				"item_code": item.item_code,
				"buying": 1
			},
			"price_list_rate"
		)
		
		if not buying_price:
			# Fallback to standard_rate from Item
			buying_price = frappe.db.get_value(
				"Item",
				item.item_code,
				"standard_rate"
			)
		
		item.buying_price = buying_price or 0
		item.offer_rate = 0  # Default, can be set manually
	
	return items
