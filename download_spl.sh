#!/bin/bash
#
# Download SPL file from Pronto server.
# Requires that Pronto server be added to SSH config as "pronto"
supplier_code=$1
scp "pronto:/oclimport/supplierpricelist/SPL2019${supplier_code}.PRN" "data/import/supplier_pricelist.csv"
