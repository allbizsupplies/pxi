import csv
from datetime import date

from pxi.report import ReportWriter
from pxi.spl_update import SPL_FIELDNAMES


def export_pricelist(filepath, price_region_items):
    """Export pricelist to file."""
    effective_date = date.today().strftime("%d-%b-%Y")
    price_list_field = "0"
    last_change_date = ""
    reason_code = ""
    price_type_code = ""

    def price_region_item_to_row(price_region_item):
        inventory_item = price_region_item.inventory_item
        return [
            inventory_item.code,
            price_region_item.code,
            str(price_region_item.price_0),
            str(price_region_item.quantity_1),
            str(price_region_item.quantity_2),
            str(price_region_item.quantity_3),
            str(price_region_item.quantity_4),
            str(price_region_item.price_1),
            str(price_region_item.price_2),
            str(price_region_item.price_3),
            str(price_region_item.price_4),
            str(price_region_item.rrp_excl_tax),
            str(price_region_item.rrp_incl_tax),
            price_list_field,
            last_change_date,
            effective_date,
            price_type_code,
            reason_code,
        ]
    rows = [price_region_item_to_row(item) for item in price_region_items]
    with open(filepath, "w") as file:
        csv.writer(file).writerows(rows)


def export_price_changes_report(filepath, price_changes):
    """Export report to file."""
    report_writer = ReportWriter(filepath)

    price_change_fields = [
        string_field("item_code", "Item Code", 20),
        string_field("region", "Region", 4),
        string_field("brand", "Brand", 7),
        string_field("apn", "APN", 20),
        string_field("description", "Description", 80),
        string_field("price_rule", "Price Rule", 7),
    ]
    for i in range(5):
        if i > 0:
            price_change_fields.append(number_field(
                "quantity_{}".format(i), "Quantity {}".format(i),
                number_format="0"))
        price_change_fields.append(number_field(
            "price_{}_was".format(i), "Price {} Was".format(i)))
        price_change_fields.append(number_field(
            "price_{}_now".format(i), "Price {} Now".format(i)))
        price_change_fields.append(number_field(
            "price_{}_diff".format(i), "Price {} Diff".format(i)))
        price_change_fields.append(number_field(
            "price_{}_diff_percentage".format(i), "Price {} Diff %".format(i),
            number_format="0%"))

    def price_change_rows(price_changes):
        for price_change in price_changes:
            price_region_item = price_change.price_region_item
            price_diffs = price_change.price_diffs
            inventory_item = price_region_item.inventory_item
            price_rule = price_region_item.price_rule
            row = {
                "item_code": inventory_item.code,
                "region": price_region_item.code,
                "brand": inventory_item.brand,
                "apn": inventory_item.apn,
                "description": inventory_item.full_description,
                "price_rule": price_rule.code
            }
            for i in range(5):
                if i > 0:
                    row["quantity_{}".format(i)] = getattr(
                        price_region_item, "quantity_{}".format(i))
                price_now = getattr(price_region_item, "price_{}".format(i))
                price_diff = price_diffs[i]
                price_was = price_now - price_diff
                price_diff_percentage = None
                if price_was > 0:
                    price_diff_percentage = (
                        price_diff / price_was).quantize(price_now)
                row["price_{}_was".format(i)] = price_now - price_diff
                row["price_{}_now".format(i)] = price_now
                row["price_{}_diff".format(i)] = price_diff
                row["price_{}_diff_percentage".format(
                    i)] = price_diff_percentage
            yield row

    report_writer.write_sheet("Price Changes", price_change_fields,
                              price_change_rows(price_changes))

    contract_item_fields = [
        string_field("contract", "Contract", 20),
        string_field("item_code", "Item Code", 20),
        string_field("description", "Description", 80),
        number_field("retail_price", "Retail Price"),
        number_field("retail_price_diff", "Price Diff"),
        number_field("retail_price_diff_percentage", "Price Diff %",
                     number_format="0%"),
    ]
    for i in range(1, 7):
        contract_item_fields.append(number_field(
            "price_{}".format(i), "Price {}".format(i)))
    report_writer.write_sheet("Contract Changes", contract_item_fields,
                              contract_item_rows(price_changes))
    report_writer.save()


