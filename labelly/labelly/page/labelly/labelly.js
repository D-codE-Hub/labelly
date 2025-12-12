frappe.pages['labelly'].on_page_load = function (wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Label Preview',
        single_column: true
    });

    $(frappe.render_template("labelly", {})).appendTo(page.body);

    // Debounce timer for auto-updates
    let update_timer = null;

    // ADD FIELD
    $("#add_field").click(function () {
        add_field_row("","", 35, 4);
    });

    // DELETE FIELD
    $("#fields_table").on("click", ".del-field", function () {
        $(this).closest("tr").remove();
        trigger_auto_update();
    });

    // Add a default field
    add_field_row("D-codE","item_code", 27, 1);

    // PAPER SIZE PRESET
    $("#paper_preset").change(function () {
        let preset = $(this).val();
        if (preset === "40x25") {
            $("#paper_width").val(40);
            $("#paper_height").val(25);
        } else if (preset === "50x25") {
            $("#paper_width").val(50);
            $("#paper_height").val(25);
        } else if (preset === "78x25") {
            $("#paper_width").val(78);
            $("#paper_height").val(25);
        } else if (preset === "100x50") {
            $("#paper_width").val(100);
            $("#paper_height").val(50);
        } else if (preset === "100x70") {
            $("#paper_width").val(100);
            $("#paper_height").val(70);
        }
        trigger_auto_update();
    });

    // AUTO-UPDATE ON INPUT CHANGE (debounced)
    $(document).on("input change", ".auto-update, .field-text, .field-name, .field-x, .field-y", function () {
        trigger_auto_update();
    });

    // Initial update on page load
    trigger_auto_update();

    // CREATE PRINT FORMAT BUTTON
    $("#create_print_format").click(function () {
        let config = get_config();
        
        frappe.prompt([
            {
                label: 'Print Format Name',
                fieldname: 'print_format_name',
                fieldtype: 'Data',
                reqd: 1,
                default: 'Label Print Format'
            }
        ],
        function(values) {
            frappe.show_alert({
                message: __('Creating print format...'),
                indicator: 'blue'
            }, 2);
            
            frappe.call({
                method: "labelly.labelly.page.labelly.labelly.create_print_format",
                args: {
                    config: config,
                    print_format_name: values.print_format_name
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Print Format created successfully'),
                            indicator: 'green'
                        }, 5);
                        
                        // Open the print format
                    }
                },
                error: function(r) {
                    frappe.show_alert({
                        message: __('Error creating print format'),
                        indicator: 'red'
                    }, 5);
                }
            });
        },
        'Create Print Format',
        'Create'
        );
    });

    function trigger_auto_update() {
        if (update_timer) {
            clearTimeout(update_timer);
        }
        update_timer = setTimeout(function () {
            update_preview_and_prn();
        }, 500); // 500ms debounce
    }

    function update_preview_and_prn() {
        let config = get_config();

        // Update Preview
        frappe.call({
            method: "labelly.labelly.page.labelly.labelly.generate_preview",
            args: { config },
            callback: function (r) {
                $("#preview_content").html(r.message.html);
            }
        });

        // Update PRN
        frappe.call({
            method: "labelly.labelly.page.labelly.labelly.generate_prn",
            args: { config },
            callback: function (r) {
                $("#prn_output").text(r.message.prn);
            }
        });
    }

    function add_field_row(text, name, x, y) {
        let row = `<tr>
            <td><input class="form-control input-sm field-text" value="${text}"></td>
            <td><input class="form-control input-sm field-name" value="${name}"></td>
            <td><input type="number" class="form-control input-sm field-x" value="${x}"></td>
            <td><input type="number" class="form-control input-sm field-y" value="${y}"></td>
            <td><button class="btn btn-xs btn-danger del-field">&times;</button></td>
        </tr>`;
        $("#fields_table tbody").append(row);
    }

    function get_config() {
        let fields = [];
        $("#fields_table tbody tr").each(function () {
            let row = $(this);
            fields.push({
                text: row.find(".field-text").val(),
                name: row.find(".field-name").val(),
                x: row.find(".field-x").val(),
                y: row.find(".field-y").val()
            });
        });

        return {
            paper_width: $("#paper_width").val(),
            paper_height: $("#paper_height").val(),
            columns_per_row: $("#columns_per_row").val() || 1,
            column_gap: $("#column_gap").val() || 5,
            printer_dpi: $("#printer_dpi").val() || 203,
            company_name: $("#company_name").val() || "",
            fields: fields,
            barcode_value: $("#barcode_value").val(),
            barcode_x: $("#barcode_x").val() || 10,
            barcode_y: $("#barcode_y").val() || 10,
            barcode_width: $("#barcode_width").val(),
            barcode_height: $("#barcode_height").val(),
            barcode_font_size: $("#barcode_font_size").val(),
            barcode_format: $("#barcode_format").val(),
            hide_barcode_text: $("#hide_barcode_text").is(":checked") ? "false" : "true",
            add_company_name: $("#add_company_name").is(":checked") ? "true" : "false",
        };
    }
};
