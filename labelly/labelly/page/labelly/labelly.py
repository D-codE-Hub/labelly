import frappe

@frappe.whitelist()
def generate_preview(config):
    if isinstance(config, str):
        config = frappe.parse_json(config)

    fields = config.get("fields", [])
    barcode = config.get("barcode_value")
    w = float(config.get("paper_width"))
    h = float(config.get("paper_height"))
    columns = int(config.get("columns_per_row", 1))
    column_gap = float(config.get("column_gap", 5))
    barcode_x = config.get("barcode_x", 10)
    barcode_y = config.get("barcode_y", 10)
    barcode_width = config.get("barcode_width")
    barcode_height = config.get("barcode_height")
    barcode_font_size = config.get("barcode_font_size")
    barcode_format = config.get("barcode_format")
    hide_barcode_text = config.get("hide_barcode_text")
    add_company_name = config.get("add_company_name")
    company_name = config.get("company_name", "")
    
    # Calculate single label width
    label_width = w
    if columns > 1:
        label_width = (w - (column_gap * (columns - 1))) / columns
    
    # Build preview for all columns
    labels_html = ""
    for col in range(columns):
        # Calculate offset for this column
        offset_x = col * (label_width + column_gap)
        
        # Build text fields with absolute positioning
        html_fields = ""
        for f in fields:
            txt = f.get("text", "")
            field_name = f.get("name", "")
            x = float(f.get("x", 10))
            y = float(f.get("y", 10))
            
            # Display text with field name if provided
            display_text = txt
            if field_name:
                display_text = f"{txt} {{{{{field_name}}}}}"
            
            html_fields += f"""
                <div style='
                    position:absolute;
                    left:{x}mm;
                    top:{y}mm;
                    font-size:10px;
                '>
                    {display_text}
                </div>
            """
        
        # Add company name if enabled
        company_html = ""
        if add_company_name == "true" and company_name:
            company_html = f"""
                <div style='
                    position:absolute;
                    left:2mm;
                    top:1mm;
                    font-size:8px;
                    font-weight:bold;
                '>
                    {company_name}
                </div>
            """
        
        # Single label
        labels_html += f"""
            <div style="
                position:absolute;
                left:{offset_x}mm;
                top:0;
                background:white;
                width:{label_width}mm;
                height:{h}mm;
            ">
                {company_html}
                {html_fields}
                
                <!-- Barcode -->
                <div style="position:absolute; left:{barcode_x}mm; top:{barcode_y}mm;">
                    <svg class="barcode-svg" data-col="{col}"></svg>
                </div>
            </div>
        """
        
        # Add gap indicator between columns
        if col < columns - 1:
            gap_x = offset_x + label_width
            labels_html += f"""
                <div style="
                    position:absolute;
                    left:{gap_x}mm;
                    top:0;
                    width:{column_gap}mm;
                    height:{h}mm;
                    background:repeating-linear-gradient(
                        45deg,
                        #e8f4f8,
                        #e8f4f8 3px,
                        #d0e8f0 3px,
                        #d0e8f0 6px
                    );
                    opacity:0.6;
                ">
                    <div style="
                        position:absolute;
                        top:50%;
                        left:50%;
                        transform:translate(-50%, -50%) rotate(-90deg);
                        font-size:8px;
                        color:#666;
                        white-space:nowrap;
                        font-weight:bold;
                    ">GAP {column_gap}mm</div>
                </div>
            """

    # Final HTML card preview
    html = f"""
    <div style="
        display:flex;
        justify-content:center;
        padding:20px;
        background:#f5f5f5;
        border-radius:12px;
    ">
        <div style="
            background:white;
            width:{w}mm;
            height:{h}mm;
            padding:5px;
            border-radius:12px;
            border:1px solid #ddd;
            box-shadow:0 4px 12px rgba(0,0,0,0.1);
            position:relative;
        ">
            {labels_html}

            <script>
                document.querySelectorAll('.barcode-svg').forEach(function(svg) {{
                    JsBarcode(svg, "{barcode}", {{
                        format: "{barcode_format}",
                        width: {barcode_width},
                        height: {barcode_height},
                        fontSize: {barcode_font_size},
                        displayValue: {hide_barcode_text},
                        margin: 0,
                    }});
                }});
            </script>
        </div>
    </div>
    """

    return {"html": html}



