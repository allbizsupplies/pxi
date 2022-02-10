
from decimal import Decimal
from sqlalchemy import (
    Column, UniqueConstraint,
    Date, DateTime, Enum, ForeignKey, Integer, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from pxi.enum import ItemType, ItemCondition, PriceBasis, TaxCode


Base = declarative_base()


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(16), unique=True, nullable=False)
    description_line_1 = Column(String(30), nullable=False)
    description_line_2 = Column(String(30))
    description_line_3 = Column(String(30))
    uom = Column(String(4), nullable=False)
    brand = Column(String(3))
    apn = Column(String(20))
    group = Column(String(4))
    item_type = Column(Enum(ItemType), nullable=False)
    condition = Column(Enum(ItemCondition))
    created = Column(DateTime)
    replacement_cost = Column(String(16), nullable=False)

    contract_items = relationship("ContractItem",
                                  back_populates="inventory_item")

    price_region_items = relationship("PriceRegionItem",
                                      back_populates="inventory_item")

    warehouse_stock_items = relationship("WarehouseStockItem",
                                         back_populates="inventory_item")

    supplier_items = relationship("SupplierItem",
                                  back_populates="inventory_item")

    gtin_items = relationship("GTINItem",
                              back_populates="inventory_item")

    inventory_web_data_item = relationship("InventoryWebDataItem",
                                           back_populates="inventory_item",
                                           uselist=False)

    def __repr__(self):
        return f"<InventoryItem(code='{self.code}')>"

    @property
    def default_price_region_item(self):
        for price_region_item in self.price_region_items:
            if price_region_item.in_default_price_region:
                return price_region_item
        return None

    @property
    def full_description(self):
        full_description = self.description_line_1
        if self.description_line_2:
            full_description += " " + self.description_line_2
        if self.description_line_3:
            full_description += " " + self.description_line_3
        return full_description


class PriceRule(Base):
    __tablename__ = "price_rules"

    id = Column(Integer, primary_key=True)
    code = Column(String(4), unique=True, nullable=False)
    description = Column(String(30), nullable=False)
    price_0_basis = Column(Enum(PriceBasis), nullable=False)
    price_1_basis = Column(Enum(PriceBasis), nullable=False)
    price_2_basis = Column(Enum(PriceBasis), nullable=False)
    price_3_basis = Column(Enum(PriceBasis), nullable=False)
    price_4_basis = Column(Enum(PriceBasis), nullable=False)
    rrp_excl_basis = Column(Enum(PriceBasis), nullable=False)
    rrp_incl_basis = Column(Enum(PriceBasis), nullable=False)
    price_0_factor = Column(String(16), nullable=False)
    price_1_factor = Column(String(16), nullable=False)
    price_2_factor = Column(String(16), nullable=False)
    price_3_factor = Column(String(16), nullable=False)
    price_4_factor = Column(String(16), nullable=False)
    rrp_excl_factor = Column(String(16), nullable=False)
    rrp_incl_factor = Column(String(16), nullable=False)

    price_region_items = relationship("PriceRegionItem",
                                      back_populates="price_rule")

    def price_basis(self, level):
        return getattr(self, f"price_{level}_basis")

    def price_factor(self, level):
        return getattr(self, f"price_{level}_factor")

    def __repr__(self):
        return f"<PriceRule(code='{self.code}')>"


class PriceRegionItem(Base):
    PRICE_LEVELS = 5
    DEFAULT_REGION_CODE = ""
    __tablename__ = "price_region_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(2), nullable=False)
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    price_rule_id = Column(Integer, ForeignKey("price_rules.id"))
    tax_code = Column(Enum(TaxCode))
    quantity_1 = Column(String(14), nullable=False)
    quantity_2 = Column(String(14), nullable=False)
    quantity_3 = Column(String(14), nullable=False)
    quantity_4 = Column(String(14), nullable=False)
    price_0 = Column(String(16), nullable=False)
    price_1 = Column(String(16), nullable=False)
    price_2 = Column(String(16), nullable=False)
    price_3 = Column(String(16), nullable=False)
    price_4 = Column(String(16), nullable=False)
    rrp_excl_tax = Column(String(16), nullable=False)
    rrp_incl_tax = Column(String(15), nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "inventory_item_id"),
    )

    inventory_item = relationship("InventoryItem",
                                  back_populates="price_region_items")

    price_rule = relationship("PriceRule",
                              back_populates="price_region_items")

    @property
    def in_default_price_region(self):
        return self.code == self.DEFAULT_REGION_CODE

    def quantity(self, level: int):
        return Decimal(getattr(self, f"quantity_{level}"))

    def price(self, level: int):
        return Decimal(getattr(self, f"price_{level}"))

    def set_price(self, level: int, value: Decimal):
        setattr(self, f"price_{level}", str(value))

    def __repr__(self):
        return (f"<PriceRegionItem(code='{self.code}',"
                f" inventory_item='{self.inventory_item.code}')>")


