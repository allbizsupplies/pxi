#!/bin/bash
#
# Upload SPL file to Pronto server.
# Requires that Pronto server be added to SSH config as "pronto"
scp "data/export/supplier_pricelist.csv" "pronto:/home/albbrad/import/supplier_pricelist.csv"
