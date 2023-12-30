import pandas as pd

pd.set_option('display.width', 800)
pd.set_option('display.max_columns', 60)
pd.set_option('mode.chained_assignment', None)

"""
Collect trade confirmation JSON from /src/config.py TRADES_JSON_DIR 
Save monthly `YYYY-MM Statement.xlsx` to /src/config.py DESTINATION_DIR  

Excel files have the columns:
*Date, *Amount, Payee, Description, Reference, Transaction Type, Account Code, Tax Rate
"""