class ContractItem(Base):
    PRICE_LEVELS = 6
    __tablename__ = "contract_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    price_1 = Column(String(11), nullable=False)
    price_2 = Column(String(11), nullable=False)
    price_3 = Column(String(11), nullable=False)
    price_4 = Column(String(11), nullable=False)
    price_5 = Column(String(11), nullable=False)
    price_6 = Column(String(11), nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "inventory_item_id"),
    )

    inventory_item = relationship("InventoryItem",
                                  back_populates="contract_items")

    def price(self, level: int):
        return Decimal(getattr(self, f"price_{level}"))

    def set_price(self, level: int, value: Decimal):
        setattr(self, f"price_{level}", str(value))

    def __repr__(self):
        return f"<ContractItem(code='{self.code}')>"


class WarehouseStockItem(Base):
    __tablename__ = "warehouse_stock_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(2), nullable=False)
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    on_hand = Column(Integer, nullable=False)
    minimum = Column(Integer, nullable=False)
    maximum = Column(Integer, nullable=False)
    bin_location = Column(String(8))
    bulk_location = Column(String(8))

    __table_args__ = (
        UniqueConstraint("code", "inventory_item_id"),
    )

    inventory_item = relationship("InventoryItem",
                                  back_populates="warehouse_stock_items")

    def __repr__(self):
        return f"<WarehouseStockItem(code='{self.code}')>"


class SupplierItem(Base):
    __tablename__ = "supplier_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False)
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    item_code = Column(String(2), nullable=False)
    priority = Column(Integer, nullable=False)
    uom = Column(String(4), nullable=False)
    conv_factor = Column(String(14), nullable=False)
    pack_quantity = Column(Integer, nullable=False)
    moq = Column(Integer, nullable=False)
    buy_price = Column(String(11), nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "inventory_item_id"),
    )

    inventory_item = relationship("InventoryItem",
                                  back_populates="supplier_items")

    def __repr__(self):
        return (f"<SupplierItem(code='{self.code}',"
                f" item_code='{self.item_code}',"
                f" inventory_item.code='{self.inventory_item.code}')>")


class GTINItem(Base):
    __tablename__ = "gtin_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(2))
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    uom = Column(String(4), nullable=False)
    conv_factor = Column(String(14), nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "inventory_item_id", "uom"),
    )

    inventory_item = relationship("InventoryItem",
                                  back_populates="gtin_items")

    def __repr__(self):
        return f"<GTINItem(code='{self.code}')>"

    @property
    def is_numeric_code(self):
        try:
            int(self.code)
            return True
        except ValueError:
            pass
        return False

    @property
    def is_barcode(self):
        if not self.is_numeric_code:
            return False
        return len(self.code) >= 8 and len(self.code) <= 14

    @property
    def is_unit_barcode(self):
        if not self.is_barcode:
            return False
        return self.conv_factor == 1


class WebMenuItem(Base):
    __tablename__ = "web_menu_items"

    id = Column(Integer, primary_key=True)
    parent_name = Column(String(255), nullable=False)
    child_name = Column(String(255), nullable=False)

    inventory_web_data_items = relationship("InventoryWebDataItem",
                                            back_populates="web_menu_item")

    @property
    def name(self):
        return f"{self.parent_name}/{self.child_name}"

    __table_args__ = (
        UniqueConstraint("parent_name", "child_name"),
    )

    def __repr__(self):
        return f"<WebMenuItem(name='{self.name}')>"


class InventoryWebDataItem(Base):
    __tablename__ = "inventory_web_data_items"

    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    web_menu_item_id = Column(Integer,
                              ForeignKey("web_menu_items.id"), nullable=True)

    inventory_item = relationship("InventoryItem",
                                  back_populates="inventory_web_data_item")

    web_menu_item = relationship("WebMenuItem",
                                 back_populates="inventory_web_data_items")

    def __repr__(self):
        return f"<InventoryWebDataItem(item='{self.inventory_item.code}')>"


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    path = Column(String(255))
    modified = Column(DateTime)
