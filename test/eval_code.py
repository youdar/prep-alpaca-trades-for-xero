from src.data_processing_tools import TradeConfirmationTools
import pandas as pd
import shutil
import os

pd.set_option('display.width', 800)
pd.set_option('display.max_columns', 60)
pd.set_option('mode.chained_assignment', None)


def clear_directory(directory):
    # Check if the directory exists
    if os.path.exists(directory):
        # Remove the directory and all its contents
        shutil.rmtree(directory)
        # Recreate the empty directory
        os.makedirs(directory)
    else:
        print(f"The directory {directory} does not exist. Creating new directory.")
        os.makedirs(directory)


def eval_read_json_files():
    json_dir = os.path.join(os.path.dirname(__file__), 'data')
    assert os.path.isdir(json_dir)
    o = TradeConfirmationTools(json_dir=json_dir)
    df = o.read_json_files()
    assert not df.empty
    # print(df.head())


def eval_write_excel_monthly_data():
    # delete existing files in test output folder
    destination_dir = os.path.join(os.path.dirname(__file__), 'temp_output_files')
    clear_directory(destination_dir)

    # collect data
    json_dir = os.path.join(os.path.dirname(__file__), 'data')
    o = TradeConfirmationTools(json_dir=json_dir)
    df = o.read_json_files()

    # write excel files
    out_dir, periods = o.write_excel_monthly_data(destination_dir=destination_dir)
    assert len(os.listdir(destination_dir)) > 0
    assert len(periods) == 2


if __name__ == '__main__':
    # eval_read_json_files()
    eval_write_excel_monthly_data()
    print('Done...')
