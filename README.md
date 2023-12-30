# Alpaca - XERO transaction uploads
When doing day trading using Alpaca and using XERO for accounting there can  
be very many daily transactions. To track profit and loss, for taxes or for general 
accounting we need to somehow upload all transactions to XERO.

This tools utilizes the monthly statements and JSON trade confirmation files downloaded 
from Alpaca [https://app.alpaca.markets/account/documents](https://app.alpaca.markets/account/documents)
to build CSV files that can be imported into XERO.

Consider doing this only at the end of each month.

#### Data collection:
1. Go to Alpaca [https://app.alpaca.markets/account/documents](https://app.alpaca.markets/account/documents)
2. filter for `Account statement` and download to a folder like `Doc YYYY/statements`

Process steps:
