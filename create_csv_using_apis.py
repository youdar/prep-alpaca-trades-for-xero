from src.utils import read_trades_info, print_month_summary


if __name__ == "__main__":
    # Change to the month to collect
    dt = "2024-12"
    save_to_file = True
    df_result = read_trades_info(dt, save_to_file=save_to_file)
    print("\n----- Month Summary -----")
    print_month_summary(df_result)
    print("\n----- Review -----")
    print('Compare to actual statement PDF')