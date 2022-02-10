
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from pxi.models import InventoryItem, PriceRegionItem, SupplierItem


@dataclass
class SupplierPricelistItem:
    item_code: str
    supp_code: str
    supp_item_code: str
    supp_price: Decimal
    supp_uom: str
    supp_sell_uom: str
    supp_eoq: str
    supp_conv_factor: Decimal


@dataclass
class SellPriceChange:
    price_region_item: PriceRegionItem
    price_diffs: List[Decimal] = field(default_factory=list)

    @property
    def price_differs(self):
        for price_diff in self.price_diffs:
            if abs(price_diff) >= Decimal("0.005"):
                return True
        return False

    @property
    def price_0_differs(self):
        return abs(self.price_diffs[0]) >= Decimal("0.005")


@dataclass
class BuyPriceChange:
    supplier_item: SupplierItem
    price_was: Decimal
    price_now: Decimal

    @property
    def price_diff(self):
        return self.price_was - self.price_now

    @property
    def price_diff_abs(self):
        return abs(self.price_diff)

    @property
    def price_diff_percentage(self):
        if self.price_was != 0:
            return self.price_diff / self.price_was


@dataclass
class UOMError:
    supplier_item: SupplierItem
    message: str
    spl_item_code: str
    expected: str
    actual: str


@dataclass
class InventoryItemImageFile:
    inventory_item: InventoryItem
    filename: str
