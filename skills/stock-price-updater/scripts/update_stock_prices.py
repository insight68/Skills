#!/usr/bin/env python3
"""
Update stock prices in Excel file with latest market data.
Supports multiple data sources and automatically matches stocks by code or name.
"""

import pandas as pd
import argparse
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple
import re

try:
    import yfinance as yf
except ImportError:
    print("Warning: yfinance not installed. Install with: pip install yfinance")
    yf = None

try:
    import akshare as ak
except ImportError:
    print("Warning: akshare not installed. Install with: pip install akshare")
    ak = None


class StockDataFetcher:
    """Fetch stock data from multiple sources."""

    def __init__(self):
        self.cache = {}

    def detect_market(self, code: str) -> str:
        """Detect which market the stock belongs to based on code format."""
        code = str(code).strip().upper()

        # A-share patterns
        if re.match(r'^(60|68)\d{4}$', code):  # Shanghai A-share
            return 'cn_sh'
        elif re.match(r'^(00|30)\d{4}$', code):  # Shenzhen A-share
            return 'cn_sz'
        elif re.match(r'^(SH|SZ)', code):  # With prefix
            return 'cn'

        # Hong Kong
        elif re.match(r'^\d{4,5}\.HK$', code) or re.match(r'^\d{4,5}$', code):
            return 'hk'

        # US stocks (contains letters)
        elif re.match(r'^[A-Z]+$', code):
            return 'us'

        return 'unknown'

    def normalize_cn_code(self, code: str) -> str:
        """Normalize Chinese stock code format."""
        code = str(code).strip()

        # Remove existing prefix
        code = re.sub(r'^(SH|SZ|sh|sz)', '', code)

        # Add appropriate prefix
        if re.match(r'^(60|68)\d{4}$', code):
            return f'sh{code}'
        elif re.match(r'^(00|30)\d{4}$', code):
            return f'sz{code}'

        return code

    def fetch_from_yfinance(self, code: str, market: str) -> Optional[Dict]:
        """Fetch data from Yahoo Finance."""
        if yf is None:
            return None

        try:
            # Format code for yfinance
            if market == 'cn_sh':
                ticker_symbol = f'{code}.SS'
            elif market == 'cn_sz':
                ticker_symbol = f'{code}.SZ'
            elif market == 'hk':
                ticker_symbol = f'{code}.HK'
            else:
                ticker_symbol = code

            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period='5d')

            if hist.empty:
                return None

            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else latest

            return {
                'open': round(latest['Open'], 2),
                'high': round(latest['High'], 2),
                'low': round(latest['Low'], 2),
                'close': round(latest['Close'], 2),
                'volume': int(latest['Volume']),
                'change': round(latest['Close'] - prev['Close'], 2),
                'change_pct': round((latest['Close'] - prev['Close']) / prev['Close'] * 100, 2) if prev['Close'] > 0 else 0,
                'date': latest.name.strftime('%Y-%m-%d'),
                'source': 'yfinance'
            }
        except Exception as e:
            print(f"  yfinance error for {code}: {e}")
            return None

    def fetch_from_akshare(self, code: str, market: str) -> Optional[Dict]:
        """Fetch data from AkShare (Chinese stocks)."""
        if ak is None or market not in ['cn_sh', 'cn_sz', 'cn']:
            return None

        try:
            normalized_code = self.normalize_cn_code(code)
            df = ak.stock_zh_a_hist(symbol=normalized_code, period="daily", adjust="qfq")

            if df.empty:
                return None

            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            close_price = float(latest['收盘'])
            prev_close = float(prev['收盘'])

            return {
                'open': round(float(latest['开盘']), 2),
                'high': round(float(latest['最高']), 2),
                'low': round(float(latest['最低']), 2),
                'close': round(close_price, 2),
                'volume': int(latest['成交量']),
                'change': round(close_price - prev_close, 2),
                'change_pct': round((close_price - prev_close) / prev_close * 100, 2) if prev_close > 0 else 0,
                'date': latest['日期'],
                'source': 'akshare'
            }
        except Exception as e:
            print(f"  akshare error for {code}: {e}")
            return None

    def fetch_stock_data(self, code: str, name: str = '') -> Optional[Dict]:
        """Fetch stock data from available sources."""
        cache_key = f"{code}_{name}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        market = self.detect_market(code)
        print(f"Fetching {code} ({name}) - Market: {market}")

        data = None

        # Try AkShare first for Chinese stocks
        if market in ['cn_sh', 'cn_sz', 'cn']:
            data = self.fetch_from_akshare(code, market)

        # Fallback to yfinance
        if data is None:
            data = self.fetch_from_yfinance(code, market)

        if data:
            self.cache[cache_key] = data

        return data


def find_column(df: pd.DataFrame, possible_names: list) -> Optional[str]:
    """Find column by possible names (case-insensitive)."""
    for col in df.columns:
        if str(col).strip().lower() in [name.lower() for name in possible_names]:
            return col
    return None


def update_excel_with_stock_data(input_file: str, output_file: str = None):
    """Update Excel file with latest stock prices."""
    if output_file is None:
        output_file = input_file

    print(f"Reading Excel file: {input_file}")
    df = pd.read_excel(input_file)

    # Find relevant columns
    code_col = find_column(df, ['股票代码', '代码', 'code', 'symbol', 'ticker'])
    name_col = find_column(df, ['股票名称', '名称', 'name', 'stock_name'])

    if code_col is None:
        print("Error: Cannot find stock code column. Expected column names: '股票代码', '代码', 'code', 'symbol', 'ticker'")
        sys.exit(1)

    print(f"Found columns - Code: '{code_col}', Name: '{name_col}'")

    # Prepare new columns
    new_columns = {
        '开盘价': 'open',
        '最高价': 'high',
        '最低价': 'low',
        '收盘价': 'close',
        '成交量': 'volume',
        '涨跌额': 'change',
        '涨跌幅(%)': 'change_pct',
        '更新日期': 'date'
    }

    for col_name in new_columns.keys():
        if col_name not in df.columns:
            df[col_name] = None

    # Fetch and update data
    fetcher = StockDataFetcher()
    success_count = 0
    fail_count = 0

    for idx, row in df.iterrows():
        code = str(row[code_col]).strip()
        name = str(row[name_col]).strip() if name_col else ''

        if pd.isna(code) or code == '' or code == 'nan':
            continue

        data = fetcher.fetch_stock_data(code, name)

        if data:
            for col_name, data_key in new_columns.items():
                df.at[idx, col_name] = data.get(data_key)
            success_count += 1
            print(f"  ✓ Updated: {code} - Close: {data['close']}")
        else:
            fail_count += 1
            print(f"  ✗ Failed: {code}")

    # Save to Excel
    print(f"\nSaving to: {output_file}")
    df.to_excel(output_file, index=False)

    print(f"\n{'='*50}")
    print(f"Update completed!")
    print(f"Success: {success_count}, Failed: {fail_count}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(description='Update stock prices in Excel file')
    parser.add_argument('input_file', help='Input Excel file path')
    parser.add_argument('-o', '--output', help='Output Excel file path (default: overwrite input)')

    args = parser.parse_args()

    update_excel_with_stock_data(args.input_file, args.output)


if __name__ == '__main__':
    main()
