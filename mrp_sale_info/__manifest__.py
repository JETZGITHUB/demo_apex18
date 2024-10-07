# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Sale Info",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
        "sale_stock",
        "manufacter_rck",
        "report_xlsx",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production.xml",
    ],
}