def export_supplier_price_changes_report(filepath, price_changes, uom_errors):
    """Export supplier price report to file."""
    report_writer = ReportWriter(filepath)

    price_change_fields = [
        string_field("item_code", "Item Code", 20),
        string_field("supplier", "Supplier", 8),
        string_field("brand", "Brand", 7),
        string_field("apn", "APN", 20),
        string_field("description", "Description", 80),
        number_field("price_was", "Price Was", number_format="0.00"),
        number_field("price_now", "Price Now", number_format="0.00"),
        number_field("price_diff", "Price Diff", number_format="0.00"),
        number_field("price_diff_percentage",
                     "Price Diff %", number_format="0%"),
    ]

    def price_change_rows(price_changes):
        for price_change in price_changes:
            supplier_item = price_change["supplier_item"]
            price_was = price_change["price_was"]
            price_now = price_change["price_now"]
            price_diff = price_change["price_diff"]
            price_diff_percentage = price_change["price_diff_percentage"]
            inventory_item = supplier_item.inventory_item
            row = {
                "item_code": inventory_item.code,
                "supplier": supplier_item.code,
                "brand": inventory_item.brand,
                "apn": inventory_item.apn,
                "description": inventory_item.full_description,
                "price_was": price_was,
                "price_now": price_now,
                "price_diff": price_diff,
                "price_diff_percentage": price_diff_percentage,
            }
            yield row

    report_writer.write_sheet("Price Changes", price_change_fields,
                              price_change_rows(price_changes))

    uom_error_fields = [
        string_field("item_code", "Item Code", 20),
        string_field("supplier", "Supplier", 8),
        string_field("brand", "Brand", 7),
        string_field("apn", "APN", 20),
        string_field("description", "Description", 80),
        string_field("message", "Error", 48),
        string_field("expected", "Expected", 20),
        string_field("actual", "Actual", 20),
    ]

    def uom_error_rows(uom_errors):
        for uom_error in uom_errors:
            supplier_item = uom_error["supplier_item"]
            inventory_item = supplier_item.inventory_item
            row = {
                "item_code": inventory_item.code,
                "supplier": supplier_item.code,
                "brand": inventory_item.brand,
                "apn": inventory_item.apn,
                "description": inventory_item.full_description,
                "message": uom_error["message"],
                "expected": uom_error["expected"],
                "actual": uom_error["actual"],
            }
            yield row

    report_writer.write_sheet("UOM Errors", uom_error_fields,
                              uom_error_rows(uom_errors))

    report_writer.save()


def contract_item_rows(price_changes):
    for price_change in price_changes:
        price_region_item = price_change.price_region_item
        price_diffs = price_change.price_diffs
        inventory_item = price_region_item.inventory_item
        contract_items = inventory_item.contract_items
        if not contract_items:
            continue
        for contract_item in contract_items:
            price_now = price_region_item.price_0
            price_diff = price_diffs[0]
            price_was = price_now - price_diff
            price_diff_percentage = None
            if price_was > 0:
                price_diff_percentage = (
                    price_diff / price_was).quantize(price_now)
            row = {
                "contract": contract_item.code,
                "item_code": inventory_item.code,
                "description": inventory_item.full_description,
                "retail_price": price_region_item.price_0,
                "retail_price_diff": price_diff,
                "retail_price_diff_percentage": price_diff_percentage,
            }
            for i in range(1, 7):
                price = getattr(contract_item, "price_{}".format(i))
                row["price_{}".format(i)] = price
            yield row


def export_product_price_task(filepath, price_region_items):
    """Export product price update task to file."""
    def price_region_item_to_row(price_region_item):
        inventory_item = price_region_item.inventory_item
        row = {
            "item_code": inventory_item.code,
            "region": price_region_item.code,
        }
        for i in range(5):
            fieldname = "price_{}".format(i)
            row[fieldname] = getattr(price_region_item, fieldname)
        return row
    rows = [price_region_item_to_row(item) for item in price_region_items]

    with open(filepath, "w") as file:
        fieldnames = ["item_code", "region"] + [
            "price_{}".format(i) for i in range(5)]
        writer = csv.DictWriter(file, fieldnames, dialect="excel-tab")
        writer.writeheader()
        writer.writerows(rows)


