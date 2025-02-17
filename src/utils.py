import alpaca_trade_api as tradeapi
from my_secrets import get_secret
import pandas as pd

"""
Create a tool that utilizes alpaca-trade-api to collect monthly trades
xlsx and csv files that can be uploaded into Xero accounting software 
(CSV need to be kept to allow upload to Xero).


The JSON file we currently process looks like:
---
{
  "creation_date": "2024-01-03",
  "correspondent": "LPCA",
  "account_no": "899603974",
  "master_account_no": "899603974",
  "account_name": "Youval Dar",
  "representative": "Alpaca",
  "currency": "USD",
  "trade_activities": [
    {
      "symbol": "TSLA",
      "cusip": "88160R101",
      "side": "buy",
      "qty": "111",
      "price": "248.6077",
      "gross_amount": "27595.45",
      "fees": [],
      "net_amount": "27595.45",
      "trade_date": "2024-01-02",
      "trade_time": "10:15:17.741",
      "settle_date": "2024-01-04",
      "asset_type": "E",
      "note": "",
      "status": "executed",
      "capacity": "agency",
      "execution_id": "1251225103782",
      "order_id": "c6463c1a-c9f6-410c-b7dc-6665965948ad"
    },
    ...
}
---

The result CSV need to look like
---
Date	Amount	Payee	Description	Reference	Transaction Type	Account Code	Tax Rate
10/9/23	-1238.05	Alpaca Securities LLC	 buy 5 CDNS for 247.61	20231009.json	buy/sell	4716	Tax Exempt
10/9/23	-16838.16	Alpaca Securities LLC	 buy 68 CDNS for 247.62	20231009.json	buy/sell	4716	Tax Exempt
10/9/23	16105.05	Alpaca Securities LLC	 sell -65 CDNS for 247.77	20231009.json	buy/sell	4716	Tax Exempt
10/9/23	18084.29	Alpaca Securities LLC	 sell -73 CDNS for 247.73	20231009.json	buy/sell	4716	Tax Exempt
10/9/23	1982.24	Alpaca Securities LLC	 sell -8 CDNS for 247.78	20231009.json	buy/sell	4716	Tax Exempt
10/10/23	-2992.08	Alpaca Securities LLC	 buy 12 CDNS for 249.34	20231010.json	buy/sell	4716	Tax Exempt
10/10/23	-2992.08	Alpaca Securities LLC	 buy 12 CDNS for 249.34	20231010.json	buy/sell	4716	Tax Exempt
10/10/23	-11968.32	Alpaca Securities LLC	 buy 48 CDNS for 249.34	20231010.json	buy/sell	4716	Tax Exempt
10/10/23	-18138.96	Alpaca Securities LLC	 buy 72 CDNS for 251.93	20231010.json	buy/sell	4716	Tax Exempt
10/10/23	18043.2	Alpaca Securities LLC	 sell -72 CDNS for 250.6	20231010.json	buy/sell	4716	Tax Exempt
10/11/23	18229.68	Alpaca Securities LLC	 sell -72 CDNS for 253.19	20231011.json	buy/sell	4716	Tax Exempt
10/12/23	-18119.91	Alpaca Securities LLC	 buy 71 CDNS for 255.21	20231012.json	buy/sell	4716	Tax Exempt
10/12/23	-0.66	Alpaca Securities LLC	Cost and Fees	statement pdf	Cost and Fees	7151	Tax Exempt
10/12/23	0	Alpaca Securities LLC	Dividend	statement pdf	dividend	4716	Tax Exempt
---

All the options for info are:
---
Date	Amount	Payee	Description	Reference	Transaction Type	Account Code	Tax Rate
Alpaca Securities LLC	Add funds	<source>	Add funds	3110	Tax Exempt
Alpaca Securities LLC	Dividend	<source>	dividends	4716	Tax Exempt
Alpaca Securities LLC	Cost and Fees	<source>	fee	7151	Tax Exempt
Alpaca Securities LLC	buy <info>	<source>	buy/sell	4716	Tax Exempt
---

"""

path_root = '/Users/youval/Library/CloudStorage/OneDrive-Personal/yquark/Docs {year}/statements/{dt} statement.csv'


def read_trades_info(dt: str, save_to_file: bool = False) -> pd.DataFrame:
    """
    Iterate on all the data for year and month provided by `dt`

    Args:
        dt: format YYYY-MM
        save_to_file: save the file or just insert data to df

    Returns:
        out_file_name:
    """
    sc = get_secret('alpaca')
    base_url = 'https://api.alpaca.markets'
    api_params = {
        'key_id': sc.api_key,
        'secret_key': sc.api_secret,
        'base_url': base_url,
        'api_version': 'v2'}
    api = tradeapi.REST(**api_params)

    # 1. collect monthly trades, fees, added funds and any other info that in the monthly statement
    # 2. save as CSV
    # 3. print totals and the output file, formated path_root

    df = pd.DataFrame()
    return df


if __name__ == '__main__':
    dt = '2024-01'
    save_to_file = False
    df = read_trades_info(dt, save_to_file)
