# Stock Data Sources

This skill supports multiple data sources for fetching stock prices. The script automatically selects the appropriate source based on the stock code format.

## Supported Data Sources

### 1. AkShare (akshare)

**Best for**: Chinese A-share stocks (Shanghai and Shenzhen exchanges)

**Installation**:
```bash
pip install akshare
```

**Supported Markets**:
- Shanghai Stock Exchange (SSE): Codes starting with 60, 68
- Shenzhen Stock Exchange (SZSE): Codes starting with 00, 30

**Code Format**:
- `600000` - Shanghai stock
- `000001` - Shenzhen stock
- `sh600000` or `sz000001` - With exchange prefix

**Features**:
- Real-time and historical data for A-shares
- Adjusted prices (前复权)
- Chinese language output
- No API key required

### 2. Yahoo Finance (yfinance)

**Best for**: Global stocks (US, Hong Kong, and international markets)

**Installation**:
```bash
pip install yfinance
```

**Supported Markets**:
- US stocks: `AAPL`, `TSLA`, `GOOGL`
- Hong Kong stocks: `0700.HK`, `9988.HK`
- Chinese stocks: `600000.SS` (Shanghai), `000001.SZ` (Shenzhen)
- Other international markets

**Code Format**:
- US: `AAPL`, `MSFT`
- Hong Kong: `0700.HK`, `9988.HK`
- Shanghai: `600000.SS`
- Shenzhen: `000001.SZ`

**Features**:
- Global market coverage
- Historical data
- No API key required
- English language output

## Automatic Source Selection

The script automatically detects the market based on the stock code format:

1. **Chinese A-shares** (60xxxx, 68xxxx, 00xxxx, 30xxxx):
   - First tries AkShare (if installed)
   - Falls back to Yahoo Finance

2. **Hong Kong stocks** (xxxx.HK or 4-5 digit codes):
   - Uses Yahoo Finance

3. **US stocks** (alphabetic codes):
   - Uses Yahoo Finance

4. **Unknown format**:
   - Tries Yahoo Finance

## Data Fields Returned

All data sources return the following standardized fields:

- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume
- `change`: Price change amount
- `change_pct`: Price change percentage
- `date`: Trading date
- `source`: Data source used (akshare or yfinance)

## Installation Requirements

Install both libraries for maximum compatibility:

```bash
pip install yfinance akshare pandas openpyxl
```

**Minimum requirements**:
- `pandas`: For Excel file handling
- `openpyxl`: For .xlsx file support
- At least one of: `yfinance` or `akshare`

## Troubleshooting

### AkShare Issues

- **Network errors**: AkShare fetches data from Chinese sources, may require stable connection
- **Code format**: Ensure codes are 6 digits, optionally with sh/sz prefix
- **Delisted stocks**: Will return no data

### Yahoo Finance Issues

- **Rate limiting**: Too many requests may be throttled
- **Delisted stocks**: Will return no data
- **Code format**: Ensure proper suffix (.SS, .SZ, .HK)

### General Issues

- **Missing data**: Stock may be suspended, delisted, or code is incorrect
- **Slow performance**: Fetching many stocks takes time; script includes caching
- **Import errors**: Install missing libraries with pip
