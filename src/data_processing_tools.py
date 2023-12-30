from src.config import TRADES_JSON_DIR, DESTINATION_DIR
import pandas as pd
import json
import os

pd.set_option('display.width', 800)
pd.set_option('display.max_columns', 60)
pd.set_option('mode.chained_assignment', None)

cols = ['*Date',
        '*Amount',
        'Payee',
        'Description',
        'Reference',
        'Transaction Type',
        'Account Code',
        'Tax Rate']


class TradeConfirmationTools:
    def __init__(self, json_dir: str = ''):
        self.cols = cols
        self.json_dir = json_dir if json_dir else TRADES_JSON_DIR
        self.destination_dir = DESTINATION_DIR
        self.collected_json_df = pd.DataFrame(self.cols)

    def read_json_files(self) -> pd.DataFrame:
        """
        - Search for all the JSON files in self.json_dir and store in `json_file_list`
        - Iterate through `json_file_list` and:
            1. Load the file
            2. check that it has "creation_date" and "trade_activities"
            3. if it has, create a `temp_df` with the columns `self.cols` and map the JSON data as follows:
               - "creation_date" -> '*Date'
               - "trade_activities.gross_amount" -> '*Amount'
               - f'{"trade_activities.side"} {"trade_activities.qty"} {"trade_activities.symbol"} {"trade_activities.price"}' -> 'Description'
            4. Add the following columns to `temp_df`
                - temp_df['Payee'] = 'Alpaca Securities LLC'
                - temp_df['Tax Rate'] = 'Tax Exempt'
                - temp_df['Account Code'] = 4716
                - temp_df['Reference'] = JSON file name
                - temp_df['Transaction Type'] = 'buy/sell'
            5. Add `temp_df` to `self.collected_json_df`

        Returns:
            collected_json_df
        """
        json_file_list = [f for f in os.listdir(self.json_dir) if f.endswith('.json')]
        rows = []
        for file_name in json_file_list:
            file_path = os.path.join(self.json_dir, file_name)

            with open(file_path, 'r') as file:
                data = json.load(file)

                if 'creation_date' in data and 'trade_activities' in data:
                    for ta in data['trade_activities']:
                        row = {
                            '*Date': data['creation_date'],
                            '*Amount': ta['gross_amount'],
                            'Description': f" {ta['side']} {ta['qty']} {ta['symbol']} for {ta['price']}",
                            'Payee': 'Alpaca Securities LLC',
                            'Tax Rate': 'Tax Exempt',
                            'Account Code': 4716,
                            'Reference': file_name,
                            'Transaction Type': 'buy/sell'
                        }
                        rows.append(row)

        self.collected_json_df = pd.DataFrame(rows, columns=self.cols)
        return self.collected_json_df
