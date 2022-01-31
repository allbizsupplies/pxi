
from datetime import datetime
from decimal import Decimal
from random import randint, choice as random_choice
import string
import time

from pxi.data import (
    BuyPriceChange,
    SellPriceChange,
    SupplierPricelistItem)
from pxi.enum import (
    ItemCondition,
    ItemType,
    PriceBasis,
    TaxCode)
from pxi.models import (
    ContractItem,
    GTINItem,
    InventoryItem,
    InventoryWebDataItem,
    PriceRegionItem,
    PriceRule,
    SupplierItem,
    WarehouseStockItem,
    WebSortcode)


def random_description(length=30):
    """
    Makes a random description.
    """
    return random_string(30)


def random_datetime(start=None, end=None):
    """
    Makes a random datetime between two given datetimes.
    """
    if start is None:
        start = datetime.fromtimestamp(0)
    if end is None:
        end = datetime.now()
    return datetime.fromtimestamp(randint(
        int(time.mktime(start.timetuple())),
        int(time.mktime(end.timetuple()))))


def random_item_code():
    """
    Makes a random item code.
    """
    return random_string(16)


def random_price():
    """
    Makes a random price.
    """
    return Decimal(random_price_string())


def random_price_factor():
    """
    Makes a random price multiplication factor with format '0.00'.
    """
    return f"{randint(1, 5)}.{(randint(0, 19) * 5):02d}"


def random_price_string():
    """
    Makes a random price string with format '0.00'.
    """
    return f"{randint(1, 100)}.{randint(0, 99):02d}"


def random_quantity():
    """
    Makes a random quantity between 0 and 999999, inclusive.
    """
    return str(randint(0, 999999))


def random_string(length):
    """
    Makes a random string of uppercase ASCII letters.
    """
    return "".join([
        random_choice(string.ascii_uppercase) for x in range(length)])


def random_uom(length=4):
    """
    Makes a random unit of measure.
    """
    return random_string(length)


def fake_inventory_item(values={}):
    """
    Makes a fake InventoryItem.
    """
    return InventoryItem(
        code=values.get("code", random_item_code()),
        description_line_1=values.get(
            "description_line_1", random_description()),
        description_line_2=values.get(
            "description_line_2", random_description()),
        description_line_3=values.get(
            "description_line_3", random_description()),
        uom=values.get("uom", random_uom()),
        brand=values.get("brand", random_string(3)),
        apn=values.get("apn", random_string(20)),
        group=values.get("group", random_string(2)),
        item_type=values.get("item_type", ItemType.STOCKED_ITEM),
        condition=values.get("condition", ItemCondition.NONE),
        created=values.get("created", random_datetime()),
        replacement_cost=values.get("replacement_cost", random_price()))


def fake_contract_item(inventory_item, values={}):
    """
    Makes a fake ContractItem.
    """
    return ContractItem(
        inventory_item=inventory_item,
        code=values.get("code", random_string(6)),
        price_1=values.get("price_1", random_price()),
        price_2=values.get("price_2", random_price()),
        price_3=values.get("price_3", random_price()),
        price_4=values.get("price_4", random_price()),
        price_5=values.get("price_5", random_price()),
        price_6=values.get("price_6", random_price()))


def fake_warehouse_stock_item(inventory_item, values={}):
    """
    Makes a fake WarehouseStockItem.
    """
    return WarehouseStockItem(
        inventory_item=inventory_item,
        code=values.get("code", random_string(4)),
        on_hand=values.get("on_hand", random_quantity()),
        minimum=values.get("minimum", random_quantity()),
        maximum=values.get("maximum", random_quantity()),
        bin_location=values.get("bin_location", random_string(8)),
        bulk_location=values.get("bulk_location", random_string(8)))


