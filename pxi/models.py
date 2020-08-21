
from sqlalchemy import (
    Column, UniqueConstraint,
    Date, DateTime, Enum, ForeignKey, Numeric, Integer, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from pxi.enum import ItemType, ItemCondition, PriceBasis, WebStatus, TaxCode


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
    group = Column(String(4), nullable=False)
    item_type = Column(Enum(ItemType), nullable=False)
    condition = Column(Enum(ItemCondition))
    created = Column(DateTime, nullable=False)
    replacement_cost = Column(Numeric(precision=15, scale=4), nullable=False)

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

    def __repr__(self):
        return "<InventoryItem(code='{}')>".format(self.code)

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
    price_0_factor = Column(Numeric(precision=15, scale=4), nullable=False)
    price_1_factor = Column(Numeric(precision=15, scale=4), nullable=False)
    price_2_factor = Column(Numeric(precision=15, scale=4), nullable=False)
    price_3_factor = Column(Numeric(precision=15, scale=4), nullable=False)
    price_4_factor = Column(Numeric(precision=15, scale=4), nullable=False)
    rrp_excl_factor = Column(Numeric(precision=15, scale=4), nullable=False)
    rrp_incl_factor = Column(Numeric(precision=15, scale=4), nullable=False)

    price_region_items = relationship("PriceRegionItem",
                                      back_populates="price_rule")

    def __repr__(self):
        return "<PriceRule(code='{}')>".format(self.code)


class PriceRegionItem(Base):
    __tablename__ = "price_region_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(2), nullable=False)
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    price_rule_id = Column(Integer, ForeignKey("price_rules.id"))
    tax_code = Column(Enum(TaxCode))
    quantity_1 = Column(Numeric(precision=13, scale=4), nullable=False)
    quantity_2 = Column(Numeric(precision=13, scale=4), nullable=False)
    quantity_3 = Column(Numeric(precision=13, scale=4), nullable=False)
    quantity_4 = Column(Numeric(precision=13, scale=4), nullable=False)
    price_0 = Column(Numeric(precision=15, scale=4), nullable=False)
    price_1 = Column(Numeric(precision=15, scale=4), nullable=False)
    price_2 = Column(Numeric(precision=15, scale=4), nullable=False)
    price_3 = Column(Numeric(precision=15, scale=4), nullable=False)
    price_4 = Column(Numeric(precision=15, scale=4), nullable=False)
    rrp_excl_tax = Column(Numeric(precision=15, scale=4), nullable=False)
    rrp_incl_tax = Column(Numeric(precision=14, scale=2), nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "inventory_item_id"),
    )

    inventory_item = relationship("InventoryItem",
                                  back_populates="price_region_items")

    price_rule = relationship("PriceRule",
                              back_populates="price_region_items")

    def __repr__(self):
        return "<PriceRegionItem(code='{}')>".format(self.code)


class ContractItem(Base):
    __tablename__ = "contract_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    price_1 = Column(Numeric(precision=10, scale=4), nullable=False)
    price_2 = Column(Numeric(precision=10, scale=4), nullable=False)
    price_3 = Column(Numeric(precision=10, scale=4), nullable=False)
    price_4 = Column(Numeric(precision=10, scale=4), nullable=False)
    price_5 = Column(Numeric(precision=10, scale=4), nullable=False)
    price_6 = Column(Numeric(precision=10, scale=4), nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "inventory_item_id"),
    )

    inventory_item = relationship("InventoryItem",
                                  back_populates="contract_items")

    def __repr__(self):
        return "<ContractItem(code='{}')>".format(self.code)


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
        return "<WarehouseStockItem(code='{}')>".format(self.code)


class SupplierItem(Base):
    __tablename__ = "supplier_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False)
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    item_code = Column(String(2), nullable=False)
    priority = Column(Integer, nullable=False)
    uom = Column(String(4), nullable=False)
    conv_factor = Column(Numeric(precision=13, scale=7), nullable=False)
    pack_quantity = Column(Integer, nullable=False)
    moq = Column(Integer, nullable=False)
    buy_price = Column(Numeric(precision=10, scale=4), nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "inventory_item_id"),
    )

    inventory_item = relationship("InventoryItem",
                                  back_populates="supplier_items")

    def __repr__(self):
        return "<SupplierItem(code='{}', item_code='{}', inventory_item.code='{}')>".format(
            self.code, self.item_code, self.inventory_item.code)


class GTINItem(Base):
    __tablename__ = "gtin_items"

    id = Column(Integer, primary_key=True)
    code = Column(String(2))
    inventory_item_id = Column(Integer,
                               ForeignKey("inventory_items.id"), nullable=False)
    uom = Column(String(4), nullable=False)
    conv_factor = Column(Numeric(precision=13, scale=7), nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "inventory_item_id", "uom"),
    )

    inventory_item = relationship("InventoryItem",
                                  back_populates="gtin_items")

    def __repr__(self):
        return "<GTINItem(code='{}')>".format(self.code)
