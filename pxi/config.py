
from typing import List, TypedDict
import yaml


class ImportPathsConfig(TypedDict):
    contract_items_datagrid: str
    inventory_items_datagrid: str
    inventory_web_data_items_datagrid: str
    gtin_items_datagrid: str
    price_rules_datagrid: str
    pricelist_datagrid: str
    supplier_items_datagrid: str
    supplier_pricelist: str
    web_menu: str
    web_menu_mappings: str
    missing_images_report: str


class ExportPathsConfig(TypedDict):
    contract_item_task: str
    downloaded_images_report: str
    gtin_report: str
    images_dir: str
    price_changes_report: str
    price_rules_json: str
    pricelist: str
    product_price_task: str
    supplier_price_changes_report: str
    tickets_list: str
    supplier_pricelist: str
    web_product_menu_data: str
    web_data_updates_report: str
    missing_images_report: str


class RemotePathsConfig(TypedDict):
    supplier_pricelist: str
    pricelist: str
    supplier_pricelist_imports: str


class PathsConfig(TypedDict):
    logging: str
    imports: ImportPathsConfig
    exports: ExportPathsConfig
    remote: RemotePathsConfig


class SSHConfig(TypedDict):
    hostname: str
    username: str
    password: str


class PriceRulesConfig(TypedDict):
    ignore: List[str]


class BinLocationsConfig(TypedDict):
    ignore: List[str]


class GTINConfig(TypedDict):
    ignore_brands: List[str]


class Config(TypedDict):
    paths: PathsConfig
    ssh: SSHConfig
    price_rules: PriceRulesConfig
    bin_locations: BinLocationsConfig
    gtin: GTINConfig


def load_config(filepath: str):
    """
    Loads config from YAML file.
    """
    with open(filepath) as file:
        config: Config = yaml.safe_load(file)
    return config
