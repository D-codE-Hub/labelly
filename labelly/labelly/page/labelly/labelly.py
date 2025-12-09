import frappe

@frappe.whitelist()
def generate_preview(config):
    if isinstance(config, str):
        config = frappe.parse_json(config)

    fields = config.get("fields", [])
    barcode = config.get("barcode_value")
    w = config.get("paper_width")
    h = config.get("paper_height")
    barcode_width = config.get("barcode_width")
    barcode_height = config.get("barcode_height")
    barcode_font_size = config.get("barcode_font_size")
    barcode_format = config.get("barcode_format")
    hide_barcode_text = config.get("hide_barcode_text")
    add_company_name = config.get("add_company_name")
    # Build text fields in NEW LINE (stacked vertically)
    html_fields = ""
    for f in fields:
        txt = f.get("text", "")
        html_fields += f"""
            <div style='
                font-size:10px;
                text-align:center;
            '>
                {txt}
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
        ">
            <!-- Text fields -->
            <div>
                {html_fields}
            </div>

            <!-- Barcode -->
            <div style="text-align:center;">
                <svg id="barcode"></svg>
            </div>

            <script>
                
                JsBarcode("#barcode", "{barcode}", {{
                    format: "{barcode_format}",
                    width: {barcode_width},
                    height: {barcode_height},
                    fontSize: {barcode_font_size},
                    displayValue: {hide_barcode_text},
                    margin: 0,
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
    fields = config.get("fields", [])
    barcode = config.get("barcode_value")

    prn_commands = []
    prn_commands.append(f"SIZE {w} mm, {h} mm")
    prn_commands.append("DIRECTION 0,0")
    prn_commands.append("REFERENCE 0,0")
    prn_commands.append("CLS")

    for f in fields:
        txt = f.get("text", "")
        x = f.get("x", 0)
        y = f.get("y", 0)
        # Assuming coordinates are passed as-is (dots vs mm handled by user input for now or assumed dots)
        # Adding a basic safety quote escape for text
        safe_text = txt.replace('"', '\\"')
        prn_commands.append(f'TEXT {x},{y},"0",0,1,1,"{safe_text}"')

    # Barcode at fixed position for now as per previous, or could be dynamic too but requirements said "fields"
    # Keeping barcode hardcoded as per original logic's spirit but safely separate
    safe_barcode = barcode.replace('"', '')
    prn_commands.append(f'BARCODE 40,100,"128",60,1,0,2,2,"{safe_barcode}"')
    
    prn_commands.append("PRINT 1")

    prn = "\n".join(prn_commands)

    return {"prn": prn}