def export_product_web_sortcode_task(filepath, inventory_items):
    """Export product web sortcode update task to file."""
    def inventory_item_to_row(inventory_item):
        return {
            "item_code": inventory_item.code,
            "web_active": inventory_item.web_status.value,
            "web_sortcode": inventory_item.web_sortcode,
        }
    rows = [inventory_item_to_row(item) for item in inventory_items]

    with open(filepath, "w") as file:
        fieldnames = ["item_code", "web_active", "web_sortcode"]
        writer = csv.DictWriter(file, fieldnames, dialect="excel-tab")
        writer.writeheader()
        writer.writerows(rows)


def export_contract_item_task(filepath, contract_items):
    """Export product price update task to file."""
    def contract_item_to_row(contract_item):
        inventory_item = contract_item.inventory_item
        row = {
            "contract": contract_item.code,
            "item_code": inventory_item.code,
        }
        for i in range(1, 7):
            fieldname = "price_{}".format(i)
            row[fieldname] = getattr(contract_item, fieldname)
        return row
    rows = [contract_item_to_row(item) for item in contract_items]

    with open(filepath, "w") as file:
        fieldnames = ["contract", "item_code"]
        for i in range(1, 7):
            fieldnames.append("price_{}".format(i))
        writer = csv.DictWriter(file, fieldnames, dialect="excel-tab")
        writer.writeheader()
        writer.writerows(rows)


def export_supplier_pricelist(filepath, supplier_items):
    """Export supplier items to Pronto SPL file."""

    exported_item_codes = []
    duplicate_supplier_pricelist_items = []

    def supplier_item_to_row(supplier_item):
        item_code = supplier_item.item_code
        if item_code not in exported_item_codes:
            exported_item_codes.append(item_code)
        else:
            duplicate_supplier_pricelist_items.append(supplier_item)
        inventory_item = supplier_item.inventory_item
        row = {
            "supplier_code": supplier_item.code,
            "supp_item_code": supplier_item.item_code,
            "desc_line_1": inventory_item.description_line_1,
            "desc_line_2": inventory_item.description_line_2,
            "supp_uom": supplier_item.uom,
            "supp_eoq": supplier_item.moq,
            "supp_conv_factor": supplier_item.conv_factor,
            "supp_price_1": supplier_item.buy_price,
            "item_code": inventory_item.code,
        }
        return row
    rows = [supplier_item_to_row(item) for item in supplier_items]

    if len(duplicate_supplier_pricelist_items) > 0:
        print("  Warning: {} exported records will be overridden on import.".format(
            len(duplicate_supplier_pricelist_items)))

    with open(filepath, "w") as file:
        fieldnames = SPL_FIELDNAMES
        writer = csv.DictWriter(file, fieldnames, dialect="excel")
        writer.writerows(rows)


def export_tickets_list(filepath, warehouse_stock_items):
    """Export tickets list to file."""
    def stocked_item_codes(warehouse_stock_items):
        for item in warehouse_stock_items:
            item_code = item.inventory_item.code
            if item.bin_location:
                yield item_code
            elif item.on_hand:
                yield item_code
            elif item.minimum:
                yield item_code

    item_codes = stocked_item_codes(warehouse_stock_items)
    lines = ["{}\n".format(item_code) for item_code in item_codes]
    with open(filepath, "w") as file:
        file.writelines(lines)


def sell_price_change(product):
    """Calculates ratio between old and new level 0 sell prices."""
    was_sell_price = product.was_sell_prices[0]
    now_sell_price = product.sell_prices[0]
    diff = now_sell_price - was_sell_price
    return diff / was_sell_price


def string_field(name, title, width):
    return {
        "name": name,
        "title": title,
        "width": width,
        "align": "left",
    }


def number_field(name, title, number_format="0.0000"):
    return {
        "name": name,
        "title": title,
        "width": 16,
        "align": "right",
        "number_format": number_format,
    }
