
import json
from pxi.datagrid import load_rows
import yaml


def to_dict(row):
    return {
        "code": row["rule"],
        "label": row["comments"],
        "margins": [row[f"price{i}_factor"] for i in range(5)]
    }


def main():
    with open("config.yml") as file:
        config = yaml.safe_load(file)
    datagrid_filepath = config["paths"]["import"]["price_rules_datagrid"]
    rows = load_rows(datagrid_filepath)
    data = [to_dict(row) for row in rows]
    json_filepath = config["paths"]["export"]["price_rules_json"]
    with open(json_filepath, "w") as file:
        json.dump(data, file)


if __name__ == "__main__":
    main()
