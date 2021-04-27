from datetime import date, datetime, timedelta
from decimal import Decimal
import random
import string

from pxi.enum import (
    PriceBasis,
    ItemCondition,
    ItemType,
    TaxCode)
from pxi.models import (
    ContractItem,
    PriceRule,
    PriceRegionItem,
    InventoryItem,
    InventoryWebDataItem,
    SupplierItem,
    WarehouseStockItem,
    WebSortcode)


def random_contract(items=5):
    contract_items = []
    # pylint: disable=unused-variable
    for i in range(5):
        inventory_item = random_inventory_item()
        contract_item = random_contract_item(inventory_item)
        contract_items.append(contract_item)
    return contract_items


def random_contract_item(inventory_item):
    """Generate contract items for inventory_items"""

    return ContractItem(
        code=random_string(6),
        inventory_item=inventory_item,
        price_1=random_price(min=18, max=20),
        price_2=random_price(min=16, max=18),
        price_3=random_price(min=14, max=16),
        price_4=random_price(min=12, max=14),
        price_5=random_price(min=10, max=12),
        price_6=random_price(min=8, max=10),
    )


def random_inventory_item():
    """Generate inventory_item with randomised fields."""
    return InventoryItem(
        code=random_string(16),
        brand=random_string(3),
        apn=random_string(20),
        description_line_1=random_string(30),
        description_line_2=random_string(30),
        description_line_3=random_string(30),
        uom="EACH",
        group="NP",
        created=datetime.now(),
        item_type=ItemType.STOCKED_ITEM,
        condition=ItemCondition.NORMAL,
        replacement_cost=random_price(),
    )


def random_price(min=10, max=100):
    """Generate a Decimal number between min and max."""
    return Decimal(random.randint(min * 100, max * 100)) / 100


def random_pricelist(items=5):
    price_region_items = []
    # pylint: disable=unused-variable
    for i in range(5):
        inventory_item = random_inventory_item()
        price_rule = random_price_rule()
        price_region_item = random_price_region_item(
            inventory_item, price_rule)
        price_region_items.append(price_region_item)
    return price_region_items


def random_price_region_item(inventory_item, price_rule):
    """Generate price region item."""
    return PriceRegionItem(
        code="",
        inventory_item=inventory_item,
        price_rule=price_rule,
        tax_code=TaxCode.TAXABLE,
        quantity_1=random.randint(2, 3),
        quantity_2=random.randint(4, 6),
        quantity_3=random.randint(8, 10),
        quantity_4=random.randint(12, 24),
        price_0=Decimal("24.00"),
        price_1=Decimal("20.00"),
        price_2=Decimal("16.00"),
        price_3=Decimal("12.00"),
        price_4=Decimal("8.00"),
        rrp_excl_tax=Decimal("0.00"),
        rrp_incl_tax=Decimal("0.00")
    )


def random_price_rule():
    """Generate price rule with randomised fields."""
    base_markup = Decimal(random.randint(200, 400)) / 100
    return PriceRule(
        code=random_string(4),
        description=random_string(30),
        price_0_basis=PriceBasis.REPLACEMENT_COST,
        price_1_basis=PriceBasis.REPLACEMENT_COST,
        price_2_basis=PriceBasis.REPLACEMENT_COST,
        price_3_basis=PriceBasis.REPLACEMENT_COST,
        price_4_basis=PriceBasis.REPLACEMENT_COST,
        rrp_excl_basis=PriceBasis.RRP_EXCL_TAX,
        rrp_incl_basis=PriceBasis.RRP_INCL_TAX,
        price_0_factor=base_markup,
        price_1_factor=base_markup * Decimal("0.95"),
        price_2_factor=base_markup * Decimal("0.90"),
        price_3_factor=base_markup * Decimal("0.85"),
        price_4_factor=base_markup * Decimal("0.75"),
        rrp_excl_factor=base_markup * Decimal("0"),
        rrp_incl_factor=base_markup * Decimal("0")
    )


def random_string(length=10):
    """Generate a random string of fixed length """
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(length))


def random_supplier_item(inventory_item):
    """Generate supplier item with randomised fields."""
    pack_qty = random.randint(1, 12)
    return SupplierItem(
        code=random_string(3),
        inventory_item=inventory_item,
        item_code=random_string(16),
        priority=random.randint(1, 9),
        uom="EACH",
        conv_factor=Decimal(1),
        pack_quantity=pack_qty,
        moq=pack_qty,
        buy_price=Decimal(random.randint(200, 400)) / 100,
    )


def random_warehouse_stock_item(inventory_item):
    """Generate warehouse stock item with randomised fields."""
    return WarehouseStockItem(
        code=random_string(3),
        inventory_item=inventory_item,
        on_hand=random.randint(0, 100),
        minimum=random.randint(0, 20),
        maximum=random.randint(40, 60),
        bin_location=random_string(8),
        bulk_location=random_string(8),
    )


def random_web_sortcode():
    """Generate web sortcode with randomised fields."""
    parent_name = random_string(30)
    child_name = random_string(30)
    return WebSortcode(
        parent_name=parent_name,
        child_name=child_name,
    )


def random_inventory_web_data_item(inventory_item, web_sortcode):
    """Generate inventory web data with randomised fields."""
    return InventoryWebDataItem(
        description=random_string(90),
        inventory_item=inventory_item,
        web_sortcode=web_sortcode
    )
