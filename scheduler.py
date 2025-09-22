"""
APEX AI TECHNICAL ANALYSIS - AUTOMATED SCHEDULER
Runs analysis periodically and saves results to CSV
"""

import pandas as pd
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import warnings

warnings.filterwarnings('ignore')

# Import from your main app
from tvDatafeed import TvDatafeed, Interval


# You'll need to extract the core analysis functions from your main app
# Or import them if you refactor them into separate modules

class ScheduledAnalyzer:
    """Automated analysis runner for APEX AI platform"""

    def __init__(self):
        self.tv = TvDatafeed()
        self.results_dir = Path("scheduled_results")
        self.results_dir.mkdir(exist_ok=True)

        # Default configuration for scheduled runs
        self.default_config = {
            'timeframes': ['4H'],  # Default 4H as requested
            'exchange': 'NSE',
            'instruments': self.load_instruments(),
            'patterns': {
                'pin_bar': True,
                'bullish_engulfing': True,
                'three_candle': True,
                'dragonfly_doji': False,
                'three_white_soldiers': False,
                'bullish_marubozu': False,
                'bullish_harami': False,
                'bullish_abandoned_baby': False,
                'tweezer_bottom': False,
                'bullish_kicker': False
            },
            'parameters': {
                'swing_lookback': 10,
                'right_lookback': 3,
                'min_swing_size': 0.5,
                'min_wick_ratio': 2.0,
                'max_body_ratio': 0.3,
                'min_engulfing_ratio': 1.1,
                'touch_tolerance': 0.10,
                'min_days_between': 1,
                'max_bars_to_analyze': 200,
            },
            'analysis_start_date': datetime.now() - timedelta(days=180),
            'capital_per_trade': 10000
        }

    def load_instruments(self):
        """Load instruments from file"""
        try:
            with open('instruments_one.txt', 'r') as f:
                content = f.read().strip()
                return [s.strip().upper() for s in content.split(',') if s.strip()]
        except:
            return ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']

    def run_scheduled_analysis(self):
        """Run the analysis with default configuration"""
        print(f"🚀 Starting scheduled analysis at {datetime.now()}")

        try:
            # 1. Update data for all instruments
            print("📊 Updating data...")
            self.update_all_data()

            # 2. Run pattern analysis
            print("🧠 Running AI pattern analysis...")
            results = self.run_pattern_analysis()

            # 3. Save results to CSV
            if results:
                filename = self.save_results_to_csv(results)
                print(f"✅ Results saved to {filename}")

                # Also save a "latest.csv" that always contains the most recent results
                latest_path = self.results_dir / "latest_results.csv"
                results_df = pd.DataFrame(results)
                results_df.to_csv(latest_path, index=False)
                print(f"✅ Latest results updated: {latest_path}")

                # Save metadata
                self.save_metadata(len(results))

                return True
            else:
                print("⚠️ No patterns found in analysis")
                return False

        except Exception as e:
            print(f"❌ Scheduled analysis failed: {e}")
            return False

    def update_all_data(self):
        """Update data for all instruments and timeframes"""
        for symbol in self.default_config['instruments']:
            for timeframe in self.default_config['timeframes']:
                try:
                    interval = self.get_interval(timeframe)
                    data = self.tv.get_hist(symbol, self.default_config['exchange'],
                                            interval, n_bars=200)

                    if data is not None and not data.empty:
                        # Save to cache directory (matching your app structure)
                        cache_dir = Path("data_cache")
                        cache_dir.mkdir(exist_ok=True)

                        cache_file = cache_dir / f"{symbol}_{self.default_config['exchange']}_{timeframe}.json"
                        cache_data = {
                            'data': data.to_json(orient='index', date_format='iso'),
                            'timestamp': datetime.now().isoformat(),
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'exchange': self.default_config['exchange'],
                            'total_candles': len(data)
                        }

                        with open(cache_file, 'w') as f:
                            json.dump(cache_data, f, indent=2)

                        print(f"  ✅ Updated {symbol} {timeframe}")

                except Exception as e:
                    print(f"  ❌ Failed to update {symbol} {timeframe}: {e}")

                time.sleep(0.5)  # Rate limiting

    def run_pattern_analysis(self):
        """Run the pattern analysis (simplified from main app)"""
        # This would use the same logic as your run_comprehensive_analysis
        # For now, returning sample structure
        # You should extract the analysis logic from your main app

        results = []

        # Load cached data and run analysis
        cache_dir = Path("data_cache")

        for symbol in self.default_config['instruments']:
            for timeframe in self.default_config['timeframes']:
                cache_file = cache_dir / f"{symbol}_{self.default_config['exchange']}_{timeframe}.json"

                if cache_file.exists():
                    # Load data
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)

                    df = pd.read_json(cache_data['data'], orient='index')
                    df.index = pd.to_datetime(df.index)

                    # Run your pattern detection logic here
                    # This is a simplified example - use your actual functions

                    # Add sample result (replace with actual analysis)
                    result = {
                        "Symbol": symbol,
                        "Timeframe": timeframe,
                        "Pattern Type": "Pin Bar",  # Example
                        "Pattern Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Entry Price": f"{df['close'].iloc[-1]:.4f}",
                        "Analysis Time": datetime.now().isoformat(),
                        "Is Today's Pattern": "YES",
                        "Trade Outcome": "Active",
                        "Current Status": "Monitoring"
                    }
                    results.append(result)

        return results

    def get_interval(self, timeframe):
        """Convert timeframe to TradingView interval"""
        interval_map = {
            '1m': Interval.in_1_minute,
            '5m': Interval.in_5_minute,
            '15m': Interval.in_15_minute,
            '30m': Interval.in_30_minute,
            '1H': Interval.in_1_hour,
            '4H': Interval.in_4_hour,
            '1D': Interval.in_daily
        }
        return interval_map.get(timeframe, Interval.in_4_hour)

    def save_results_to_csv(self, results):
        """Save analysis results to timestamped CSV"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.results_dir / f"analysis_{timestamp}.csv"

        df = pd.DataFrame(results)
        df.to_csv(filename, index=False)

        return filename

    def save_metadata(self, result_count):
        """Save metadata about the latest analysis"""
        metadata = {
            'last_run': datetime.now().isoformat(),
            'result_count': result_count,
            'config': self.default_config,
            'status': 'success'
        }

        metadata_file = self.results_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)


def main():
    """Main entry point for scheduler"""
    analyzer = ScheduledAnalyzer()
    analyzer.run_scheduled_analysis()


if __name__ == "__main__":
    main()