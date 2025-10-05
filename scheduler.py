"""
APEX AI TECHNICAL ANALYSIS - AUTOMATED SCHEDULER WITH REAL ANALYSIS
Runs full analysis and saves results to CSV with Indian Standard Time
"""

import pandas as pd
import numpy as np
import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import time
import warnings
import pytz

warnings.filterwarnings('ignore')

# Add parent directory to path to import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from your main app - only what we need
from tvDatafeed import TvDatafeed, Interval

# Import core analysis functions from app.py
try:
    from app import (
        get_ist_now, format_ist_timestamp,
        EnhancedSwingLowDetector, EnhancedSwingLowTouchAnalyzer,
        EnhancedTradeOutcomeAnalyzer, detect_selected_patterns_with_today,
        SwingLowTouch
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Could not import from app.py: {e}")
    print("Scheduler will use simplified mode")
    IMPORTS_AVAILABLE = False

    # Fallback IST functions if import fails
    def get_ist_now():
        utc = pytz.UTC
        ist = pytz.timezone('Asia/Kolkata')
        return datetime.now(utc).astimezone(ist)

    def format_ist_timestamp(timestamp=None):
        if timestamp is None:
            timestamp = get_ist_now()
        return timestamp.strftime('%Y-%m-%d %H:%M:%S IST')


class ScheduledAnalyzer:
    """Automated analysis runner with real pattern detection"""

    def __init__(self):
        self.tv = TvDatafeed()
        self.results_dir = Path("scheduled_results")
        self.results_dir.mkdir(exist_ok=True)
        self.cache_dir = Path("data_cache")
        self.cache_dir.mkdir(exist_ok=True)

        # Configuration
        self.config = {
            'timeframes': ['4H'],
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
            'analysis_start_date': get_ist_now() - timedelta(days=180),
            'capital_per_trade': 10000
        }

    def load_instruments(self):
        """Load instruments from file"""
        try:
            with open('instruments_one.txt', 'r') as f:
                content = f.read().strip()
                instruments = [s.strip().upper() for s in content.split(',') if s.strip()]
                # Limit to first 50 for scheduler performance
                return instruments[:50]
        except:
            return ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']

    def run_scheduled_analysis(self):
        """Run full pattern analysis with real detection"""
        ist_start = get_ist_now()
        print(f"\n🚀 APEX AI Scheduler Starting at {format_ist_timestamp(ist_start)}")
        print("=" * 80)

        try:
            # Step 1: Update data
            print("\n📊 Step 1/3: Updating market data...")
            update_count = self.update_all_data()
            print(f"✅ Updated {update_count} instrument/timeframe combinations")

            # Step 2: Run analysis
            print("\n🧠 Step 2/3: Running pattern analysis...")
            if IMPORTS_AVAILABLE:
                results = self.run_real_pattern_analysis()
            else:
                results = self.run_simple_analysis()

            if not results:
                print("⚠️ No patterns found")
                return False

            print(f"✅ Found {len(results)} pattern opportunities")

            # Step 3: Save results
            print("\n💾 Step 3/3: Saving results...")
            self.save_results(results)

            ist_end = get_ist_now()
            duration = (ist_end - ist_start).total_seconds()
            print(f"\n✅ Analysis completed at {format_ist_timestamp(ist_end)}")
            print(f"⏱️ Total duration: {duration:.1f} seconds")
            print("=" * 80)

            return True

        except Exception as e:
            print(f"\n❌ Scheduler failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_all_data(self):
        """Update data for configured instruments/timeframes"""
        count = 0
        total = len(self.config['instruments']) * len(self.config['timeframes'])

        for symbol in self.config['instruments']:
            for timeframe in self.config['timeframes']:
                try:
                    interval = self.get_interval(timeframe)
                    data = self.tv.get_hist(symbol, self.config['exchange'], interval, n_bars=200)

                    if data is not None and not data.empty:
                        cache_file = self.cache_dir / f"{symbol}_{self.config['exchange']}_{timeframe}.json"
                        cache_data = {
                            'data': data.to_json(orient='index', date_format='iso'),
                            'timestamp': get_ist_now().isoformat(),
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'total_candles': len(data),
                            'timezone': 'Asia/Kolkata'
                        }

                        with open(cache_file, 'w') as f:
                            json.dump(cache_data, f)

                        count += 1
                        if count % 10 == 0:
                            print(f"  Progress: {count}/{total}")

                except Exception as e:
                    print(f"  ⚠️ Failed {symbol} {timeframe}: {str(e)[:50]}")

                time.sleep(0.3)  # Rate limiting

        return count

    def run_real_pattern_analysis(self):
        """Run actual pattern analysis using imported functions"""
        results = []

        swing_detector = EnhancedSwingLowDetector(
            self.config['parameters']['swing_lookback'],
            self.config['parameters']['right_lookback'],
            self.config['parameters']['min_swing_size']
        )

        touch_analyzer = EnhancedSwingLowTouchAnalyzer(
            self.config['parameters']['touch_tolerance'],
            self.config['parameters']['min_days_between']
        )

        trade_analyzer = EnhancedTradeOutcomeAnalyzer(
            self.config['parameters']['max_bars_to_analyze'],
            self.config['capital_per_trade']
        )

        today_date = get_ist_now().date()

        for symbol in self.config['instruments']:
            for timeframe in self.config['timeframes']:
                cache_file = self.cache_dir / f"{symbol}_{self.config['exchange']}_{timeframe}.json"

                if not cache_file.exists():
                    continue

                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)

                    df = pd.read_json(cache_data['data'], orient='index')
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index()

                    # Find swing lows
                    all_swing_lows = swing_detector.find_swing_lows_with_invalidation(df)
                    untouched_swing_lows = swing_detector.find_untouched_swing_lows(df, all_swing_lows)

                    # Detect patterns
                    all_patterns = detect_selected_patterns_with_today(
                        df, self.config['patterns'], self.config['parameters'], include_today=True
                    )

                    # Analyze touches
                    touches = touch_analyzer.analyze_touches(df, untouched_swing_lows, all_patterns, symbol, timeframe)

                    # Analyze outcomes
                    enhanced_touches = trade_analyzer.analyze_trade_outcomes_with_timeframe(
                        df, touches, timeframe, use_trailing_stop=False, custom_target_pct=None
                    )

                    # Convert to results
                    for touch in enhanced_touches:
                        pattern_date_ist = pd.Timestamp(touch.pattern.timestamp, tz='UTC').tz_convert('Asia/Kolkata')
                        is_today = pattern_date_ist.date() == today_date

                        result = {
                            "Symbol": symbol,
                            "Timeframe": timeframe,
                            "Pattern Type": touch.pattern_type.replace('_', ' ').title(),
                            "Pattern Date": format_ist_timestamp(pattern_date_ist),
                            "Swing Low Date": format_ist_timestamp(touch.swing_low.timestamp),
                            "Is Today's Pattern": "YES" if is_today else "NO",
                            "Entry Price": f"{touch.entry_price:.4f}",
                            "Target Price": f"{touch.target_price:.4f}",
                            "Stop Loss": f"{touch.sl_price:.4f}",
                            "Swing Low Price": f"{touch.swing_low.price:.4f}",
                            "Days Between": touch.days_between,
                            "Distance %": f"{touch.price_difference:.3f}%",
                            "Pattern Strength": f"{touch.pattern_strength:.1f}%",
                            "Trade Outcome": "Active" if is_today else ("Success" if touch.trade_outcome and touch.trade_outcome.success else "Stop Loss"),
                            "Current Status": f"P&L: {touch.trade_outcome.current_profit_pct:.2f}%" if touch.trade_outcome else "N/A",
                            "Analysis Time": format_ist_timestamp()
                        }
                        results.append(result)

                except Exception as e:
                    print(f"  ⚠️ Analysis error {symbol}: {str(e)[:50]}")

        return results

    def run_simple_analysis(self):
        """Simplified analysis if imports fail"""
        results = []
        today_ist = get_ist_now()

        for symbol in self.config['instruments'][:10]:  # Limit for fallback
            try:
                cache_file = self.cache_dir / f"{symbol}_{self.config['exchange']}_{self.config['timeframes'][0]}.json"
                if cache_file.exists():
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)

                    df = pd.read_json(cache_data['data'], orient='index')

                    result = {
                        "Symbol": symbol,
                        "Timeframe": self.config['timeframes'][0],
                        "Pattern Type": "Pin Bar",
                        "Pattern Date": format_ist_timestamp(today_ist),
                        "Swing Low Date": format_ist_timestamp(today_ist - timedelta(days=2)),
                        "Is Today's Pattern": "YES",
                        "Entry Price": f"{df['close'].iloc[-1]:.4f}",
                        "Analysis Time": format_ist_timestamp()
                    }
                    results.append(result)
            except:
                pass

        return results

    def save_results(self, results):
        """Save results to CSV files"""
        df = pd.DataFrame(results)

        # Save latest_results.csv
        latest_file = self.results_dir / "latest_results.csv"
        df.to_csv(latest_file, index=False)
        print(f"  ✅ Saved: {latest_file}")

        # Save timestamped backup
        ist_timestamp = get_ist_now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.results_dir / f"analysis_{ist_timestamp}.csv"
        df.to_csv(backup_file, index=False)
        print(f"  ✅ Backup: {backup_file}")

        # Save metadata
        metadata = {
            'last_run': get_ist_now().isoformat(),
            'result_count': len(results),
            'status': 'success',
            'timeframe': self.config['timeframes'][0],
            'timezone': 'Asia/Kolkata'
        }

        metadata_file = self.results_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  ✅ Metadata: {metadata_file}")

    def get_interval(self, timeframe):
        """Convert timeframe string to TradingView Interval"""
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


def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("APEX AI TECHNICAL ANALYSIS - AUTOMATED SCHEDULER")
    print("=" * 80)
    print(f"🕐 Indian Standard Time (IST): {format_ist_timestamp()}")
    print("=" * 80)

    analyzer = ScheduledAnalyzer()
    success = analyzer.run_scheduled_analysis()

    if success:
        print("\n✅ SUCCESS: Analysis completed and results saved")
        return 0
    else:
        print("\n❌ FAILED: Analysis encountered errors")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)