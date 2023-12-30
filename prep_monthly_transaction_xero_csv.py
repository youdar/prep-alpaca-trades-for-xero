import pandas as pd
from src import TradeConfirmationTools

pd.set_option('display.width', 800)
pd.set_option('display.max_columns', 60)
pd.set_option('mode.chained_assignment', None)

"""
Collect trade confirmation JSON from /src/config.py TRADES_JSON_DIR 
Save monthly `YYYY-MM Statement.xlsx` to /src/config.py DESTINATION_DIR  

Excel files have the columns:
*Date, *Amount, Payee, Description, Reference, Transaction Type, Account Code, Tax Rate
"""


def prep_monthly_transaction_xero_csv():
    o = TradeConfirmationTools()
    print(f"Collecting data from {o.json_dir}")
    df = o.read_json_files()
    print(f"Collected data size: {df.shape}")
    print(f"Creating Excel files in {o.destination_dir}")
    _, periods = o.write_excel_monthly_data()
    print(f"Collected periods {', '.join(periods)}")
    print('Done...')


if __name__ == '__main__':
    prep_monthly_transaction_xero_csv()
