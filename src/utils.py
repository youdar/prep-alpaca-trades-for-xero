import alpaca_trade_api as tradeapi
from my_secrets import get_secret
import pandas as pd
from datetime import datetime, timedelta

"""
Create a tool that utilizes Alpaca alpaca-trade-api to collect monthly trades
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


# def read_trades_info(dt: str, save_to_file: bool = False) -> pd.DataFrame:
#     """
#     Iterate on all the data for year and month provided by `dt`
#
#     Args:
#         dt: format YYYY-MM
#         save_to_file: save the file or just insert data to df
#
#     Returns:
#         out_file_name:
#     """
#     sc = get_secret('alpaca')
#     base_url = 'https://api.alpaca.markets'
#     api_params = {
#         'key_id': sc.api_key,
#         'secret_key': sc.api_secret,
#         'base_url': base_url,
#         'api_version': 'v2'}
#     api = tradeapi.REST(**api_params)
#
#     # 1. collect monthly trades, fees, added funds and any other info that in the monthly statement
#     # 2. save as CSV
#     # 3. print totals and the output file, formated path_root
#
#     df = pd.DataFrame()
#     return df





path_root = '/Users/youval/Library/CloudStorage/OneDrive-Personal/yquark/Docs {year}/statements/{dt} statement.csv'


def _date_range_for_month(dt: str):
    """
    Given 'YYYY-MM', return (start_datetime, end_datetime) for that calendar month.
    Example: '2024-01' => (2024-01-01 00:00:00, 2024-01-31 23:59:59)
    """
    year_str, month_str = dt.split("-")
    year = int(year_str)
    month = int(month_str)
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(seconds=1)
    return start, end


