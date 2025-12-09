frappe.pages['labelly'].on_page_load = function (wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Barcode Preview',
        single_column: true
    });

    $(frappe.render_template("labelly", {})).appendTo(page.body);

    // ADD FIELD
    $("#add_field").click(function () {
        add_field_row("", 10, 10);
    });

    // DELETE FIELD
    $("#fields_table").on("click", ".del-field", function () {
        $(this).closest("tr").remove();
    });

    // Add a default field
    add_field_row("D-codE", 10, 10);


    // UPDATE PREVIEW
    $("#update_preview").click(function () {
        let config = get_config();

        frappe.call({
            method: "labelly.labelly.page.labelly.labelly.generate_preview",
            args: { config },
            callback: function (r) {
                $("#preview_content").html(r.message.html);
            }
        });
    });

    // GENERATE PRN
    $("#generate_prn").click(function () {
        let config = get_config();

        frappe.call({
            method: "labelly.labelly.page.labelly.labelly.generate_prn",
            args: { config },
            callback: function (r) {
                $("#prn_output").text(r.message.prn);
            }
        });
    });

    function add_field_row(text, x, y) {
        let row = `<tr>
            <td><input class="form-control input-sm field-text" value="${text}"></td>
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
                x: row.find(".field-x").val(),
                y: row.find(".field-y").val()
            });
        });

        return {
            paper_width: $("#paper_width").val(),
            paper_height: $("#paper_height").val(),
            fields: fields,
            barcode_value: $("#barcode_value").val(),
            barcode_width: $("#barcode_width").val(),
            barcode_height: $("#barcode_height").val(),
            barcode_font_size: $("#barcode_font_size").val(),
            barcode_format: $("#barcode_format").val(),
            hide_barcode_text: $("#hide_barcode_text").is(":checked") ? "false" : "true",
            add_company_name: $("#add_company_name").is(":checked") ? "true" : "false",
        };
    }
};
