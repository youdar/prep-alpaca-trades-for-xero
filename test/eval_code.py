from src.data_processing_tools import TradeConfirmationTools
import os

pd.set_option('display.width', 800)
pd.set_option('display.max_columns', 60)
pd.set_option('mode.chained_assignment', None)
def eval_read_json_files():
    json_dir = os.path.join(os.path.dirname(__file__), 'data')
    assert os.path.isdir(json_dir)
    o = TradeConfirmationTools(json_dir=json_dir)
    df = o.read_json_files()
    print(df.head())


if __name__ == '__main__':
    eval_read_json_files()