def read_trades_info(dt: str, save_to_file: bool = False) -> pd.DataFrame:
    """
    Collect monthly trades, fees, dividends, and fund transfers for the
    given year-month using the Alpaca API, and produce a DataFrame that
    can be uploaded into Xero.

    Args:
        dt: format 'YYYY-MM'
        save_to_file: whether to save the resulting CSV file

    Returns:
        df: Pandas DataFrame with columns:
            ['Date','Amount','Payee','Description','Reference',
             'Transaction Type','Account Code','Tax Rate']
    """
    # Load your Alpaca creds
    sc = get_secret('alpaca')
    base_url = 'https://api.alpaca.markets'
    api_params = {
        'key_id': sc.api_key,
        'secret_key': sc.api_secret,
        'base_url': base_url,
        'api_version': 'v2'
    }
    api = tradeapi.REST(**api_params)

    # Figure out the date range for the month


    start_dt, end_dt = _date_range_for_month(dt)
    NY = 'America/New_York'
    after_str = pd.Timestamp(start_dt, tz=NY).isoformat()
    before_str = pd.Timestamp(end_dt, tz=NY).isoformat()

    # We'll collect records from multiple activity endpoints
    data_rows = []

    # --- 1) Get all "FILL" activities (buys/sells) ---
    # see https://alpaca.markets/docs/api-references/trading-api/account-activities/#get-account-activities
    fills = api.get_activities(
        activity_types='FILL',
        after=after_str,
        until=before_str
    )

    # Each fill has attributes like: transaction_time, side, qty, symbol, price, net_amount, etc.
    for fill in fills:
        trade_time = fill.transaction_time
        date_str = trade_time.strftime('%m/%d/%y')
        qty = float(fill.qty)
        px = float(fill.price)
        side = fill.side  # "buy" or "sell"
        amount = qty * px * ((side == 'sell') - (side == 'buy'))
        description = f"{side} {int(qty)} {fill.symbol} for {px:.2f}"
        tx_type = "buy/sell"
        payee = "Alpaca Securities LLC"

        # For your sample, Account Code = 4716, Tax Rate = "Tax Exempt"
        row = {
            'Date': date_str,
            'Amount': amount,
            'Payee': payee,
            'Description': description,
            'Reference': 'Using APIs',
            'Transaction Type': tx_type,
            'Account Code': '4716',
            'Tax Rate': 'Tax Exempt'
        }
        data_rows.append(row)

    # --- 2) Get all "DIV" (dividends) ---
    divs = api.get_activities(
        activity_types='DIV',
        after=after_str,
        until=before_str
    )

    # Each div might have fields like: net_amount, date_paid, etc.
    for div in divs:
        date_str = div.transaction_time.strftime('%m/%d/%y')
        amount = float(div.net_amount)  # typically > 0 for dividend

        row = {
            'Date': date_str,
            'Amount': amount,
            'Payee': "Alpaca Securities LLC",
            'Description': "Dividend",
            # The reference might be "statement pdf" or some generic label
            'Reference': "monthly statement (DIV)",
            'Transaction Type': "dividends",
            'Account Code': '4716',  # your chart-of-accounts code for dividends
            'Tax Rate': 'Tax Exempt'
        }
        data_rows.append(row)

    # --- 3) Get non-trade activities that might be fees or transfers ---
    # Alpaca breaks these out by 'NONTRADE' type, e.g. 'FEE', 'TRANS', 'WIRE', 'JNLC', 'JNLS'
    # There's a separate method: get_nontrade_activities() or get_activities() with 'FEE', 'TRANS', etc.
    # If your library version doesn’t have get_nontrade_activities(), you can do:
    #    api.get_activities(activity_types=['FEE','TRANS','WIRE','JNLC','JNLS'], after=..., before=...)
    # or make separate calls per type. We'll do them in one pass if supported:

    non_trades = []
    # Some older alpaca_trade_api versions don’t allow list-of-types.
    # If you get errors, just do multiple calls e.g. for 'FEE' and 'TRANS' separately.
    for act_type in ['FEE', 'TRANS', 'WIRE', 'JNLC', 'JNLS', 'INT']:
        try:
            acts = api.get_activities(
                activity_types=act_type,
                after=after_str,
                before=before_str
            )
            non_trades.extend(acts)
        except Exception:
            pass  # some activity_types might not exist or not be supported

    for nt in non_trades:
        date_str = nt.transaction_time.strftime('%m/%d/%y')
        amount = float(nt.net_amount)

        # Distinguish between "FEE", "TRANS"/"WIRE" (add funds?), "JNLC"/"JNLS"?
        if nt.activity_type == 'FEE':
            description = "Cost and Fees"
            tx_type = "fee"
            account_code = '7151'  # from your example
        elif nt.activity_type in ['TRANS', 'WIRE', 'JNLC', 'JNLS']:
            # Could be deposit or withdrawal. net_amount can be negative (out) or positive (in)
            if amount > 0:
                description = "Add funds"
                tx_type = "Add funds"
                account_code = '3110'  # from your example
            else:
                description = "Withdrawal"
                tx_type = "Withdrawal"
                # you'd have to decide your own account code
                account_code = '3110'
        elif nt.activity_type == 'INT':
            # If you ever get interest paid, treat it similarly to dividend
            description = "Interest Income"
            tx_type = "interest"
            account_code = '4716'
        else:
            description = "Other Non-Trade"
            tx_type = "other"
            account_code = '7151'

        row = {
            'Date': date_str,
            'Amount': amount,
            'Payee': "Alpaca Securities LLC",
            'Description': description,
            # For reference, you might want to store the 'id' or 'monthly statement'
            'Reference': "monthly statement (NONTRADE)",
            'Transaction Type': tx_type,
            'Account Code': account_code,
            'Tax Rate': 'Tax Exempt'
        }
        data_rows.append(row)

    # --- Combine all rows into a single DataFrame ---
    df = pd.DataFrame(data_rows, columns=[
        'Date', 'Amount', 'Payee', 'Description', 'Reference',
        'Transaction Type', 'Account Code', 'Tax Rate'
    ])

    # Sort by Date ascending (optional)
    df.sort_values(by='Date', inplace=True)

    # Build the output filename
    year_str, month_str = dt.split("-")
    out_file_name = path_root.format(year=year_str, dt=dt)

    if save_to_file:
        df.to_csv(out_file_name, index=False)
        print(f"Saved CSV: {out_file_name}")
        # Optionally also save .xlsx
        xlsx_file_name = out_file_name.replace(".csv", ".xlsx")
        df.to_excel(xlsx_file_name, index=False)
        print(f"Saved Excel: {xlsx_file_name}")

    # Summaries / totals
    # E.g. total trades, total fees, etc. for debugging
    print("Totals:")
    print("  Buys/Sells:", df[df['Transaction Type'] == 'buy/sell']['Amount'].sum())
    print("  Dividends:", df[df['Transaction Type'] == 'dividends']['Amount'].sum())
    print("  Fees:", df[df['Transaction Type'] == 'fee']['Amount'].sum())
    print("  Added funds:", df[df['Transaction Type'] == 'Add funds']['Amount'].sum())

    return df


if __name__ == '__main__':
    dt = '2024-01'
    save_to_file = False
    df = read_trades_info(dt, save_to_file)
    print(df.head(20))