@frappe.whitelist()
def generate_prn(config):
    if isinstance(config, str):
        config = frappe.parse_json(config)

    w = config.get("paper_width")
    h = config.get("paper_height")
    columns = int(config.get("columns_per_row", 1))
    column_gap = float(config.get("column_gap", 5))
    printer_dpi = int(config.get("printer_dpi", 203))
    fields = config.get("fields", [])
    barcode = config.get("barcode_value")
    barcode_x = config.get("barcode_x", 10)
    barcode_y = config.get("barcode_y", 10)
    barcode_width = config.get("barcode_width", 2)
    barcode_height = config.get("barcode_height", 40)
    barcode_format = config.get("barcode_format", "CODE128")
    add_company_name = config.get("add_company_name")
    company_name = config.get("company_name", "")

    # Convert mm to dots based on DPI
    # DPI to dots/mm: DPI / 25.4
    DOTS_PER_MM = printer_dpi / 25.4
    
    def mm_to_dots(mm_value):
        return int(float(mm_value) * DOTS_PER_MM)
    
    # Calculate single label width
    label_width = float(w)
    if columns > 1:
        label_width = (float(w) - (column_gap * (columns - 1))) / columns

    prn_commands = []
    prn_commands.append(f"SIZE {w} mm, {h} mm")
    prn_commands.append("DIRECTION 0,0")
    prn_commands.append("REFERENCE 0,0")
    prn_commands.append("CLS")
    prn_commands.append("")

    # Generate PRN for each column
    for col in range(columns):
        offset_x = col * (label_width + column_gap)
        offset_x_dots = mm_to_dots(offset_x)
        # Add company name if enabled
        if add_company_name == "true" and company_name:
            company_x = offset_x_dots + mm_to_dots(2)
            company_y = mm_to_dots(1)
            safe_company = company_name.replace('"', '\\"')
            prn_commands.append(f'TEXT {company_x},{company_y},"0",0,1,1,"{safe_company}"')
        
        # Add text fields with converted coordinates
        for f in fields:
            txt = f.get("text", "")
            field_name = f.get("name", "")
            x = mm_to_dots(float(f.get("x", 0))) + offset_x_dots
            y = mm_to_dots(f.get("y", 0))
            safe_text = txt.replace('"', '\\"')
            
            # Add field name comment if provided
            if field_name:
                prn_commands.append(f'TEXT {x},{y},"0",0,1,1,"{safe_text} {{{{{field_name}}}}}"')
            else:
                prn_commands.append(f'TEXT {x},{y},"0",0,1,1,"{safe_text}"')

        # Map barcode format to PRN barcode type
        barcode_type_map = {
            "CODE128": "128",
            "EAN13": "EAN13",
            "UPCA": "UPCA"
        }
        barcode_type = barcode_type_map.get(barcode_format, "128")
        
        # Convert barcode position and size
        bc_x = mm_to_dots(barcode_x) + offset_x_dots
        bc_y = mm_to_dots(barcode_y)
        bc_height = mm_to_dots(barcode_height)
        bc_width = int(barcode_width)  # Width multiplier (1-10)
        
        safe_barcode = barcode.replace('"', '')
        
        # PRN BARCODE syntax: BARCODE x,y,"type",height,readable,rotation,narrow,wide,"data"
        prn_commands.append(f'BARCODE {bc_x},{bc_y},"{barcode_type}",{bc_height},1,0,{bc_width},{bc_width},"{safe_barcode}"')
        prn_commands.append("")
    
    prn_commands.append("PRINT 1")

    prn = "\n".join(prn_commands)

    return {"prn": prn}


@frappe.whitelist()
def create_print_format(config, print_format_name):
	"""
	Create a Print Format for Label Print doctype using the PRN data
	
	Args:
		config: Configuration dict with all label settings
		print_format_name: Name for the new print format
	
	Returns:
		Name of created print format
	"""
	if isinstance(config, str):
		config = frappe.parse_json(config)
	
	# Generate the PRN data (instead of preview)
	prn_data = generate_prn(config)
	prn_content = prn_data.get("prn", "")
	
	# Create Jinja2 template with PRN field substitution
	html_template = convert_prn_to_jinja_template(prn_content, config)
	
	# Check if print format already exists
	existing = frappe.db.exists("Print Format", print_format_name)
	if existing:
		print_format_name = f"{print_format_name} {frappe.utils.now()}"
	
	# Create Print Format
	print_format = frappe.get_doc({
		"doctype": "Print Format",
		"name": print_format_name,
		"doc_type": "Label Print",
		"module": "Labelly",
		"standard": "No",
		"custom_format": 1,
		"html": html_template,
		"print_format_type": "Jinja",
		"print_format_builder": 0
	})
	
	print_format.insert(ignore_permissions=True)
	
	return print_format.name


def convert_prn_to_jinja_template(prn_content, config):
	"""
	Convert PRN commands to HTML display with Jinja2 field substitution
	"""
	fields = config.get("fields", [])
	barcode_value = config.get("barcode_value")
	company_name = config.get("company_name", "")
	add_company_name = config.get("add_company_name")
	
	# Start with PRN content
	template = prn_content
	
	# Replace static text with Jinja variables for each field
	for field in fields:
		field_name = field.get("name", "")
		field_text = field.get("text", "")
		
		if field_name:
			# Replace field name placeholder with Jinja variable
			static_placeholder = f"{{{{{field_name}}}}}"
			jinja_variable = f"{{{{ item.{field_name} }}}}"
			template = template.replace(static_placeholder, jinja_variable)
			
			# Also replace the text value if present
			template = template.replace(f'"{field_text}"', f'"{{{{ item.{field_name} or \'{field_text}\' }}}}"')
	
	# Replace static barcode with item barcode
	template = template.replace(f'"{barcode_value}"', '"{{ item.barcode }}"')
	
	# Replace company name if enabled
	if add_company_name == "true" and company_name:
		template = template.replace(f'"{company_name}"', '"{{ doc.company or \'' + company_name + '\' }}"')
	
	# Wrap PRN in HTML pre tags for display and loop through items
	html_template = f"""
        {{% for item in doc.items %}}
        {template.replace(chr(10), '<br>')}
        {{% endfor %}}
        """
	return html_template
