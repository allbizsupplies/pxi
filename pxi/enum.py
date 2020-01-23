from enum import Enum


class ItemType(Enum):
    STOCKED_ITEM = "S"
    INDENT_ITEM = "I"
    KIT_ITEM = "K"
    LABOUR = "L"
    CROSS_REFERENCE = "X"
    SPECIAL = "Z"


class ItemCondition(Enum):
    NONE = None
    NORMAL = "A"
    PURCHASE_STOP = "C"
    FREIGHT = "F"
    NO_BACKORDERS = "L"
    NO_SUPPLY = "N"
    INACTIVE = "I"
    OBSOLETE = "O"
    DISCONTINUED = "T"


class PriceBasis(Enum):
    REPLACEMENT_COST = "C"
    AVERAGE_COST = "A"
    RRP_EXCL_TAX = "R"
    RRP_INCL_TAX = "R1"
    EXISTING_PRICE_0 = "E"
    EXISTING_PRICE_1 = "P"
    EXISTING_PRICE_2 = "Q"
    EXISTING_PRICE_3 = "U"
    EXISTING_PRICE_4 = "V"


class TaxCode(Enum):
    TAXABLE = "G"
    EXEMPT = "E"


class WebStatus(Enum):
    ACTIVE = "Y"
    INACTIVE = "N"