def fake_price_rule(values={}):
    """
    Makes a fake PriceRule.
    """
    return PriceRule(
        code=values.get("code", random_string(4)),
        description=values.get("description", random_description()),
        price_0_basis=values.get("_basis", PriceBasis.REPLACEMENT_COST),
        price_1_basis=values.get("_basis", PriceBasis.REPLACEMENT_COST),
        price_2_basis=values.get("_basis", PriceBasis.REPLACEMENT_COST),
        price_3_basis=values.get("_basis", PriceBasis.REPLACEMENT_COST),
        price_4_basis=values.get("_basis", PriceBasis.REPLACEMENT_COST),
        rrp_excl_basis=values.get("rrp_excl_basis", PriceBasis.RRP_EXCL_TAX),
        rrp_incl_basis=values.get("rrp_incl_basis", PriceBasis.RRP_INCL_TAX),
        price_0_factor=values.get("_factor", random_price_factor()),
        price_1_factor=values.get("_factor", random_price_factor()),
        price_2_factor=values.get("_factor", random_price_factor()),
        price_3_factor=values.get("_factor", random_price_factor()),
        price_4_factor=values.get("_factor", random_price_factor()),
        rrp_excl_factor=values.get("rrp_excl_factor", 0),
        rrp_incl_factor=values.get("rrp_incl_factor", 0))


def fake_price_region_item(inventory_item, price_rule, values={}):
    """
    Makes a fake PriceRegionitem.
    """
    return PriceRegionItem(
        inventory_item=inventory_item,
        price_rule=price_rule,
        code=values.get("code", random_string(4)),
        tax_code=values.get("tax_code", TaxCode.TAXABLE),
        quantity_1=values.get("quantity_1", random_quantity()),
        quantity_2=values.get("quantity_2", random_quantity()),
        quantity_3=values.get("quantity_3", random_quantity()),
        quantity_4=values.get("quantity_4", random_quantity()),
        price_0=values.get("price_0", random_price()),
        price_1=values.get("price_1", random_price()),
        price_2=values.get("price_2", random_price()),
        price_3=values.get("price_3", random_price()),
        price_4=values.get("price_4", random_price()),
        rrp_excl_tax=values.get("rrp_excl_tax", 0),
        rrp_incl_tax=values.get("rrp_incl_tax", 0))


def fake_supplier_item(inventory_item, values={}):
    """
    Makes a fake SupplierItem.
    """
    return SupplierItem(
        inventory_item=inventory_item,
        code=values.get("code", random_string(3)),
        item_code=values.get("item_code", random_item_code()),
        priority=values.get("priority", randint(1, 9)),
        uom=values.get("uom", random_uom()),
        conv_factor=values.get("conv_factor", 1),
        pack_quantity=values.get("pack_quantity", 1),
        moq=values.get("moq", 1),
        buy_price=values.get("buy_price", random_price()))


def fake_gtin_item(inventory_item, values={}):
    """
    Makes a fake GTINItem.
    """
    return GTINItem(
        inventory_item=inventory_item,
        code=values.get("code", random_item_code()),
        uom=values.get("uom", random_uom()),
        conv_factor=values.get("conv_factor", 1))


def fake_web_sortcode(values={}):
    """
    Makes a fake WebSortcode.
    """
    return WebSortcode(
        parent_name=values.get("parent_name", random_string(20)),
        child_name=values.get("child_name", random_string(20)))


def fake_inv_web_data_item(inventory_item, web_sortcode, values={}):
    """
    Makes a fake InventoryWebDataItem.
    """
    return InventoryWebDataItem(
        inventory_item=inventory_item,
        web_sortcode=web_sortcode,
        description=values.get("description", random_string(20)))


def fake_supplier_pricelist_item(supplier_item, values={}):
    return SupplierPricelistItem(
        item_code=values.get("item_code", supplier_item.inventory_item.code),
        supp_code=values.get("supp_code", supplier_item.code),
        supp_item_code=values.get("supp_item_code", supplier_item.item_code),
        supp_conv_factor=values.get(
            "supp_conv_factor", Decimal(supplier_item.conv_factor)),
        supp_price=values.get("supp_price", Decimal(supplier_item.buy_price)),
        supp_uom=values.get("supp_uom", supplier_item.uom),
        supp_sell_uom=values.get(
            "supp_sell_uom", supplier_item.inventory_item.uom),
        supp_eoq=values.get("supp_eoq", supplier_item.moq))


def fake_sell_price_change(price_region_item, values={}):
    return SellPriceChange(
        price_region_item,
        values.get("price_diffs", [
            random_price(),
            random_price(),
            random_price(),
            random_price(),
            random_price(),
        ]))


def fake_buy_price_change(supplier_item, values={}):
    return BuyPriceChange(
        supplier_item,
        values.get("price_was", random_price()),
        values.get("price_now", random_price()))
