import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta
from my_secrets import get_secret

pd.set_option('display.width', 800)
pd.set_option('display.max_columns', 60)
pd.set_option('mode.chained_assignment', None)

# A dictionary mapping each Alpaca activity_type to a (Transaction Type, Default Account Code).
# Some examples below. Adjust to your needs.
ACTIVITY_MAPPING = {
    # Primary known ones:
    'FILL': ('buy/sell', '4716'),  # trades
    'DIV': ('dividend', '4716'),
    'DIVCGL': ('dividend', '4716'),
    'DIVCGS': ('dividend', '4716'),
    'DIVFEE': ('fee', '7151'),  # e.g. 'Dividend fee'
    'DIVFT': ('dividend', '4716'),  # foreign tax withheld
    'DIVNRA': ('dividend', '4716'),  # NRA withheld
    'DIVROC': ('dividend', '4716'),  # return of capital
    'DIVTW': ('dividend', '4716'),  # Tefra withheld
    'DIVTXEX': ('dividend', '4716'),  # tax exempt
    'INT': ('interest', '4716'),
    'INTNRA': ('interest', '4716'),
    'INTTW': ('interest', '4716'),
    'FEE': ('fee', '7151'),  # catch-all fee

    # Transfers/Deposits/Withdrawals:
    'TRANS': ('transfer', '3110'),  # sometimes same as CSD/CSW
    'CSD': ('deposit', '3110'),  # + net_amount
    'CSW': ('withdrawal', '3110'),  # - net_amount
    'WIRE': ('transfer', '3110'),
    'ACATC': ('acats_cash', '3110'),
    'ACATS': ('acats_securities', '3110'),

    # Journals:
    'JNL': ('journal', '3110'),
    'JNLC': ('journal_in', '3110'),
    'JNLS': ('journal_out', '3110'),

    # Corporate actions:
    'MA': ('merger_acquisition', '9999'),
    'NC': ('name_change', '9999'),
    'REORG': ('reorg', '9999'),
    'SC': ('symbol_change', '9999'),
    'SSO': ('stock_spinoff', '9999'),
    'SSP': ('stock_split', '9999'),

    # Options:
    'OPASN': ('option_assignment', '9999'),
    'OPEXP': ('option_expiration', '9999'),
    'OPXRC': ('option_exercise', '9999'),

    # Pass-thru
    'PTC': ('pass_thru_charge', '7151'),
    'PTR': ('pass_thru_rebate', '4716'),

    # "MISC" or rarely used catch-all:
    'MISC': ('misc', '9999')
}


def print_month_summary(df: pd.DataFrame):
    """
    Print a summary for the month by grouping transactions by Transaction Type.
    Uses the 'Date' column (formatted as mm/dd/yy) to verify that all data
    is for a single month and gives feedback to ensure the data collected is as expected.
    """
    if df.empty:
        print("No data collected for the month.")
        return

    # Convert the 'Date' column to datetime and extract the month period.
    try:
        date_dt = pd.to_datetime(df['*Date'], format='%m/%d/%y', errors='coerce')
        unique_months = [x.__str__() for x in date_dt.dt.to_period('M').unique()]
        unique_months.sort()
    except Exception as e:
        print("Error parsing dates in '*Date' column:", e)
        unique_months = set()

    unique_months = ', '.join(unique_months)
    print(f"Monthly Summary for {unique_months}:")

    # Group by 'Transaction Type' and summarize
    summary = df.groupby('Transaction Type')['*Amount'].agg(['count', 'sum']).reset_index()
    print("Summary by Transaction Type:")
    print(summary)

    overall_total = df['*Amount'].sum()
    print(f"\nOverall Total account changes: {overall_total:.2f}")


def compute_fill_amount(row):
    if row['activity_type'] == 'FILL':
        qty = float(row.get('qty', 0))
        price = float(row.get('price', 0))
        side = row.get('side', '').lower()
        # If side is 'sell', factor = +1; if 'buy', factor = -1.
        factor = 1 if side == 'sell' else -1
        amount = round(qty * price, 2)
        return amount * factor
    else:
        return float(row.get('net_amount', 0))


