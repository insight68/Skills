# Excel File Format Requirements

This document describes the expected Excel file format for the stock price updater.

## Required Columns

The Excel file must contain at least one of the following column names for stock codes (case-insensitive):

- `股票代码` (Chinese)
- `代码` (Chinese)
- `code` (English)
- `symbol` (English)
- `ticker` (English)

## Optional Columns

Stock name column (helps with identification, but not required):

- `股票名称` (Chinese)
- `名称` (Chinese)
- `name` (English)
- `stock_name` (English)

## Output Columns

The script will add or update the following columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| 开盘价 | Opening price | 15.23 |
| 最高价 | Highest price | 15.88 |
| 最低价 | Lowest price | 15.10 |
| 收盘价 | Closing price | 15.67 |
| 成交量 | Trading volume | 12345678 |
| 涨跌额 | Price change amount | 0.45 |
| 涨跌幅(%) | Price change percentage | 2.95 |
| 更新日期 | Update date | 2026-03-03 |

## Example Excel Structure

### Before Update

| 股票代码 | 股票名称 |
|---------|---------|
| 600000 | 浦发银行 |
| 000001 | 平安银行 |
| AAPL | Apple Inc. |
| 0700.HK | 腾讯控股 |

### After Update

| 股票代码 | 股票名称 | 开盘价 | 最高价 | 最低价 | 收盘价 | 成交量 | 涨跌额 | 涨跌幅(%) | 更新日期 |
|---------|---------|-------|-------|-------|-------|--------|-------|----------|---------|
| 600000 | 浦发银行 | 8.50 | 8.65 | 8.45 | 8.60 | 15234567 | 0.10 | 1.18 | 2026-03-03 |
| 000001 | 平安银行 | 12.30 | 12.45 | 12.25 | 12.40 | 23456789 | 0.15 | 1.22 | 2026-03-03 |
| AAPL | Apple Inc. | 175.20 | 178.50 | 174.80 | 177.30 | 45678901 | 2.10 | 1.20 | 2026-03-03 |
| 0700.HK | 腾讯控股 | 385.00 | 390.00 | 383.00 | 388.50 | 12345678 | 3.50 | 0.91 | 2026-03-03 |

## Stock Code Formats

### Chinese A-Shares

**Shanghai Stock Exchange**:
- Format: `600000`, `601000`, `688000`
- 6 digits starting with 60 or 68
- Optional prefix: `sh600000`

**Shenzhen Stock Exchange**:
- Format: `000001`, `300001`
- 6 digits starting with 00 or 30
- Optional prefix: `sz000001`

### Hong Kong Stocks

- Format: `0700.HK`, `9988.HK`
- 4-5 digits with `.HK` suffix
- Can also use just the number: `0700`, `9988`

### US Stocks

- Format: `AAPL`, `TSLA`, `GOOGL`
- Alphabetic ticker symbols
- Usually 1-5 characters

## Notes

- The script automatically detects column names (case-insensitive)
- Existing data in output columns will be overwritten
- Empty or invalid stock codes will be skipped
- The script preserves all other columns in the Excel file
- File format: `.xlsx` (Excel 2007+)
