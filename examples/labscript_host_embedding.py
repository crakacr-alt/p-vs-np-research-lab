from pnp_lab.labscript import LabRuntime, ModuleNamespace


# Host сам решает, какие функции разрешить LabScript.
company = ModuleNamespace(
    "company",
    {
        "price_with_tax": lambda price: round(price * 1.2, 2),
        "project_name": "Research Lab Demo",
    },
)

runtime = LabRuntime(modules={"company": company})

runtime.execute(
    """
LangRule="-ENG"

import company

print(company.project_name)
print(company.price_with_tax(100))
"""
)