def read_trades_info(dt: str, save_to_file: bool = False) -> pd.DataFrame:
    """
    Collect monthly trades, fees, dividends, deposits, withdrawals, etc. for the given YYYY-MM.
    Map them into a format suitable for Xero using the extended activity type list.
    """
    year, month = map(int, dt.split('-'))
    start_date = datetime(year, month, 1)
    next_month = (month + 1 % 13)
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year
    end_date = datetime(next_year, next_month, 1)

    NY = 'America/New_York'
    after_str = pd.Timestamp(start_date, tz=NY).isoformat()
    before_str = pd.Timestamp(end_date, tz=NY).isoformat()

    # We'll

    # Init Alpaca
    sc = get_secret('alpaca')
    api = tradeapi.REST(
        key_id=sc.api_key,
        secret_key=sc.api_secret,
        base_url='https://api.alpaca.markets',
        api_version='v2'
    )

    # Attempt to fetch all activity types in separate calls (some older versions of the SDK don't allow a single list)
    all_activities = []
    for a_type in ACTIVITY_MAPPING.keys():
        page_token = None  # Initialize page_token for each activity type
        while True:
            try:
                response = api.get_activities(
                    activity_types=a_type,
                    after=after_str,
                    until=before_str,
                    page_token=page_token,
                    page_size=100
                )
                if not response:
                    break  # Exit loop if no activities are returned
                all_activities.extend(response)
                # The page_token for the next page is the ID of the last activity in the current response
                page_token = response[-1].id
            except Exception as e:
                print(f"Error fetching activities for type {a_type}: {e}")
                break

    # Convert to DataFrame
    data = [act._raw for act in all_activities]
    df = pd.DataFrame(data)
    if df.empty:
        print("No activities found for that month.")
        return df

    # Convert transaction_time to datetime
    mask = df['date'].isnull() | (df['date'].astype(str).str.strip() == '')
    if 'transaction_time' in df.columns:
        df.loc[mask, '*Date'] = pd.to_datetime(df.loc[mask, 'transaction_time'], errors='coerce').dt.strftime('%m/%d/%y')
    df.loc[~mask, '*Date'] = pd.to_datetime(df.loc[~mask, 'date'], errors='coerce').dt.strftime('%m/%d/%y')
    df['*Date'] = df['*Date'].fillna(method='ffill').fillna(method='bfill')

    # net_amount is your inflow/outflow. Typically negative for buys, positive for sells, etc.
    df['*Amount'] = pd.to_numeric(df['net_amount'], errors='coerce')
    df['*Amount'] = df.apply(compute_fill_amount, axis=1)

    # Map activity types -> (Transaction Type, Default Account Code)
    def map_activity_type(a_type):
        if a_type in ACTIVITY_MAPPING:
            return ACTIVITY_MAPPING[a_type]
        # fallback if not in dictionary:
        return ('other', '9999')  # or any default code you prefer

    df[['Transaction Type', 'Account Code']] = df.apply(
        lambda row: pd.Series(map_activity_type(row['activity_type'])),
        axis=1
    )

    # Description can vary by type. For FILL, you might want side/symbol/price.
    def make_description(row):
        a_type = row['activity_type']
        if a_type == 'FILL':
            side = row.get('side', '')
            symbol = row.get('symbol', '')
            qty = row.get('qty', '')
            px = row.get('price', '')
            return f"{side} {qty} {symbol} @ {px}"
        elif a_type.startswith('DIV'):
            return "Dividend"
        elif a_type.startswith('INT'):
            return "Interest"
        elif a_type == 'FEE':
            return "Cost and Fees"
        elif a_type in ['CSD', 'CSW', 'TRANS', 'ACATC', 'ACATS', 'JNLC', 'JNLS', 'JNL']:
            # deposits / withdrawals / transfers / journals
            return a_type
        return a_type  # fallback

    df['Description'] = df.apply(make_description, axis=1)

    # If you want to interpret deposit vs. withdrawal specifically:
    #   e.g. if it's 'CSD' or 'TRANS' and net_amount > 0 => deposit, else withdrawal
    #   That depends on your usage. You can refine further here if you like.

    df['Reference'] = "API call"
    df['Payee'] = 'Alpaca Securities LLC'
    df['Tax Rate'] = 'Tax Exempt'

    # Final columns for Xero
    df = df[['*Date', '*Amount', 'Payee', 'Description', 'Reference', 'Transaction Type', 'Account Code', 'Tax Rate']]

    # Sort by Date ascending
    df.sort_values('*Date', inplace=True)

    if save_to_file:
        out_file_name = f'/Users/youval/Google Drive/yquark/Docs {year}/statements/{dt} statement.csv'
        df.to_csv(out_file_name, index=False)
        print(f"Saved CSV to {out_file_name}")

    return df


__all__ = [
    'print_month_summary',
    'read_trades_info',
]
