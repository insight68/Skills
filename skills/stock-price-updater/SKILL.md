---
name: stock-price-updater
description: "Update Excel files with latest stock market data including open, high, low, close prices, volume, and price changes. Supports multiple data sources (Yahoo Finance, AkShare) and automatically matches stocks by code or name. Use when users need to: (1) Update stock prices in Excel spreadsheets, (2) Fetch latest market data for multiple stocks, (3) Add trading data columns to existing stock lists, (4) Work with Chinese A-shares, Hong Kong stocks, or US stocks in Excel format."
---

# Stock Price Updater

## Overview

Update Excel files with latest stock market data from multiple sources. The script automatically detects stock markets, fetches real-time prices, and writes comprehensive trading data including open/high/low/close prices, volume, and price changes.

## Quick Start

Basic usage:

```bash
python3 scripts/update_stock_prices.py <excel_file>
```

Save to a different file:

```bash
python3 scripts/update_stock_prices.py input.xlsx -o output.xlsx
```

## Installation

Install required dependencies:

```bash
pip install pandas openpyxl yfinance akshare
```

Minimum requirements:
- `pandas` and `openpyxl` (required for Excel handling)
- At least one of: `yfinance` or `akshare` (for fetching stock data)

## Excel File Requirements

The Excel file must contain a stock code column with one of these names (case-insensitive):
- `股票代码`, `代码` (Chinese)
- `code`, `symbol`, `ticker` (English)

Optional stock name column:
- `股票名称`, `名称` (Chinese)
- `name`, `stock_name` (English)

The script will add or update these columns:
- `开盘价` (Open), `最高价` (High), `最低价` (Low), `收盘价` (Close)
- `成交量` (Volume)
- `涨跌额` (Change), `涨跌幅(%)` (Change %)
- `更新日期` (Update Date)

For detailed format specifications and examples, see [references/excel-format.md](references/excel-format.md).

## Supported Stock Markets

The script automatically detects the market based on code format:

**Chinese A-Shares**:
- Shanghai: `600000`, `601000`, `688000` (or with `sh` prefix)
- Shenzhen: `000001`, `300001` (or with `sz` prefix)
- Uses AkShare (preferred) or Yahoo Finance

**Hong Kong Stocks**:
- Format: `0700.HK`, `9988.HK` or just `0700`, `9988`
- Uses Yahoo Finance

**US Stocks**:
- Format: `AAPL`, `TSLA`, `GOOGL`
- Uses Yahoo Finance

**Other Markets**:
- Supported through Yahoo Finance with appropriate suffixes

For detailed information about data sources, see [references/data-sources.md](references/data-sources.md).

## Workflow

When a user requests to update stock prices in an Excel file:

1. **Verify file exists** and is accessible
2. **Check dependencies**: Ensure pandas, openpyxl, and at least one data source library (yfinance or akshare) are installed
3. **Run the script**: Execute `python3 scripts/update_stock_prices.py <file_path>`
4. **Review output**: The script reports success/failure for each stock
5. **Verify results**: Check the updated Excel file for new data columns

## Script Features

- **Automatic market detection**: Identifies Chinese, Hong Kong, US, and other markets by code format
- **Multiple data sources**: Tries AkShare for Chinese stocks, falls back to Yahoo Finance
- **Flexible column matching**: Finds stock code columns by multiple possible names
- **Data caching**: Avoids redundant API calls for duplicate stocks
- **Comprehensive output**: Adds 8 data columns with complete trading information
- **Error handling**: Reports which stocks succeeded or failed to update

## Troubleshooting

**"Cannot find stock code column" error**:
- Ensure Excel has a column named: `股票代码`, `代码`, `code`, `symbol`, or `ticker`
- Column names are case-insensitive

**Missing data for specific stocks**:
- Stock may be suspended, delisted, or code format is incorrect
- Check the code format matches the market (e.g., US stocks need ticker symbols like `AAPL`, not numbers)

**Import errors**:
- Install missing libraries: `pip install yfinance akshare pandas openpyxl`
- At minimum, need pandas, openpyxl, and one data source library

**Slow performance**:
- Fetching many stocks takes time (each API call takes 1-3 seconds)
- Script includes caching to avoid duplicate requests
- Consider running during off-peak hours for large files

**Network errors**:
- AkShare requires stable connection to Chinese data sources
- Yahoo Finance may rate-limit excessive requests
- Try again after a few minutes if rate-limited

For detailed troubleshooting, see [references/data-sources.md](references/data-sources.md).
