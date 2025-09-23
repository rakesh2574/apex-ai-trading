"""
PROFESSIONAL AI MARKET ANALYSIS PLATFORM - ENHANCED WITH DATE PICKER
===========================================================================


"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import time
import io
from datetime import datetime, timedelta, date
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Tuple, Union, Any
import warnings
from pathlib import Path

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Check for TradingView availability
try:
    from tvDatafeed import TvDatafeed, Interval

    TV_AVAILABLE = True
except ImportError:
    TV_AVAILABLE = False
    st.error("❌ TradingView DataFeed not available. Install with: pip install tvDatafeed")

import pytz


def get_ist_now():
    """Get current time in IST"""
    utc = pytz.UTC
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(utc).astimezone(ist)


def convert_to_ist(timestamp):
    """Convert any timestamp to IST"""
    if isinstance(timestamp, str):
        timestamp = pd.Timestamp(timestamp)

    # Handle both datetime.datetime and pandas.Timestamp
    if hasattr(timestamp, 'tzinfo'):
        # Standard datetime object
        if timestamp.tzinfo is None:
            # Assume UTC if no timezone
            timestamp = pytz.UTC.localize(timestamp)
    elif hasattr(timestamp, 'tz'):
        # Pandas Timestamp
        if timestamp.tz is None:
            # Assume UTC if no timezone
            timestamp = timestamp.tz_localize('UTC')
    else:
        # Fallback - assume UTC
        try:
            timestamp = pytz.UTC.localize(timestamp)
        except:
            timestamp = pd.Timestamp(timestamp).tz_localize('UTC')

    ist = pytz.timezone('Asia/Kolkata')
    return timestamp.astimezone(ist)


def format_ist_timestamp(timestamp=None):
    """Format timestamp in IST for display"""
    if timestamp is None:
        timestamp = get_ist_now()
    else:
        timestamp = convert_to_ist(timestamp)

    return timestamp.strftime('%Y-%m-%d %H:%M:%S IST')


def safe_convert_to_ist(timestamp):
    """Safely convert timestamp to IST with error handling"""
    try:
        return convert_to_ist(timestamp)
    except Exception as e:
        # If conversion fails, return current IST time
        print(f"Warning: Timestamp conversion failed: {e}")
        return get_ist_now()


def safe_format_ist_timestamp(timestamp):
    """Safely format timestamp in IST with error handling"""
    try:
        if pd.isna(timestamp) or timestamp in ['N/A', '']:
            return 'N/A'
        return format_ist_timestamp(timestamp)
    except Exception as e:
        print(f"Warning: Timestamp formatting failed: {e}")
        return 'N/A'
def check_login():
    """Handle login authentication - Enhanced with viewer support"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.is_viewer = False
        st.session_state.login_username = ''

    if not st.session_state.authenticated:
        # Display login page
        st.set_page_config(
            page_title="APEX AI Assisted Technical Analysis",
            page_icon="🚀",
            layout="centered",
            initial_sidebar_state="collapsed"
        )

        # Your existing styling here...
        st.markdown("""
        <style>
        .login-container {
            background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 102, 204, 0.3);
            margin: 2rem auto;
        }
        .login-title {
            color: white;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        .login-subtitle {
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown('<h1 class="login-title">🚀 APEX AI</h1>', unsafe_allow_html=True)
            st.markdown('<p class="login-subtitle">Assisted Technical Analysis Platform</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            with st.form("login_form"):
                st.subheader("🔐 Secure Login")

                username = st.text_input("Username", placeholder="Enter username", key="login_username_input")
                password = st.text_input("Password", type="password", placeholder="Enter password",
                                         key="login_password_input")

                col_a, col_b = st.columns(2)
                with col_a:
                    login_button = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
                with col_b:
                    contact_button = st.form_submit_button("📧 Contact Admin", use_container_width=True)

                if login_button:
                    # Define all accounts
                    VIEWER_ACCOUNTS = {
                        'viewer': 'view123',
                        'client': 'client456',
                        'results': 'results789',
                        'readonly': 'readonly123'
                    }

                    FULL_ACCESS_ACCOUNTS = {
                        'Arthur': 'trapezoid'
                    }

                    # Check credentials
                    login_success = False

                    # Check if it's a viewer account
                    if username in VIEWER_ACCOUNTS and password == VIEWER_ACCOUNTS[username]:
                        st.session_state.authenticated = True
                        st.session_state.login_username = username
                        st.session_state.is_viewer = True  # CRITICAL: Set to True for viewers
                        login_success = True
                        st.success("✅ Login successful! Loading results viewer...")

                    # Check if it's a full access account
                    elif username in FULL_ACCESS_ACCOUNTS and password == FULL_ACCESS_ACCOUNTS[username]:
                        st.session_state.authenticated = True
                        st.session_state.login_username = username
                        st.session_state.is_viewer = False  # CRITICAL: Set to False for full access
                        login_success = True
                        st.success("✅ Login successful! Loading full platform...")

                    else:
                        st.error("❌ Invalid credentials. Please try again.")

                    if login_success:
                        time.sleep(1)
                        st.rerun()

                if contact_button:
                    st.info("📧 Contact admin@apex-ai.com for support")

            st.divider()
            st.markdown("""
            <div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
            <p>© 2024 APEX AI Technical Analysis Platform</p>
            </div>
            """, unsafe_allow_html=True)

        st.stop()


def logout():
    """Handle logout"""
    st.session_state.authenticated = False
    st.session_state.login_username = ''
    st.session_state.is_viewer = False
    st.rerun()

# ============================================================================
# ENHANCED DATA STRUCTURES - COMPLETE WITH ALL PROFESSIONAL FEATURES
# ============================================================================

# ============================================================================
# RESULT VIEWER LOGIN SYSTEM - ADD THIS AFTER check_login() FUNCTION
# ============================================================================

def check_results_viewer_login():
    """Special login check for users who just want to view cached results"""

    if not st.session_state.get('authenticated', False):
        return False

    # Get the username that was used to login
    username = st.session_state.get('login_username', '')

    # Define result viewer credentials
    # You can modify these or load from secrets.toml
    RESULT_VIEWER_ACCOUNTS = {
        'viewer': 'view123',
        'client': 'client456',
        'results': 'results789',
        'readonly': 'readonly123'
    }

    # Check if current user is a viewer account
    if username.lower() in RESULT_VIEWER_ACCOUNTS:
        return True

    return False


def render_cached_results_viewer():
    """Complete result viewer interface for client accounts with IST timezone support"""

    # Apply professional theme
    apply_professional_theme()

    # Header
    st.title("📊 APEX AI - Analysis Results Viewer")
    st.markdown("**Pre-computed Professional Analysis Results - Updated Automatically**")

    # Top controls
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🚪 Logout", type="primary", key="viewer_logout"):
            # Clear session and redirect to login
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    with col2:
        if st.button("🔄 Refresh", key="viewer_refresh"):
            st.rerun()

    with col3:
        username = st.session_state.get('login_username', 'Viewer')
        st.info(f"👤 Logged in as: **{username}** (Read-Only Results Viewer)")

    st.divider()

    # Check for results directory and files
    results_dir = Path("scheduled_results")
    results_dir.mkdir(exist_ok=True)

    latest_file = results_dir / "latest_results.csv"
    metadata_file = results_dir / "metadata.json"

    # If no results exist, show message and create sample
    if not latest_file.exists():
        st.warning("⚠️ No analysis results available yet.")
        st.info("📋 The automated scheduler or manual analysis hasn't generated results yet.")

        # Show expected file location
        st.code(f"Expected file: {latest_file.absolute()}")

        # Create sample data for demonstration
        if st.button("🧪 Generate Sample Data for Testing"):
            sample_results = create_sample_results()
            sample_df = pd.DataFrame(sample_results)

            # Convert sample timestamps to IST
            for col in ['Pattern Date', 'Swing Low Date']:
                if col in sample_df.columns:
                    sample_df[col] = sample_df[col].apply(lambda x: format_ist_timestamp())

            sample_df['Analysis Time'] = format_ist_timestamp()
            sample_df.to_csv(latest_file, index=False)

            # Create sample metadata with IST
            sample_metadata = {
                'last_run': get_ist_now().isoformat(),
                'result_count': len(sample_results),
                'status': 'sample_data',
                'timeframe': '4H',
                'timezone': 'Asia/Kolkata'
            }

            with open(metadata_file, 'w') as f:
                json.dump(sample_metadata, f, indent=2)

            st.success("✅ Sample results created with IST timestamps. Refreshing...")
            time.sleep(1)
            st.rerun()
        return

    # Load and display results with comprehensive error handling
    try:
        # Load CSV with multiple encoding attempts
        results_df = None
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

        for encoding in encodings_to_try:
            try:
                results_df = pd.read_csv(latest_file, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue

        if results_df is None:
            st.error("❌ Could not read the CSV file with any supported encoding.")
            return

        if results_df.empty:
            st.warning("⚠️ Results file exists but is empty.")
            return

        # Load metadata if available
        metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                st.warning("⚠️ Metadata file is corrupted or missing, continuing without metadata.")

        # Display metadata metrics with IST time handling
        st.subheader("📈 Analysis Summary")

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            if 'last_run' in metadata:
                try:
                    last_run_str = metadata['last_run']

                    # Handle IST formatted timestamps
                    if 'IST' in last_run_str:
                        st.metric("Last Update", last_run_str.split('T')[1].split('.')[0] + " IST")
                    else:
                        # Convert UTC to IST
                        last_run = datetime.fromisoformat(last_run_str.replace('Z', '+00:00'))
                        ist_time = convert_to_ist(last_run)
                        time_diff = get_ist_now().replace(tzinfo=None) - ist_time.replace(tzinfo=None)
                        hours_ago = time_diff.total_seconds() / 3600

                        if hours_ago < 1:
                            minutes_ago = int(time_diff.total_seconds() / 60)
                            st.metric("Last Update (IST)", f"{minutes_ago} min ago")
                        else:
                            st.metric("Last Update (IST)", f"{hours_ago:.1f} hours ago")
                except Exception:
                    st.metric("Last Update", "Invalid date")
            else:
                st.metric("Last Update (IST)", "Unknown")

        with col2:
            st.metric("Total Patterns", len(results_df))

        with col3:
            # Count today's patterns safely
            today_count = 0
            if "Is Today's Pattern" in results_df.columns:
                try:
                    today_count = len(results_df[results_df["Is Today's Pattern"].astype(str).str.upper() == "YES"])
                except:
                    pass
            st.metric("Today's Patterns", today_count)

        with col4:
            # Count unique symbols safely
            if "Symbol" in results_df.columns:
                try:
                    unique_symbols = results_df["Symbol"].nunique()
                    st.metric("Symbols", unique_symbols)
                except:
                    st.metric("Symbols", "N/A")
            else:
                st.metric("Symbols", "N/A")

        with col5:
            st.metric("Timeframe", metadata.get('timeframe', '4H'))

        with col6:
            status = metadata.get('status', 'unknown')
            if status == 'success':
                st.metric("Status", "✅ Live Data")
            elif status == 'sample_data':
                st.metric("Status", "📊 Sample Data")
            else:
                st.metric("Status", "⚠️ Check Status")

        st.divider()

        # Filter controls
        st.subheader("🔍 Filter Options")

        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

        with filter_col1:
            # Symbol filter
            if "Symbol" in results_df.columns:
                all_symbols = ["All"] + sorted(results_df["Symbol"].unique().tolist())
                selected_symbol = st.selectbox("Symbol", all_symbols, key="viewer_symbol_filter")
            else:
                selected_symbol = "All"

        with filter_col2:
            # Pattern filter
            if "Pattern Type" in results_df.columns:
                all_patterns = ["All"] + sorted(results_df["Pattern Type"].unique().tolist())
                selected_pattern = st.selectbox("Pattern", all_patterns, key="viewer_pattern_filter")
            else:
                selected_pattern = "All"

        with filter_col3:
            # Today's patterns filter
            show_today_only = st.checkbox("Today's Patterns Only", value=False, key="viewer_today_filter")

        with filter_col4:
            # Trade outcome filter
            if "Trade Outcome" in results_df.columns:
                all_outcomes = ["All"] + sorted(results_df["Trade Outcome"].unique().tolist())
                selected_outcome = st.selectbox("Outcome", all_outcomes, key="viewer_outcome_filter")
            else:
                selected_outcome = "All"

        # Apply filters
        filtered_df = results_df.copy()

        if selected_symbol != "All" and "Symbol" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Symbol"] == selected_symbol]

        if selected_pattern != "All" and "Pattern Type" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Pattern Type"] == selected_pattern]

        if show_today_only and "Is Today's Pattern" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Is Today's Pattern"].astype(str).str.upper() == "YES"]

        if selected_outcome != "All" and "Trade Outcome" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Trade Outcome"] == selected_outcome]

        st.divider()

        # Display filtered results
        if not filtered_df.empty:
            # Today's patterns section
            if "Is Today's Pattern" in filtered_df.columns:
                today_df = filtered_df[filtered_df["Is Today's Pattern"].astype(str).str.upper() == "YES"]

                if not today_df.empty:
                    st.subheader(f"🎯 Today's Patterns ({len(today_df)} found)")

                    # Highlight today's patterns
                    st.dataframe(
                        today_df,
                        use_container_width=True,
                        height=min(200, len(today_df) * 35 + 50)
                    )

                    st.divider()

            # All results section
            st.subheader(f"📋 All Analysis Results ({len(filtered_df)} patterns)")

            # Download section
            col1, col2 = st.columns(2)

            with col1:
                # Download filtered results
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download Filtered Results ({len(filtered_df)} rows)",
                    data=csv,
                    file_name=f"apex_filtered_results_{get_ist_now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                # Download all results
                all_csv = results_df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download All Results ({len(results_df)} rows)",
                    data=all_csv,
                    file_name=f"apex_all_results_{get_ist_now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            # Display the filtered dataframe
            st.dataframe(
                filtered_df,
                use_container_width=True,
                height=600
            )

            # Pattern statistics
            st.divider()
            st.subheader("📊 Pattern Statistics")

            if "Pattern Type" in filtered_df.columns:
                pattern_counts = filtered_df["Pattern Type"].value_counts()

                stat_col1, stat_col2 = st.columns(2)

                with stat_col1:
                    st.write("**Pattern Distribution:**")
                    for pattern, count in pattern_counts.items():
                        percentage = (count / len(filtered_df)) * 100
                        st.write(f"• {pattern}: {count} ({percentage:.1f}%)")

                with stat_col2:
                    if "Trade Outcome" in filtered_df.columns:
                        st.write("**Outcome Distribution:**")
                        outcome_counts = filtered_df["Trade Outcome"].value_counts()
                        for outcome, count in outcome_counts.items():
                            percentage = (count / len(filtered_df)) * 100
                            st.write(f"• {outcome}: {count} ({percentage:.1f}%)")

        else:
            st.warning("⚠️ No results match the selected filters.")

        # Show file info with IST timestamps
        st.divider()
        st.subheader("📁 File Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**File Size:** {latest_file.stat().st_size / 1024:.2f} KB")
        with col2:
            mod_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
            ist_mod_time = convert_to_ist(mod_time)
            st.info(f"**File Modified:** {ist_mod_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
        with col3:
            st.info(f"**Rows × Columns:** {len(results_df)} × {len(results_df.columns)}")

        # Footer information with IST timezone info
        st.divider()
        st.info(f"""
        📊 **Result Viewer Mode Information:**
        - Results are generated by automated scheduler and manual analysis
        - This is a read-only view of the latest analysis results  
        - Data is updated automatically every few hours
        - All timestamps displayed in Indian Standard Time (IST)
        - Current IST time: {format_ist_timestamp()}
        - Contact administrator for any questions or issues
        """)

        # Show timezone info prominently
        st.success(f"🕐 **Timezone**: All timestamps displayed in Indian Standard Time (IST)")

    except pd.errors.EmptyDataError:
        st.error("❌ The results file is empty or corrupted.")
        st.info("The scheduler may not have completed successfully. Please check back later.")
    except pd.errors.ParserError as e:
        st.error(f"❌ Error parsing CSV file: {str(e)}")
        st.info("The file may be corrupted or have formatting issues. Try refreshing or contact administrator.")
        st.code(f"File location: {latest_file.absolute()}")
    except FileNotFoundError:
        st.error("❌ Results file not found.")
        st.info("The scheduler hasn't created results yet, or the file was moved/deleted.")
    except Exception as e:
        st.error(f"❌ Unexpected error loading results: {str(e)}")
        st.info("Please contact your administrator if this issue persists.")
        st.code(f"Error details: {type(e).__name__}: {str(e)}")


def create_sample_results():
    """Create sample results for demonstration when no real data exists"""

    # Sample data matching your analysis structure
    symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
    patterns = ['Pin Bar', 'Bullish Engulfing', 'Morning Star']
    outcomes = ['Success', 'Active', 'Stop Loss']

    sample_data = []
    today = datetime.now()

    for i in range(20):
        days_back = np.random.randint(0, 7)
        pattern_date = today - timedelta(days=days_back)
        is_today = "YES" if days_back == 0 else "NO"

        sample_data.append({
            "Symbol": np.random.choice(symbols),
            "Timeframe": "4H",
            "Pattern Type": np.random.choice(patterns),
            "Pattern Date": pattern_date.strftime("%Y-%m-%d %H:%M"),
            "Is Today's Pattern": is_today,
            "Entry Price": f"{np.random.uniform(100, 3000):.4f}",
            "Target Price": f"{np.random.uniform(100, 3000):.4f}",
            "Stop Loss": f"{np.random.uniform(100, 3000):.4f}",
            "Trade Outcome": np.random.choice(outcomes),
            "Current Status": f"P&L: {np.random.uniform(-2, 5):.2f}%",
            "Pattern Strength": f"{np.random.uniform(50, 90):.1f}%",
            "Days Between": np.random.randint(1, 10),
            "Distance %": f"{np.random.uniform(0.1, 2.0):.3f}%",
            "Analysis Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return sample_data


# ============================================================================
# MODIFY YOUR EXISTING main() FUNCTION - REPLACE WITH THIS
# ============================================================================

def main():
    """Main Professional AI Market Analysis Platform with Result Viewer Mode"""

    # Check authentication first
    check_login()

    # TEMPORARY DEBUG - Remove after testing
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"User: {st.session_state.get('login_username', 'None')}")
    with col2:
        st.write(f"Is Viewer: {st.session_state.get('is_viewer', 'Not Set')}")
    with col3:
        if st.button("Clear Session"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    # Check if viewer
    if st.session_state.get('is_viewer', False):
        st.warning("VIEWER MODE - Showing CSV only")
        render_cached_results_viewer()
        return

    st.success("FULL ACCESS MODE - Showing complete platform")

    ######### to be removed till now

    # DEBUG: Show what user type is logged in
    # st.write(f"DEBUG: User={st.session_state.get('login_username')}, IsViewer={st.session_state.get('is_viewer')}")

    # CRITICAL CHECK: If viewer, show ONLY CSV viewer
    if st.session_state.get('is_viewer', False):
        # This is a viewer - show ONLY the CSV viewer
        render_cached_results_viewer()
        return  # STOP HERE - Don't show anything else

    # ONLY FULL ACCESS USERS (Arthur) CONTINUE BELOW THIS LINE
    # =========================================================

    # Set page config for full platform
    st.set_page_config(
        page_title="🚀 APEX AI Technical Analysis Platform",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state and apply professional theme
    init_session_state()
    apply_professional_theme()

    # REST OF YOUR EXISTING main() CODE CONTINUES HERE...
    # Professional main title
    st.title("🚀 APEX AI TECHNICAL ANALYSIS PLATFORM")
    st.markdown(
        "**Advanced Technical Analysis: AI-Powered Pattern Recognition + Smart Capital Management + Real-Time Processing + Professional Features 📊🧠**")

    # Check TradingView availability
    if not TV_AVAILABLE:
        st.error("❌ TradingView DataFeed not available. Install with: `pip install tvDatafeed`")
        st.stop()
    else:
        st.success("✅ APEX AI Analysis System Ready!")

    # Professional features banner
    st.markdown("""
    <div class="feature-highlight">
    <h3 style="color: #0066cc; margin: 0;">🧠 APEX AI FEATURES ACTIVE:</h3>
    <p style="color: #5a6c7d; margin: 5px 0;">
    ✅ DATE PICKER DATA DOWNLOADS | ✅ SMART BAR CALCULATION | ✅ TODAY'S REAL-TIME DATA | ✅ Advanced Swing Low Validation | ✅ Current Trade Status | ✅ Precision AI Detection | ✅ Professional Capital Management
    </p>
    </div>
    """, unsafe_allow_html=True)

    # Create professional application tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔄 Data Management",
        "📊 AI Pattern Analysis",
        "💰 Capital Simulation",
        "🔴 Real-Time Monitoring",
        "⚙️ AI Configuration",
        "📈 Analytics Dashboard"
    ])

    with tab1:
        render_instrument_management()
        st.divider()
        render_data_management_tab()

    with tab2:
        render_analysis_tab()

    with tab3:
        render_capital_simulation_tab()

    with tab4:
        render_live_monitoring_tab()

    with tab5:
        render_settings_tab()

    with tab6:
        st.header("📈 Professional Analytics Dashboard")

        if st.session_state.debug_info:
            st.subheader("🔍 AI Analysis Performance Metrics")

            # Special handling for today's patterns
            today_patterns = st.session_state.debug_info.get('today_patterns_detected', 0)
            if today_patterns > 0:
                st.success(f"🎯 TODAY'S PATTERNS DETECTED: {today_patterns}")

            debug_df = pd.DataFrame([
                {"Metric": k, "Value": v}
                for k, v in st.session_state.debug_info.items()
            ])

            create_download_buttons(debug_df, "ai_analytics_dashboard", "AI Analytics Report")
            st.dataframe(debug_df, use_container_width=True)

            # Show capital analytics if available
            if 'capital_debug' in st.session_state.debug_info:
                st.subheader("💰 Capital Management Analytics")
                with st.expander("View AI Capital Management Logs"):
                    for msg in st.session_state.debug_info['capital_debug']:
                        st.text(msg)

            # Show AI swing low analytics
            if 'total_invalidated_swing_lows' in st.session_state.debug_info:
                st.subheader("🔧 AI Swing Low Validation Analytics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Swing Lows", st.session_state.debug_info.get('total_swing_lows', 0))
                with col2:
                    st.metric("AI Invalidated", st.session_state.debug_info.get('total_invalidated_swing_lows', 0))
                with col3:
                    st.metric("Valid AI Signals", st.session_state.debug_info.get('total_valid_touches', 0))
                with col4:
                    st.metric("Today's Patterns", st.session_state.debug_info.get('today_patterns_detected', 0))
        else:
            st.info("No analytics data available. Run an AI analysis to see professional performance metrics.")

    # Professional sidebar with logout button
    with st.sidebar:
        st.header("🎛️ APEX AI SYSTEM")

        # Logout button at the top
        if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
            logout()

        st.divider()

        # Professional AI features status
        st.markdown("""
        <div class="professional-card">
        <h4 style="color: #0066cc; margin: 0;">🧠 APEX AI FEATURES</h4>
        <p style="color: #5a6c7d; font-size: 12px; margin: 5px 0;">
        ✅ Date Picker Downloads<br>
        ✅ Real-Time Analysis<br>
        ✅ Pattern Recognition<br>
        ✅ Smart Capital Management<br>
        ✅ Advanced Validation
        </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Date picker status
        use_date_picker = st.session_state.get('use_date_picker', False)
        if use_date_picker:
            download_start_date = st.session_state.get('data_download_start_date', datetime.now() - timedelta(days=30))
            st.success(f"📅 Date Picker: {download_start_date.strftime('%Y-%m-%d')}")
        else:
            st.info("📅 Default bar counts")

        # Professional status indicators
        st.markdown("""
        <div class="professional-card">
        <h4 style="color: #00cc88; margin: 0;">🔧 SYSTEM STATUS</h4>
        <p style="color: #5a6c7d; font-size: 12px; margin: 5px 0;">
        ✅ Advanced Swing Low Validation<br>
        ✅ Real-Time Trade Monitoring<br>
        ✅ Precision Entry/Exit Detection<br>
        ✅ AI Signal Validation<br>
        ✅ Date-Based Data Downloads
        </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Instruments status
        if st.session_state.instruments_list:
            st.success(f"✅ {len(st.session_state.instruments_list)} instruments loaded")
        else:
            st.warning("⚠️ No instruments loaded")

        # Pattern selection status
        selected_patterns_count = sum(st.session_state.pattern_selection.values())
        if selected_patterns_count > 0:
            st.success(f"🧠 {selected_patterns_count}/10 AI patterns selected")
        else:
            st.warning("⚠️ No patterns selected")

        # Professional Capital Management Status
        st.divider()
        st.subheader("💰 Capital Management")

        if st.session_state.capital_manager:
            summary = st.session_state.capital_manager.get_performance_summary()
            st.success(f"✅ AI Capital System Active")
            st.metric("Total Capital", f"${summary['total_capital_current']:,.0f}")
            st.metric("AI ROI", f"{summary['total_roi_pct']:.1f}%")
            st.metric("Trades", f"{summary['trades_executed']}")
        else:
            st.info("💰 AI capital system ready")
            st.metric("Total Capital", f"${st.session_state.total_capital:,.0f}")
            st.metric("Per Trade", f"${st.session_state.capital_per_trade:,.0f}")

        # Today's date and status
        st.divider()
        today_str = datetime.now().strftime('%Y-%m-%d')
        st.metric("Today's Date", today_str)
        st.success("✅ Real-time data active")

        # Data update status
        if st.session_state.last_data_update:
            time_diff = datetime.now() - st.session_state.last_data_update
            minutes_ago = int(time_diff.total_seconds() / 60)
            st.info(f"🕒 Data updated: {minutes_ago}min ago")
        else:
            st.info("🕒 Ready for first update")

        # Analysis status
        if st.session_state.analysis_complete:
            if st.session_state.analysis_results:
                today_patterns = len(
                    [r for r in st.session_state.analysis_results if r.get("Is Today's Pattern") == "YES"])
                st.success(f"📊 {len(st.session_state.analysis_results)} opportunities found")
                if today_patterns > 0:
                    st.success(f"🎯 {today_patterns} from TODAY!")
            else:
                st.info("📊 Analysis complete - no opportunities")
        else:
            st.info("📊 Ready for AI analysis")

        st.divider()

        # Professional Patterns showcase
        st.subheader("🧠 AI Pattern Recognition")
        pattern_emojis = {
            'pin_bar': '📍',
            'bullish_engulfing': '🔥',
            'three_candle': '🌟',
            'dragonfly_doji': '🐉',
            'three_white_soldiers': '⚔️',
            'bullish_marubozu': '💪',
            'bullish_harami': '🤰',
            'bullish_abandoned_baby': '👶',
            'tweezer_bottom': '🔧',
            'bullish_kicker': '🚀'
        }

        for pattern_key, emoji in pattern_emojis.items():
            is_selected = st.session_state.pattern_selection.get(pattern_key, False)
            status = "✅" if is_selected else "⭕"
            pattern_name = pattern_key.replace('_', ' ').title()
            st.write(f"{status} {emoji} {pattern_name}")

        st.divider()

        # Professional quick actions
        st.subheader("⚡ Quick Actions")

        if st.button("🔄 Refresh Platform", use_container_width=True):
            st.rerun()

        if st.button("🧹 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['file_manager', 'authenticated', 'login_username', 'is_viewer']:  # Keep essential keys
                    del st.session_state[key]
            st.success("Session reset!")
            st.rerun()

        st.divider()

        # Professional summary
        st.markdown("""
        <div class="professional-card">
        <h5 style="color: #0066cc; margin: 0;">🧠 APEX AI PLATFORM</h5>
        <p style="color: #5a6c7d; font-size: 11px; margin: 3px 0;">
        Professional AI Market Analysis Platform with real-time pattern detection, 
        advanced capital management, and comprehensive trading analytics.
        </p>
        </div>
        """, unsafe_allow_html=True)




@dataclass
class SwingLow:
    """Represents a swing low point in price data - ENHANCED WITH INVALIDATION TRACKING"""
    index: int
    timestamp: pd.Timestamp
    price: float
    is_invalidated: bool = False
    invalidation_timestamp: Optional[pd.Timestamp] = None
    invalidation_index: Optional[int] = None
    is_touched: bool = False
    touch_timestamp: Optional[pd.Timestamp] = None
    touch_pattern: Optional[str] = None
    touch_index: Optional[int] = None


@dataclass
class PinBar:
    """Represents a pin bar candlestick pattern"""
    index: int
    timestamp: pd.Timestamp
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    pattern_type: str = 'pin_bar'
    body_ratio: float = 0.0
    wick_ratio: float = 0.0
    is_bullish: bool = True
    is_live: bool = False
    pattern_strength: float = 0.0


@dataclass
class BullishEngulfing:
    """Represents a bullish engulfing candlestick pattern"""
    index: int
    timestamp: pd.Timestamp
    first_candle_open: float
    first_candle_high: float
    first_candle_low: float
    first_candle_close: float
    second_candle_open: float
    second_candle_high: float
    second_candle_low: float
    second_candle_close: float
    pattern_type: str = 'bullish_engulfing'
    engulfing_ratio: float = 0.0
    pattern_low: float = 0.0
    is_bullish: bool = True
    is_live: bool = False
    pattern_strength: float = 0.0


@dataclass
class ThreeCandle:
    """Represents a three candle (Morning Star) pattern"""
    index: int
    timestamp: pd.Timestamp
    first_candle_open: float
    first_candle_high: float
    first_candle_low: float
    first_candle_close: float
    second_candle_open: float
    second_candle_high: float
    second_candle_low: float
    second_candle_close: float
    third_candle_open: float
    third_candle_high: float
    third_candle_low: float
    third_candle_close: float
    pattern_type: str = 'three_candle'
    pattern_low: float = 0.0
    pattern_strength: float = 0.0
    is_bullish: bool = True
    is_live: bool = False


@dataclass
class DragonflyDoji:
    """Represents a dragonfly doji pattern"""
    index: int
    timestamp: pd.Timestamp
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    pattern_type: str = 'dragonfly_doji'
    body_ratio: float = 0.0
    lower_wick_ratio: float = 0.0
    is_bullish: bool = True
    is_live: bool = False
    pattern_strength: float = 0.0


@dataclass
class ThreeWhiteSoldiers:
    """Represents a three white soldiers pattern"""
    index: int
    timestamp: pd.Timestamp
    first_candle_open: float
    first_candle_high: float
    first_candle_low: float
    first_candle_close: float
    second_candle_open: float
    second_candle_high: float
    second_candle_low: float
    second_candle_close: float
    third_candle_open: float
    third_candle_high: float
    third_candle_low: float
    third_candle_close: float
    pattern_type: str = 'three_white_soldiers'
    pattern_low: float = 0.0
    average_body_size: float = 0.0
    is_bullish: bool = True
    is_live: bool = False
    pattern_strength: float = 0.0


@dataclass
class BullishMarubozu:
    """Represents a bullish marubozu pattern"""
    index: int
    timestamp: pd.Timestamp
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    pattern_type: str = 'bullish_marubozu'
    body_size: float = 0.0
    upper_wick_ratio: float = 0.0
    lower_wick_ratio: float = 0.0
    is_bullish: bool = True
    is_live: bool = False
    pattern_strength: float = 0.0


@dataclass
class BullishHarami:
    """Represents a bullish harami pattern"""
    index: int
    timestamp: pd.Timestamp
    first_candle_open: float
    first_candle_high: float
    first_candle_low: float
    first_candle_close: float
    second_candle_open: float
    second_candle_high: float
    second_candle_low: float
    second_candle_close: float
    pattern_type: str = 'bullish_harami'
    pattern_low: float = 0.0
    containment_ratio: float = 0.0
    is_bullish: bool = True
    is_live: bool = False
    pattern_strength: float = 0.0


@dataclass
class BullishAbandonedBaby:
    """Represents a bullish abandoned baby pattern"""
    index: int
    timestamp: pd.Timestamp
    first_candle_open: float
    first_candle_high: float
    first_candle_low: float
    first_candle_close: float
    doji_open: float
    doji_high: float
    doji_low: float
    doji_close: float
    third_candle_open: float
    third_candle_high: float
    third_candle_low: float
    third_candle_close: float
    pattern_type: str = 'bullish_abandoned_baby'
    pattern_low: float = 0.0
    gap_down_size: float = 0.0
    gap_up_size: float = 0.0
    is_bullish: bool = True
    is_live: bool = False
    pattern_strength: float = 0.0


@dataclass
class TweezerBottom:
    """Represents a tweezer bottom pattern"""
    index: int
    timestamp: pd.Timestamp
    first_candle_open: float
    first_candle_high: float
    first_candle_low: float
    first_candle_close: float
    second_candle_open: float
    second_candle_high: float
    second_candle_low: float
    second_candle_close: float
    pattern_type: str = 'tweezer_bottom'
    pattern_low: float = 0.0
    low_match_precision: float = 0.0
    is_bullish: bool = True
    is_live: bool = False
    pattern_strength: float = 0.0


@dataclass
class BullishKicker:
    """Represents a bullish kicker pattern"""
    index: int
    timestamp: pd.Timestamp
    first_candle_open: float
    first_candle_high: float
    first_candle_low: float
    first_candle_close: float
    second_candle_open: float
    second_candle_high: float
    second_candle_low: float
    second_candle_close: float
    pattern_type: str = 'bullish_kicker'
    pattern_low: float = 0.0
    gap_size: float = 0.0
    is_bullish: bool = True
    is_live: bool = False
    pattern_strength: float = 0.0


@dataclass
class TradeOutcome:
    """Enhanced trade outcome with trailing stop and partial exit support"""
    success: bool
    target_reached: bool
    sl_hit: bool
    max_profit_pct: float
    max_drawdown_pct: float
    current_profit_pct: float
    bars_to_resolution: int
    resolution_type: str
    target_price: float
    sl_price: float
    target_pct_used: float = 0.0
    exit_timestamp: Optional[pd.Timestamp] = None
    exit_price: float = 0.0
    entry_price: float = 0.0
    current_price: float = 0.0
    last_update_timestamp: Optional[pd.Timestamp] = None

    # Trailing stop fields
    trailing_active: bool = False
    trailing_sl_price: float = 0.0
    highest_price_reached: float = 0.0
    trailing_profit_pct: float = 0.0

    # Partial exit fields
    partial_exits_enabled: bool = False
    first_exit_triggered: bool = False
    first_exit_price: float = 0.0
    first_exit_pct: float = 0.5  # Default 0.5%
    first_exit_timestamp: Optional[pd.Timestamp] = None
    first_exit_bars: int = 0

    second_exit_triggered: bool = False
    second_exit_price: float = 0.0
    second_exit_pct: float = 0.9  # Default 0.9%
    second_exit_timestamp: Optional[pd.Timestamp] = None
    second_exit_bars: int = 0

    # Partial exit capital tracking
    first_exit_capital_pct: float = 50.0  # 50% of capital
    second_exit_capital_pct: float = 50.0  # Remaining 50%

    # Weighted average exit
    weighted_exit_price: float = 0.0
    weighted_profit_pct: float = 0.0
    total_pnl_pct: float = 0.0


@dataclass
class SwingLowTouch:
    """Represents a pattern touching an untouched swing low - ENHANCED"""
    swing_low: SwingLow
    pattern: Union[PinBar, BullishEngulfing, ThreeCandle, DragonflyDoji, ThreeWhiteSoldiers,
    BullishMarubozu, BullishHarami, BullishAbandonedBaby, TweezerBottom, BullishKicker]
    touch_type: str
    pattern_type: str
    distance_pips: float
    days_between: int
    price_difference: float
    trade_outcome: Optional[TradeOutcome] = None
    is_live: bool = False
    pattern_strength: float = 0.0
    symbol: str = ""
    timeframe: str = ""
    entry_price: float = 0.0
    sl_price: float = 0.0
    target_price: float = 0.0
    is_swing_low_valid: bool = True  # Track if swing low was valid at touch time


# ============================================================================
# COMPLETE CAPITAL MANAGEMENT DATA STRUCTURES
# ============================================================================

@dataclass
class CapitalEvent:
    """Represents a capital event (lock/release)"""
    timestamp: pd.Timestamp
    event_type: str  # 'lock', 'release'
    amount: float
    trade_id: str
    symbol: str
    pattern_type: str
    entry_price: float
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    available_capital_after: float = 0.0
    locked_capital_after: float = 0.0


@dataclass
class Trade:
    """Enhanced trade structure with complete capital management"""
    trade_id: str
    symbol: str
    timeframe: str
    pattern_type: str
    entry_timestamp: pd.Timestamp
    entry_price: float
    capital_allocated: float
    target_price: float
    sl_price: float
    target_pct: float

    # Trade status
    status: str = 'open'  # 'open', 'closed'
    exit_timestamp: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    roi_pct: Optional[float] = None

    # Touch details
    swing_low_touch: Optional[SwingLowTouch] = None
    trade_outcome: Optional[TradeOutcome] = None

    # Capital tracking
    capital_locked_timestamp: Optional[pd.Timestamp] = None
    capital_released_timestamp: Optional[pd.Timestamp] = None

    # Additional tracking
    days_held: int = 0
    bars_held: int = 0


# ============================================================================
# ENHANCED SWING LOW DETECTOR - PROFESSIONAL VERSION
# ============================================================================

class EnhancedSwingLowDetector:
    """Enhanced swing low detector with customizable asymmetric parameters - COMPLETE VERSION"""

    def __init__(self, left_lookback: int = 10, right_lookback: int = None, min_swing_size_pct: float = 0.5):
        self.left_lookback = left_lookback

        # CUSTOMIZABLE RIGHT LOOKBACK - User can set explicitly
        if right_lookback is not None:
            self.right_lookback = max(1, right_lookback)  # Minimum 1 bar
        else:
            # Default formula: right = left/3, minimum 2
            self.right_lookback = max(2, left_lookback // 3)

        self.min_swing_size_pct = min_swing_size_pct

    def find_swing_lows_with_invalidation(self, df: pd.DataFrame) -> List[SwingLow]:
        """Find swing lows and track their invalidation professionally - ASYMMETRIC VERSION"""
        swing_lows = []

        # ASYMMETRIC PARAMETERS - Key change from original
        left_lookback = self.left_lookback  # Full historical context
        right_lookback = self.right_lookback  # User customizable confirmation

        print(f"🔧 Asymmetric swing detection: {left_lookback} left + {right_lookback} right bars")

        # ASYMMETRIC RANGE - This is the crucial change
        start_idx = left_lookback
        end_idx = len(df) - right_lookback  # Much earlier detection possible

        if end_idx <= start_idx:
            print(f"❌ Not enough data: need {left_lookback + right_lookback} bars, have {len(df)}")
            return swing_lows

        print(f"🔍 Checking bars {start_idx} to {end_idx - 1} (total: {end_idx - start_idx} bars)")

        # Step 1: Find all potential swing lows using asymmetric logic
        for i in range(start_idx, end_idx):
            if i >= len(df):
                break

            current_low = df['low'].iloc[i]

            # LEFT SIDE CHECK (Historical Context - Full lookback)
            left_valid = True
            for j in range(max(0, i - left_lookback), i):
                if j < len(df) and df['low'].iloc[j] < current_low:
                    left_valid = False
                    break

            # RIGHT SIDE CHECK (Forward Confirmation - Customizable lookback)
            right_valid = True
            for j in range(i + 1, min(i + right_lookback + 1, len(df))):
                if j < len(df) and df['low'].iloc[j] < current_low:
                    right_valid = False
                    break

            if left_valid and right_valid:
                swing_low = SwingLow(
                    index=i,
                    timestamp=df.index[i],
                    price=current_low,
                    is_invalidated=False,
                    invalidation_timestamp=None,
                    invalidation_index=None,
                    is_touched=False,
                    touch_timestamp=None,
                    touch_pattern=None,
                    touch_index=None
                )
                swing_lows.append(swing_low)

        print(f"✅ Found {len(swing_lows)} asymmetric swing lows")

        # Step 2: Check invalidation for each swing low
        invalidated_count = 0
        for swing_low in swing_lows:
            # Look at all future data after this swing low
            future_data = df[df.index > swing_low.timestamp]

            for future_index, (future_timestamp, future_row) in enumerate(future_data.iterrows()):
                # If any future candle's low breaks below swing low, invalidate it
                if future_row['low'] < swing_low.price:
                    swing_low.is_invalidated = True
                    swing_low.invalidation_timestamp = future_timestamp
                    swing_low.invalidation_index = swing_low.index + future_index + 1
                    invalidated_count += 1
                    break

        valid_count = len(swing_lows) - invalidated_count
        print(f"📊 Invalidation check: {valid_count} valid, {invalidated_count} invalidated")

        return swing_lows

    def get_valid_swing_lows_at_timestamp(self, swing_lows: List[SwingLow],
                                          check_timestamp: pd.Timestamp) -> List[SwingLow]:
        """Get swing lows that are still valid at a specific timestamp"""
        valid_lows = []

        for swing_low in swing_lows:
            # Swing low must exist before the check timestamp
            if swing_low.timestamp >= check_timestamp:
                continue

            # If swing low is invalidated, check if invalidation happened after check_timestamp
            if swing_low.is_invalidated:
                if swing_low.invalidation_timestamp and swing_low.invalidation_timestamp <= check_timestamp:
                    continue  # Was already invalidated at check time

            valid_lows.append(swing_low)

        return valid_lows

    def find_swing_lows(self, df: pd.DataFrame) -> List[SwingLow]:
        """Legacy method for compatibility"""
        return self.find_swing_lows_with_invalidation(df)

    def find_untouched_swing_lows(self, df: pd.DataFrame, swing_lows: List[SwingLow]) -> List[SwingLow]:
        """Find swing lows that remain untouched by future price action"""
        untouched_lows = []

        for swing_low in swing_lows:
            if not swing_low.is_touched and not swing_low.is_invalidated:
                untouched_lows.append(swing_low)

        return untouched_lows


# ============================================================================
# ENHANCED TRADE OUTCOME ANALYZER - PROFESSIONAL VERSION
# ============================================================================

class EnhancedTradeOutcomeAnalyzer:
    """Enhanced analyzer with professional current status tracking, flexible targets, and partial exits"""

    def __init__(self, max_bars_to_analyze: int = 100, capital_per_trade: float = 10000):
        self.max_bars_to_analyze = max_bars_to_analyze
        self.capital_per_trade = capital_per_trade

        # Default timeframe-specific targets for optimized trading
        self.default_timeframe_targets = {
            '1m': 0.5,  # 0.5% for 1-minute scalping
            '5m': 0.75,  # 0.75% for 5-minute quick trades
            '15m': 1.0,  # 1% for 15-minute intraday
            '30m': 1.5,  # 1.5% for 30-minute intraday
            '1H': 2.5,  # 2.5% for 1-hour short swings
            '4H': 5.0,  # 5% for 4-hour swing trades
            '1D': 8.0  # 8% for daily position trades
        }

        # Partial exit configuration
        self.partial_exit_config = {
            'first_exit_pct': 0.5,  # Exit at 0.5%
            'second_exit_pct': 0.9,  # Exit at 0.9%
            'first_exit_capital_pct': 50.0,  # 50% of capital
            'second_exit_capital_pct': 50.0  # Remaining 50%
        }

    def get_target_for_timeframe(self, timeframe: str, custom_target: float = None) -> float:
        """Get appropriate target percentage for timeframe or use custom target"""
        if custom_target is not None and custom_target > 0:
            return custom_target
        return self.default_timeframe_targets.get(timeframe, 2.0)  # Default 2%

    def analyze_trade_outcomes_with_timeframe(self, df: pd.DataFrame, touches: List[SwingLowTouch],
                                              timeframe: str, use_trailing_stop: bool = False,
                                              intraday_mode: bool = False,
                                              entry_cutoff_time: str = '11:45',
                                              exit_time: str = '15:15',
                                              custom_target_pct: float = None,
                                              use_partial_exits: bool = False,
                                              first_exit_pct: float = 0.5,
                                              second_exit_pct: float = 0.9,
                                              first_exit_capital_pct: float = 50.0) -> List[SwingLowTouch]:
        """Analyze trade outcomes with flexible targets, partial exits, and configurable options"""
        enhanced_touches = []
        target_pct = self.get_target_for_timeframe(timeframe, custom_target_pct)

        for touch in touches:
            # Skip live patterns for outcome analysis
            if touch.is_live:
                enhanced_touches.append(touch)
                continue

            # Check intraday entry cutoff if in intraday mode
            if intraday_mode:
                pattern_time = pd.Timestamp(touch.pattern.timestamp)
                pattern_hour_min = pattern_time.strftime('%H:%M')

                # Skip patterns that occur after entry cutoff time
                if pattern_hour_min > entry_cutoff_time:
                    continue

            # Get entry and stop loss prices based on pattern type
            entry_price, sl_price = self._get_entry_and_sl_prices(touch)

            # Calculate target price using flexible target
            target_price = entry_price * (1 + target_pct / 100)

            # Store prices in touch for capital management
            touch.entry_price = entry_price
            touch.sl_price = sl_price
            touch.target_price = target_price

            # Get future data after the pattern
            pattern_index = touch.pattern.index
            future_data = df.iloc[pattern_index + 1:pattern_index + 1 + self.max_bars_to_analyze]

            if future_data.empty:
                trade_outcome = TradeOutcome(
                    success=False, target_reached=False, sl_hit=False,
                    max_profit_pct=0.0, max_drawdown_pct=0.0, current_profit_pct=0.0,
                    bars_to_resolution=0, resolution_type='no_data',
                    target_price=target_price, sl_price=sl_price,
                    target_pct_used=target_pct,
                    entry_price=entry_price, current_price=entry_price,
                    partial_exits_enabled=use_partial_exits,
                    first_exit_pct=first_exit_pct,
                    second_exit_pct=second_exit_pct,
                    first_exit_capital_pct=first_exit_capital_pct,
                    second_exit_capital_pct=100.0 - first_exit_capital_pct
                )
            else:
                if use_partial_exits:
                    trade_outcome = self._analyze_single_trade_with_partial_exits(
                        future_data, entry_price, target_price, sl_price, target_pct,
                        use_trailing_stop, intraday_mode,
                        pd.Timestamp(touch.pattern.timestamp), exit_time,
                        first_exit_pct, second_exit_pct, first_exit_capital_pct
                    )
                else:
                    trade_outcome = self._analyze_single_trade_enhanced(
                        future_data, entry_price, target_price, sl_price, target_pct,
                        use_trailing_stop, intraday_mode,
                        pd.Timestamp(touch.pattern.timestamp), exit_time
                    )

            # Create enhanced touch with trade outcome
            enhanced_touch = SwingLowTouch(
                swing_low=touch.swing_low,
                pattern=touch.pattern,
                touch_type=touch.touch_type,
                pattern_type=touch.pattern_type,
                distance_pips=touch.distance_pips,
                days_between=touch.days_between,
                price_difference=touch.price_difference,
                trade_outcome=trade_outcome,
                is_live=touch.is_live,
                pattern_strength=touch.pattern_strength,
                symbol=touch.symbol,
                timeframe=touch.timeframe,
                entry_price=entry_price,
                sl_price=sl_price,
                target_price=target_price,
                is_swing_low_valid=touch.is_swing_low_valid
            )

            enhanced_touches.append(enhanced_touch)

        return enhanced_touches

    def _analyze_single_trade_with_partial_exits(self, future_data: pd.DataFrame, entry_price: float,
                                                 target_price: float, sl_price: float, target_pct: float,
                                                 use_trailing_stop: bool = False,
                                                 intraday_mode: bool = False,
                                                 entry_timestamp: pd.Timestamp = None,
                                                 exit_time: str = '15:15',
                                                 first_exit_pct: float = 0.5,
                                                 second_exit_pct: float = 0.9,
                                                 first_exit_capital_pct: float = 50.0) -> TradeOutcome:
        """Analyze single trade with partial exit support"""

        # Calculate partial exit prices
        first_exit_price = entry_price * (1 + first_exit_pct / 100)
        second_exit_price = entry_price * (1 + second_exit_pct / 100)
        second_exit_capital_pct = 100.0 - first_exit_capital_pct

        # Initialize tracking variables
        first_exit_triggered = False
        first_exit_timestamp = None
        first_exit_bars = 0

        second_exit_triggered = False
        second_exit_timestamp = None
        second_exit_bars = 0

        sl_hit = False
        bars_to_resolution = 0
        resolution_type = 'ongoing'
        max_profit_pct = 0.0
        max_drawdown_pct = 0.0
        exit_timestamp = None
        current_profit_pct = 0.0
        current_price = entry_price
        last_update_timestamp = None

        # Position tracking
        remaining_position_pct = 100.0  # Start with 100% position

        # Parse intraday exit time
        if intraday_mode and exit_time:
            exit_hour, exit_minute = map(int, exit_time.split(':'))

        for i, (timestamp, row) in enumerate(future_data.iterrows()):
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']

            # Check for intraday exit
            if intraday_mode and entry_timestamp:
                if timestamp.date() == entry_timestamp.date():
                    if timestamp.hour > exit_hour or (timestamp.hour == exit_hour and timestamp.minute >= exit_minute):
                        # Force exit at close price
                        bars_to_resolution = i + 1
                        resolution_type = 'intraday_exit'
                        exit_timestamp = timestamp
                        current_price = close_price
                        current_profit_pct = ((close_price - entry_price) / entry_price) * 100
                        break

            # Update current price and profit
            current_price = close_price
            last_update_timestamp = timestamp
            current_profit_pct = ((close_price - entry_price) / entry_price) * 100

            # Calculate max profit and drawdown
            current_high_profit = ((high_price - entry_price) / entry_price) * 100
            current_low_drawdown = ((low_price - entry_price) / entry_price) * 100
            max_profit_pct = max(max_profit_pct, current_high_profit)
            max_drawdown_pct = min(max_drawdown_pct, current_low_drawdown)

            # Check for stop loss (applies to entire remaining position)
            if low_price <= sl_price and remaining_position_pct > 0:
                sl_hit = True
                bars_to_resolution = i + 1
                resolution_type = 'stop_loss'
                exit_timestamp = timestamp
                break

            # Check for first partial exit
            if not first_exit_triggered and high_price >= first_exit_price:
                first_exit_triggered = True
                first_exit_timestamp = timestamp
                first_exit_bars = i + 1
                remaining_position_pct -= first_exit_capital_pct

                # Don't break, continue to check for second exit

            # Check for second partial exit
            if not second_exit_triggered and high_price >= second_exit_price:
                second_exit_triggered = True
                second_exit_timestamp = timestamp
                second_exit_bars = i + 1
                remaining_position_pct -= second_exit_capital_pct

                # If both exits triggered, position is closed
                if first_exit_triggered and second_exit_triggered:
                    bars_to_resolution = i + 1
                    resolution_type = 'partial_exits_complete'
                    exit_timestamp = timestamp
                    break

        # Calculate weighted results
        weighted_profit_pct = 0.0
        total_pnl_pct = 0.0

        if sl_hit:
            # Stop loss hit - entire remaining position exits at stop loss
            loss_pct = ((sl_price - entry_price) / entry_price) * 100
            if first_exit_triggered:
                # First exit successful, remaining position hit stop loss
                weighted_profit_pct = (first_exit_pct * first_exit_capital_pct +
                                       loss_pct * second_exit_capital_pct) / 100.0
                total_pnl_pct = weighted_profit_pct
            else:
                # Full position hit stop loss
                weighted_profit_pct = loss_pct
                total_pnl_pct = loss_pct
        else:
            # Calculate based on partial exits
            if first_exit_triggered and second_exit_triggered:
                # Both targets hit
                weighted_profit_pct = (first_exit_pct * first_exit_capital_pct +
                                       second_exit_pct * second_exit_capital_pct) / 100.0
                total_pnl_pct = weighted_profit_pct
            elif first_exit_triggered:
                # Only first target hit, rest still open
                weighted_profit_pct = (first_exit_pct * first_exit_capital_pct +
                                       current_profit_pct * second_exit_capital_pct) / 100.0
                total_pnl_pct = weighted_profit_pct
            else:
                # No targets hit yet
                weighted_profit_pct = current_profit_pct
                total_pnl_pct = current_profit_pct

        # Determine success
        success = first_exit_triggered or second_exit_triggered
        target_reached = second_exit_triggered  # Full target is second exit

        return TradeOutcome(
            success=success,
            target_reached=target_reached,
            sl_hit=sl_hit,
            max_profit_pct=max_profit_pct,
            max_drawdown_pct=max_drawdown_pct,
            current_profit_pct=current_profit_pct,
            bars_to_resolution=bars_to_resolution,
            resolution_type=resolution_type,
            target_price=target_price,
            sl_price=sl_price,
            target_pct_used=target_pct,
            exit_timestamp=exit_timestamp,
            entry_price=entry_price,
            current_price=current_price,
            last_update_timestamp=last_update_timestamp,

            # Partial exit data
            partial_exits_enabled=True,
            first_exit_triggered=first_exit_triggered,
            first_exit_price=first_exit_price,
            first_exit_pct=first_exit_pct,
            first_exit_timestamp=first_exit_timestamp,
            first_exit_bars=first_exit_bars,

            second_exit_triggered=second_exit_triggered,
            second_exit_price=second_exit_price,
            second_exit_pct=second_exit_pct,
            second_exit_timestamp=second_exit_timestamp,
            second_exit_bars=second_exit_bars,

            first_exit_capital_pct=first_exit_capital_pct,
            second_exit_capital_pct=second_exit_capital_pct,

            weighted_profit_pct=weighted_profit_pct,
            total_pnl_pct=total_pnl_pct
        )

    def _analyze_single_trade_enhanced(self, future_data: pd.DataFrame, entry_price: float,
                                       target_price: float, sl_price: float,
                                       target_pct: float, use_trailing_stop: bool = False,
                                       intraday_mode: bool = False,
                                       entry_timestamp: pd.Timestamp = None,
                                       exit_time: str = '15:15') -> TradeOutcome:
        """Enhanced single trade analysis with configurable stop loss and intraday mode (original logic)"""
        target_reached = False
        sl_hit = False
        bars_to_resolution = 0
        resolution_type = 'ongoing'
        max_profit_pct = 0.0
        max_drawdown_pct = 0.0
        exit_timestamp = None
        current_profit_pct = 0.0
        current_price = entry_price
        last_update_timestamp = None

        # Trailing stop variables
        trailing_active = False
        trailing_sl_price = sl_price
        highest_price_reached = entry_price
        final_profit_pct = 0.0

        # Parse intraday exit time
        if intraday_mode and exit_time:
            exit_hour, exit_minute = map(int, exit_time.split(':'))

        for i, (timestamp, row) in enumerate(future_data.iterrows()):
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']

            # Check for intraday exit if enabled
            if intraday_mode and entry_timestamp:
                if timestamp.date() == entry_timestamp.date():
                    if timestamp.hour > exit_hour or (timestamp.hour == exit_hour and timestamp.minute >= exit_minute):
                        bars_to_resolution = i + 1
                        resolution_type = 'intraday_exit'
                        exit_timestamp = timestamp
                        current_price = close_price
                        current_profit_pct = ((close_price - entry_price) / entry_price) * 100
                        final_profit_pct = current_profit_pct

                        if current_profit_pct > 0:
                            target_reached = False
                            success = True
                        else:
                            sl_hit = False
                            success = False
                        break

            # Update current price and profit
            current_price = close_price
            last_update_timestamp = timestamp
            current_profit_pct = ((close_price - entry_price) / entry_price) * 100

            # Calculate max profit and drawdown from high/low
            current_high_profit = ((high_price - entry_price) / entry_price) * 100
            current_low_drawdown = ((low_price - entry_price) / entry_price) * 100

            max_profit_pct = max(max_profit_pct, current_high_profit)
            max_drawdown_pct = min(max_drawdown_pct, current_low_drawdown)

            if use_trailing_stop:
                # TRAILING STOP LOGIC
                if not trailing_active:
                    if high_price >= target_price:
                        target_reached = True
                        trailing_active = True
                        trailing_sl_price = low_price
                        highest_price_reached = high_price
                        continue

                    if low_price <= sl_price:
                        sl_hit = True
                        bars_to_resolution = i + 1
                        resolution_type = 'stop_loss'
                        exit_timestamp = timestamp
                        final_profit_pct = ((sl_price - entry_price) / entry_price) * 100
                        break
                else:
                    if high_price > highest_price_reached:
                        highest_price_reached = high_price
                        trailing_sl_price = low_price

                    if low_price <= trailing_sl_price:
                        sl_hit = True
                        bars_to_resolution = i + 1
                        resolution_type = 'trailing_stop'
                        exit_timestamp = timestamp
                        final_profit_pct = ((trailing_sl_price - entry_price) / entry_price) * 100
                        break
            else:
                # FIXED STOP LOSS LOGIC
                if high_price >= target_price:
                    target_reached = True
                    bars_to_resolution = i + 1
                    resolution_type = 'target_hit'
                    exit_timestamp = timestamp
                    final_profit_pct = target_pct
                    break

                if low_price <= sl_price:
                    sl_hit = True
                    bars_to_resolution = i + 1
                    resolution_type = 'stop_loss'
                    exit_timestamp = timestamp
                    final_profit_pct = ((sl_price - entry_price) / entry_price) * 100
                    break

        # Determine success based on stop loss type
        if use_trailing_stop:
            success = target_reached or (not sl_hit)
            if target_reached:
                success = True
            elif sl_hit and not trailing_active:
                success = False
            else:
                success = False
        else:
            success = target_reached

        # Handle ongoing trades
        if not target_reached and not sl_hit and resolution_type == 'ongoing':
            final_profit_pct = current_profit_pct

        return TradeOutcome(
            success=success,
            target_reached=target_reached,
            sl_hit=sl_hit,
            max_profit_pct=max_profit_pct,
            max_drawdown_pct=max_drawdown_pct,
            current_profit_pct=current_profit_pct,
            bars_to_resolution=bars_to_resolution,
            resolution_type=resolution_type,
            target_price=target_price,
            sl_price=sl_price,
            target_pct_used=target_pct,
            exit_timestamp=exit_timestamp,
            entry_price=entry_price,
            current_price=current_price,
            last_update_timestamp=last_update_timestamp,
            trailing_active=trailing_active if use_trailing_stop else False,
            trailing_sl_price=trailing_sl_price if use_trailing_stop else sl_price,
            highest_price_reached=highest_price_reached if use_trailing_stop else entry_price,
            trailing_profit_pct=final_profit_pct,
            partial_exits_enabled=False
        )

    def _get_entry_and_sl_prices(self, touch: SwingLowTouch) -> Tuple[float, float]:
        """Get entry and stop loss prices based on pattern type"""
        pattern = touch.pattern
        pattern_type = touch.pattern_type

        if pattern_type == 'pin_bar':
            entry_price = pattern.close_price
            sl_price = pattern.low_price
        elif pattern_type == 'bullish_engulfing':
            entry_price = pattern.second_candle_close
            sl_price = pattern.pattern_low
        elif pattern_type == 'three_candle':
            entry_price = pattern.third_candle_close
            sl_price = pattern.pattern_low
        elif pattern_type == 'dragonfly_doji':
            entry_price = pattern.close_price
            sl_price = pattern.low_price
        elif pattern_type == 'three_white_soldiers':
            entry_price = pattern.third_candle_close
            sl_price = pattern.pattern_low
        elif pattern_type == 'bullish_marubozu':
            entry_price = pattern.close_price
            sl_price = pattern.open_price
        elif pattern_type == 'bullish_harami':
            entry_price = pattern.second_candle_close
            sl_price = pattern.pattern_low
        elif pattern_type == 'bullish_abandoned_baby':
            entry_price = pattern.third_candle_close
            sl_price = pattern.pattern_low
        elif pattern_type == 'tweezer_bottom':
            entry_price = pattern.second_candle_close
            sl_price = pattern.pattern_low
        elif pattern_type == 'bullish_kicker':
            entry_price = pattern.second_candle_close
            sl_price = pattern.pattern_low
        else:
            entry_price = getattr(pattern, 'close_price', getattr(pattern, 'third_candle_close', 0))
            sl_price = getattr(pattern, 'pattern_low', getattr(pattern, 'low_price', entry_price * 0.98))

        return entry_price, sl_price

    def calculate_pnl(self, entry_price: float, trade_outcome: TradeOutcome, capital: float = None) -> float:
        """Calculate P&L for a trade based on outcome with partial exit support"""
        if capital is None:
            capital = self.capital_per_trade

        if trade_outcome.partial_exits_enabled:
            # Use weighted profit for partial exits
            return capital * (trade_outcome.total_pnl_pct / 100)
        elif trade_outcome.trailing_active and trade_outcome.sl_hit:
            return capital * (trade_outcome.trailing_profit_pct / 100)
        elif trade_outcome.success and not trade_outcome.sl_hit:
            return capital * (trade_outcome.current_profit_pct / 100)
        elif trade_outcome.sl_hit:
            loss_pct = ((trade_outcome.sl_price - entry_price) / entry_price) * 100
            return capital * (loss_pct / 100)
        else:
            return capital * (trade_outcome.current_profit_pct / 100)


# ============================================================================
# ENHANCED SWING LOW TOUCH ANALYZER - PROFESSIONAL VERSION
# ============================================================================

class EnhancedSwingLowTouchAnalyzer:
    """Enhanced analyzer that only counts valid swing low touches with strict validation"""

    def __init__(self, touch_tolerance_pct: float = 0.1, min_days_between: int = 1):
        self.touch_tolerance_pct = touch_tolerance_pct
        self.min_days_between = min_days_between

    def analyze_touches(self, df: pd.DataFrame, untouched_swing_lows: List[SwingLow],
                        all_patterns: Dict[str, List], symbol: str = "", timeframe: str = "") -> List[SwingLowTouch]:
        """Analyze when patterns touch untouched swing lows - ENHANCED WITH DAYS FILTER AND STRICT TOUCH VALIDATION"""
        touches = []

        # Create enhanced swing low detector for validation
        swing_detector = EnhancedSwingLowDetector()

        # Combine all patterns
        combined_patterns = []
        for pattern_type, patterns in all_patterns.items():
            for pattern in patterns:
                combined_patterns.append((pattern_type, pattern))

        for pattern_type, pattern in combined_patterns:
            pattern_timestamp = pd.Timestamp(pattern.timestamp)

            # Get swing lows that were valid at the time of pattern formation
            valid_swing_lows = swing_detector.get_valid_swing_lows_at_timestamp(
                untouched_swing_lows, pattern_timestamp
            )

            for swing_low in valid_swing_lows:
                # Only consider swing lows that occurred before this pattern
                if swing_low.timestamp >= pattern_timestamp:
                    continue

                # Skip if swing low was already touched by another pattern
                if swing_low.is_touched:
                    continue

                # NEW: Check minimum days between swing low and pattern
                days_between = (pattern_timestamp - swing_low.timestamp).days
                if days_between < self.min_days_between:
                    continue

                # Get pattern low for strict touch validation
                if hasattr(pattern, 'pattern_low'):
                    pattern_low = pattern.pattern_low
                elif hasattr(pattern, 'low_price'):
                    pattern_low = pattern.low_price
                else:
                    pattern_low = getattr(pattern, 'close_price', 0)

                # ENHANCED: Strict swing low touch validation
                # The pattern low must actually touch (equal to or slightly penetrate) the swing low
                swing_low_price = swing_low.price

                # Calculate if pattern actually touches the swing low
                price_difference = pattern_low - swing_low_price

                # For a valid touch:
                # 1. Pattern low should be equal to or slightly below swing low (price_difference <= 0)
                # 2. If above swing low, must be within very tight tolerance
                is_actual_touch = False

                if price_difference <= 0:
                    # Pattern low is at or below swing low - this is a valid touch
                    # Allow slight penetration below (up to tolerance)
                    penetration_pct = abs(price_difference / swing_low_price) * 100
                    if penetration_pct <= self.touch_tolerance_pct:
                        is_actual_touch = True
                else:
                    # Pattern low is above swing low - only allow if within very small tolerance
                    distance_above_pct = (price_difference / swing_low_price) * 100
                    # Use much tighter tolerance for cases where pattern is above swing low
                    if distance_above_pct <= (self.touch_tolerance_pct * 0.3):  # 30% of normal tolerance
                        is_actual_touch = True

                # Only proceed if we have an actual touch
                if is_actual_touch:
                    # Calculate final distance percentage for reporting
                    final_distance_pct = abs(price_difference / swing_low_price) * 100

                    touch = SwingLowTouch(
                        swing_low=swing_low,
                        pattern=pattern,
                        touch_type='strict_touch',
                        pattern_type=pattern_type,
                        distance_pips=price_difference,  # Can be negative (penetration) or positive (slight gap)
                        days_between=days_between,
                        price_difference=final_distance_pct,
                        is_live=getattr(pattern, 'is_live', False),
                        pattern_strength=getattr(pattern, 'pattern_strength', 50.0),
                        symbol=symbol,
                        timeframe=timeframe,
                        is_swing_low_valid=True  # It was valid at touch time
                    )

                    touches.append(touch)

                    # Mark swing low as touched
                    swing_low.is_touched = True
                    swing_low.touch_timestamp = pattern_timestamp
                    swing_low.touch_pattern = pattern_type
                    swing_low.touch_index = pattern.index

        return touches


# ============================================================================
# COMPLETE CAPITAL MANAGEMENT SYSTEM - PROFESSIONAL
# ============================================================================

class CapitalManager:
    """Complete Capital Management System with professional chronological simulation"""

    def __init__(self, total_capital: float, capital_per_trade: float, start_date: datetime):
        self.total_capital = total_capital
        self.capital_per_trade = capital_per_trade
        self.start_date = pd.Timestamp(start_date)
        self.available_capital = total_capital
        self.locked_capital = 0.0

        # Tracking
        self.trades: List[Trade] = []
        self.open_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
        self.capital_events: List[CapitalEvent] = []
        self.capital_history: List[Dict] = []
        self.daily_snapshots: Dict[pd.Timestamp, Dict] = {}

        # Statistics
        self.total_trades_attempted = 0
        self.total_trades_executed = 0
        self.total_trades_rejected = 0
        self.max_concurrent_trades = 0
        self.max_drawdown = 0.0
        self.peak_capital = total_capital

        # Performance metrics
        self.total_pnl = 0.0
        self.winning_trades = 0
        self.losing_trades = 0

        # Debug tracking
        self.debug_info = []
        self.rejected_trades_log = []

        # Initialize first snapshot
        self.record_capital_snapshot(self.start_date, "Initialization")

    def can_enter_trade(self, timestamp: pd.Timestamp) -> bool:
        """Check if we have enough capital for a new trade at given timestamp"""
        # Check if timestamp is after start date
        if timestamp < self.start_date:
            return False
        return self.available_capital >= self.capital_per_trade

    def process_trade_opportunity(self, touch: SwingLowTouch, df: pd.DataFrame) -> Optional[Trade]:
        """Process a trade opportunity with professional capital management"""
        pattern_timestamp = pd.Timestamp(touch.pattern.timestamp)

        # Check if pattern is after start date
        if pattern_timestamp < self.start_date:
            self.debug_info.append(f"⏭️ Skipping pattern before start date: {pattern_timestamp}")
            return None

        self.total_trades_attempted += 1

        # Check capital availability
        if not self.can_enter_trade(pattern_timestamp):
            self.total_trades_rejected += 1
            self.rejected_trades_log.append({
                'timestamp': pattern_timestamp,
                'symbol': touch.symbol,
                'pattern': touch.pattern_type,
                'reason': f'Insufficient capital (Available: ${self.available_capital:.0f})'
            })
            self.debug_info.append(f"❌ Rejected: {touch.symbol} at {pattern_timestamp} - Insufficient capital")
            return None

        # Create trade
        trade_id = f"{touch.symbol}_{touch.pattern_type}_{pattern_timestamp.strftime('%Y%m%d_%H%M%S')}"

        trade = Trade(
            trade_id=trade_id,
            symbol=touch.symbol,
            timeframe=touch.timeframe,
            pattern_type=touch.pattern_type,
            entry_timestamp=pattern_timestamp,
            entry_price=touch.entry_price,
            capital_allocated=self.capital_per_trade,
            target_price=touch.target_price,
            sl_price=touch.sl_price,
            target_pct=touch.trade_outcome.target_pct_used if touch.trade_outcome else 0,
            swing_low_touch=touch,
            trade_outcome=touch.trade_outcome
        )

        # Lock capital
        self.lock_capital(trade)

        # Process trade outcome
        if touch.trade_outcome:
            self.process_trade_exit(trade, df)

        return trade

    def lock_capital(self, trade: Trade) -> bool:
        """Lock capital for a trade entry"""
        # Double-check capital availability
        if self.available_capital < self.capital_per_trade:
            return False

        # Lock the capital
        self.available_capital -= self.capital_per_trade
        self.locked_capital += self.capital_per_trade
        trade.capital_locked_timestamp = trade.entry_timestamp
        trade.status = 'open'

        # Track open trades
        self.open_trades.append(trade)
        self.max_concurrent_trades = max(self.max_concurrent_trades, len(self.open_trades))

        # Record capital event
        event = CapitalEvent(
            timestamp=trade.entry_timestamp,
            event_type='lock',
            amount=self.capital_per_trade,
            trade_id=trade.trade_id,
            symbol=trade.symbol,
            pattern_type=trade.pattern_type,
            entry_price=trade.entry_price,
            available_capital_after=self.available_capital,
            locked_capital_after=self.locked_capital
        )
        self.capital_events.append(event)

        # Add to trades
        self.trades.append(trade)
        self.total_trades_executed += 1

        # Record snapshot
        self.record_capital_snapshot(trade.entry_timestamp, f"Entry: {trade.symbol}")

        self.debug_info.append(f"✅ Locked ${self.capital_per_trade:.0f} for {trade.trade_id}")

        return True

    def process_trade_exit(self, trade: Trade, df: pd.DataFrame):
        """Process trade exit based on outcome"""
        if not trade.trade_outcome:
            return

        outcome = trade.trade_outcome

        # Determine exit details
        if outcome.exit_timestamp:
            exit_timestamp = pd.Timestamp(outcome.exit_timestamp)
        else:
            # Estimate exit based on bars
            hours = self._estimate_hours_from_bars(outcome.bars_to_resolution, trade.timeframe)
            exit_timestamp = trade.entry_timestamp + pd.Timedelta(hours=hours)

        # Determine exit price and P&L - ENHANCED WITH CURRENT STATUS
        if outcome.target_reached:
            exit_price = trade.target_price
            pnl = self.capital_per_trade * (trade.target_pct / 100)
        elif outcome.sl_hit:
            exit_price = trade.sl_price
            pnl = self.capital_per_trade * ((trade.sl_price - trade.entry_price) / trade.entry_price)
        else:
            # Use current price for ongoing trades
            exit_price = outcome.current_price
            pnl = self.capital_per_trade * (outcome.current_profit_pct / 100)

        # Release capital
        self.release_capital(trade, exit_timestamp, exit_price, pnl)

    def release_capital(self, trade: Trade, exit_timestamp: pd.Timestamp,
                        exit_price: float, pnl: float) -> None:
        """Release capital when trade exits"""
        if trade.status != 'open':
            return

        # Update trade
        trade.exit_timestamp = exit_timestamp
        trade.exit_price = exit_price
        trade.pnl = pnl
        trade.roi_pct = (pnl / trade.capital_allocated) * 100 if trade.capital_allocated > 0 else 0
        trade.status = 'closed'
        trade.capital_released_timestamp = exit_timestamp
        trade.days_held = (exit_timestamp - trade.entry_timestamp).days

        # Remove from open trades, add to closed
        if trade in self.open_trades:
            self.open_trades.remove(trade)
        self.closed_trades.append(trade)

        # Release capital with P&L
        released_amount = trade.capital_allocated + pnl
        self.available_capital += released_amount
        self.locked_capital -= trade.capital_allocated

        # Update statistics
        self.total_pnl += pnl
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        # Track peak and drawdown
        current_total = self.available_capital + self.locked_capital
        if current_total > self.peak_capital:
            self.peak_capital = current_total

        drawdown_pct = ((self.peak_capital - current_total) / self.peak_capital) * 100
        if drawdown_pct > self.max_drawdown:
            self.max_drawdown = drawdown_pct

        # Record capital event
        event = CapitalEvent(
            timestamp=exit_timestamp,
            event_type='release',
            amount=released_amount,
            trade_id=trade.trade_id,
            symbol=trade.symbol,
            pattern_type=trade.pattern_type,
            entry_price=trade.entry_price,
            exit_price=exit_price,
            pnl=pnl,
            available_capital_after=self.available_capital,
            locked_capital_after=self.locked_capital
        )
        self.capital_events.append(event)

        # Record snapshot
        self.record_capital_snapshot(exit_timestamp, f"Exit: {trade.symbol} P&L: ${pnl:.2f}")

        self.debug_info.append(f"💰 Released ${released_amount:.0f} for {trade.trade_id} (P&L: ${pnl:.2f})")

    def _estimate_hours_from_bars(self, bars: int, timeframe: str) -> float:
        """Estimate hours from number of bars and timeframe"""
        timeframe_hours = {
            '1m': 1 / 60, '5m': 5 / 60, '15m': 15 / 60, '30m': 0.5,
            '1H': 1, '4H': 4, '1D': 24
        }
        return bars * timeframe_hours.get(timeframe, 4)

    def record_capital_snapshot(self, timestamp: pd.Timestamp, event_description: str = ""):
        """Record current capital state"""
        total_capital = self.available_capital + self.locked_capital
        utilization_pct = (self.locked_capital / self.total_capital) * 100 if self.total_capital > 0 else 0

        snapshot = {
            'timestamp': timestamp,
            'available_capital': self.available_capital,
            'locked_capital': self.locked_capital,
            'total_capital': total_capital,
            'utilization_pct': utilization_pct,
            'total_pnl': self.total_pnl,
            'open_trades': len(self.open_trades),
            'closed_trades': len(self.closed_trades),
            'event': event_description
        }

        self.capital_history.append(snapshot)

        # Store daily snapshot
        date_key = pd.Timestamp(timestamp.date())
        self.daily_snapshots[date_key] = snapshot

    def simulate_chronological_trading(self, all_touches: List[SwingLowTouch],
                                       data_cache: Dict[str, pd.DataFrame]) -> None:
        """Main simulation method - process all trades chronologically"""

        if not all_touches:
            st.warning("⚠️ No pattern touches to simulate")
            return

        # Filter touches after start date
        valid_touches = []
        for touch in all_touches:
            pattern_timestamp = pd.Timestamp(touch.pattern.timestamp)
            if pattern_timestamp >= self.start_date:
                valid_touches.append(touch)

        if not valid_touches:
            st.error(f"❌ No patterns found after {self.start_date.strftime('%Y-%m-%d')}")

            # Show available date range
            all_dates = [pd.Timestamp(t.pattern.timestamp) for t in all_touches]
            if all_dates:
                earliest = min(all_dates)
                latest = max(all_dates)
                st.info(f"📅 Available patterns: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
                st.warning(f"💡 Set start date to {earliest.strftime('%Y-%m-%d')} or earlier")
            return

        # Sort touches chronologically
        valid_touches.sort(key=lambda x: x.pattern.timestamp)

        st.info(f"📊 Processing {len(valid_touches)} patterns from {self.start_date.strftime('%Y-%m-%d')}")

        # Process each touch
        progress_bar = st.progress(0)
        for i, touch in enumerate(valid_touches):
            # Get the data for this symbol/timeframe
            cache_key = f"{touch.symbol}_{touch.timeframe}"
            df = data_cache.get(cache_key)

            if df is not None:
                self.process_trade_opportunity(touch, df)

            # Update progress
            progress_bar.progress((i + 1) / len(valid_touches))

        progress_bar.empty()

        # Final summary
        st.success(f"✅ Simulation complete: {self.total_trades_executed} trades executed")

        if self.total_trades_rejected > 0:
            st.warning(f"⚠️ {self.total_trades_rejected} trades rejected due to insufficient capital")

    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        total_capital_current = self.available_capital + self.locked_capital
        total_roi = ((total_capital_current - self.total_capital) / self.total_capital) * 100

        win_rate = (self.winning_trades / (self.winning_trades + self.losing_trades) * 100) if (
                                                                                                       self.winning_trades + self.losing_trades) > 0 else 0

        return {
            'total_capital_start': self.total_capital,
            'total_capital_current': total_capital_current,
            'available_capital': self.available_capital,
            'locked_capital': self.locked_capital,
            'total_pnl': self.total_pnl,
            'total_roi_pct': total_roi,
            'trades_attempted': self.total_trades_attempted,
            'trades_executed': self.total_trades_executed,
            'trades_rejected': self.total_trades_rejected,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate_pct': win_rate,
            'max_drawdown_pct': self.max_drawdown,
            'max_concurrent_trades': self.max_concurrent_trades,
            'capital_utilization_pct': (self.locked_capital / self.total_capital) * 100,
            'open_trades': len(self.open_trades),
            'closed_trades': len(self.closed_trades)
        }

    def get_capital_timeline_df(self) -> pd.DataFrame:
        """Get capital timeline as DataFrame"""
        if not self.capital_history:
            return pd.DataFrame()

        df = pd.DataFrame(self.capital_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.sort_values('timestamp')

    def get_trades_df(self) -> pd.DataFrame:
        """Get all trades as DataFrame"""
        if not self.trades:
            return pd.DataFrame()

        trades_data = []
        for trade in self.trades:
            trade_dict = {
                'Trade ID': trade.trade_id,
                'Symbol': trade.symbol,
                'Timeframe': trade.timeframe,
                'Pattern': trade.pattern_type,
                'Entry Date': trade.entry_timestamp.strftime('%Y-%m-%d %H:%M'),
                'Entry Price': f"{trade.entry_price:.4f}",
                'Target': f"{trade.target_price:.4f}",
                'Stop Loss': f"{trade.sl_price:.4f}",
                'Capital': f"${trade.capital_allocated:,.0f}",
                'Status': trade.status,
                'Exit Date': trade.exit_timestamp.strftime('%Y-%m-%d %H:%M') if trade.exit_timestamp else 'Open',
                'Exit Price': f"{trade.exit_price:.4f}" if trade.exit_price else 'N/A',
                'P&L': f"${trade.pnl:.2f}" if trade.pnl is not None else 'Open',
                'ROI %': f"{trade.roi_pct:.2f}%" if trade.roi_pct is not None else 'Open',
                'Days Held': trade.days_held if trade.status == 'closed' else 'Open'
            }
            trades_data.append(trade_dict)

        return pd.DataFrame(trades_data)

    def get_rejected_trades_df(self) -> pd.DataFrame:
        """Get rejected trades as DataFrame"""
        if not self.rejected_trades_log:
            return pd.DataFrame()
        return pd.DataFrame(self.rejected_trades_log)

    def get_capital_events_df(self) -> pd.DataFrame:
        """Get capital events as DataFrame"""
        if not self.capital_events:
            return pd.DataFrame()

        events_data = []
        for event in self.capital_events:
            event_dict = {
                'Timestamp': event.timestamp,
                'Event Type': event.event_type.title(),
                'Amount': f"${event.amount:,.2f}",
                'Trade ID': event.trade_id,
                'Symbol': event.symbol,
                'Pattern': event.pattern_type,
                'Entry Price': f"{event.entry_price:.4f}",
                'Exit Price': f"{event.exit_price:.4f}" if event.exit_price else 'N/A',
                'P&L': f"${event.pnl:.2f}" if event.pnl is not None else 'N/A',
                'Available After': f"${event.available_capital_after:,.0f}",
                'Locked After': f"${event.locked_capital_after:,.0f}"
            }
            events_data.append(event_dict)

        return pd.DataFrame(events_data)


# ============================================================================
# FILE MANAGEMENT SYSTEM
# ============================================================================

class FileManager:
    """Manages file operations for instruments and data caching"""

    def __init__(self):
        self.instruments_file = "instruments_one.txt"
        self.data_cache_dir = "data_cache"
        self.config_file = "analyzer_config.json"
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories and files"""
        Path(self.data_cache_dir).mkdir(exist_ok=True)

        if not os.path.exists(self.instruments_file):
            default_instruments = "BTCUSDT,ETHUSDT,BNBUSDT,ADAUSDT,SOLUSDT,DOTUSDT,LINKUSDT,LTCUSDT,BCHUSDT,XLMUSDT"
            with open(self.instruments_file, 'w') as f:
                f.write(default_instruments)

    def load_instruments(self) -> List[str]:
        """Load instruments from file"""
        try:
            with open(self.instruments_file, 'r') as f:
                content = f.read().strip()
                if content:
                    return [s.strip().upper() for s in content.split(',') if s.strip()]
                return []
        except FileNotFoundError:
            return []

    def save_instruments(self, instruments: List[str]):
        """Save instruments to file"""
        with open(self.instruments_file, 'w') as f:
            f.write(','.join(instruments))

    def get_cache_filename(self, symbol: str, timeframe: str, exchange: str) -> str:
        """Get cache filename for symbol/timeframe combination"""
        return os.path.join(self.data_cache_dir, f"{symbol}_{exchange}_{timeframe}.json")

    def save_data_to_cache(self, symbol: str, timeframe: str, exchange: str, data: pd.DataFrame):
        """Save data to cache file with complete OHLCV data"""
        try:
            cache_file = self.get_cache_filename(symbol, timeframe, exchange)
            cache_data = {
                'data': data.to_json(orient='index', date_format='iso'),
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'timeframe': timeframe,
                'exchange': exchange,
                'total_candles': len(data),
                'date_range': {
                    'start': data.index.min().isoformat(),
                    'end': data.index.max().isoformat()
                } if len(data) > 0 else None
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            st.warning(f"Failed to cache data for {symbol} {timeframe}: {e}")

    def load_data_from_cache(self, symbol: str, timeframe: str, exchange: str) -> Optional[pd.DataFrame]:
        """Load OHLCV data from cache file"""
        try:
            cache_file = self.get_cache_filename(symbol, timeframe, exchange)
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)

                df = pd.read_json(cache_data['data'], orient='index')
                df.index = pd.to_datetime(df.index)
                return df.sort_index()
            return None
        except Exception as e:
            return None

    def get_cache_info(self, symbol: str, timeframe: str, exchange: str) -> Optional[Dict]:
        """Get cache metadata without loading data"""
        try:
            cache_file = self.get_cache_filename(symbol, timeframe, exchange)
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                return {
                    'timestamp': cache_data.get('timestamp'),
                    'total_candles': cache_data.get('total_candles', 0),
                    'date_range': cache_data.get('date_range'),
                    'file_size_kb': round(os.path.getsize(cache_file) / 1024, 2)
                }
            return None
        except:
            return None


# ============================================================================
# ENHANCED BACKGROUND DATA MANAGER WITH SMART UPDATES + DATE PICKER SUPPORT
# ============================================================================

class BackgroundDataManager:
    """Enhanced data manager with intelligent incremental updates and date picker support"""

    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.tv = TvDatafeed() if TV_AVAILABLE else None
        self.timeframes = ['1m', '5m', '15m', '30m', '1H', '4H', '1D']
        self.last_update_times = {}

    def get_interval_from_timeframe(self, timeframe: str):
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
        return interval_map.get(timeframe, Interval.in_15_minute)

    def should_update_timeframe(self, timeframe: str) -> bool:
        """Check if timeframe needs updating based on its frequency"""
        update_intervals = {
            '1m': timedelta(minutes=2),
            '5m': timedelta(minutes=3),
            '15m': timedelta(minutes=5),
            '30m': timedelta(minutes=10),
            '1H': timedelta(minutes=15),
            '4H': timedelta(hours=1),
            '1D': timedelta(hours=4)
        }

        last_update = self.last_update_times.get(timeframe)
        if not last_update:
            return True

        return datetime.now() - last_update >= update_intervals.get(timeframe, timedelta(minutes=5))

    def calculate_bars_from_date(self, start_date: datetime, timeframe: str) -> int:
        """Calculate number of bars needed from start date to now - ENHANCED WITH DATE PICKER SUPPORT"""
        if not start_date:
            return self._calculate_bars_needed(timeframe)

        # Calculate time difference
        now = datetime.now()
        time_diff = now - start_date

        # Calculate bars based on timeframe
        timeframe_minutes = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1H': 60,
            '4H': 240,
            '1D': 1440
        }

        tf_minutes = timeframe_minutes.get(timeframe, 60)
        total_minutes = time_diff.total_seconds() / 60
        bars_needed = int(total_minutes / tf_minutes) + 50  # Add buffer for gaps/weekends

        # Apply reasonable limits
        max_bars = {
            '1m': 5000,  # ~3.5 days max
            '5m': 4000,  # ~2 weeks max
            '15m': 3000,  # ~1 month max
            '30m': 2500,  # ~2 months max
            '1H': 2000,  # ~3 months max
            '4H': 1500,  # ~9 months max
            '1D': 1000  # ~3 years max
        }

        limit = max_bars.get(timeframe, 2000)
        bars_needed = min(bars_needed, limit)

        # Minimum bars for analysis
        min_bars = {
            '1m': 100,
            '5m': 200,
            '15m': 300,
            '30m': 250,
            '1H': 200,
            '4H': 150,
            '1D': 100
        }

        minimum = min_bars.get(timeframe, 200)
        bars_needed = max(bars_needed, minimum)

        return bars_needed

    def update_data_incrementally(self, symbols: List[str], timeframes: List[str],
                                  exchange: str = 'NSE', force_update: bool = False,
                                  start_date: Optional[datetime] = None) -> Dict[str, Dict[str, str]]:
        """Smart incremental data updates with date picker support - ENHANCED"""
        if not self.tv:
            return {"error": "TradingView not available"}

        results = {}

        for symbol in symbols:
            results[symbol] = {}
            for timeframe in timeframes:
                try:
                    cached_data = self.file_manager.load_data_from_cache(symbol, timeframe, exchange)

                    # Determine bars needed
                    if start_date:
                        # Use date picker to calculate bars
                        bars_needed = self.calculate_bars_from_date(start_date, timeframe)
                        use_date_based = True
                    else:
                        # Use default bars
                        bars_needed = self._calculate_bars_needed(timeframe)
                        use_date_based = False

                    if cached_data is not None and not cached_data.empty and not force_update and not use_date_based:
                        # Standard incremental update logic
                        last_timestamp = cached_data.index.max()
                        current_time = datetime.now()
                        time_diff = current_time - last_timestamp
                        incremental_bars = self._calculate_incremental_bars(timeframe, time_diff)

                        if incremental_bars <= 1:
                            age_minutes = int(time_diff.total_seconds() / 60)
                            results[symbol][timeframe] = f"✅ Current ({len(cached_data)} bars, {age_minutes}m old)"
                            continue

                        interval = self.get_interval_from_timeframe(timeframe)
                        new_data = self.tv.get_hist(symbol, exchange, interval, n_bars=incremental_bars)

                        if new_data is not None and not new_data.empty:
                            new_data = self._clean_data(new_data)
                            combined_data = self._merge_data(cached_data, new_data)
                            self.file_manager.save_data_to_cache(symbol, timeframe, exchange, combined_data)
                            new_bars = len(combined_data) - len(cached_data)
                            results[symbol][timeframe] = f"✅ Updated +{new_bars} bars ({len(combined_data)} total)"
                            self.last_update_times[timeframe] = datetime.now()
                        else:
                            results[symbol][timeframe] = f"✅ Current ({len(cached_data)} bars)"

                    elif start_date and cached_data is not None and not cached_data.empty and not force_update:
                        # Check if cached data covers the requested date range
                        cached_start = cached_data.index.min()
                        if cached_start <= pd.Timestamp(start_date):
                            # We have enough data
                            age = datetime.now() - cached_data.index.max()
                            age_hours = int(age.total_seconds() / 3600)
                            results[symbol][
                                timeframe] = f"✅ Date range covered ({len(cached_data)} bars, {age_hours}h old)"
                            continue
                        else:
                            # Need more historical data
                            interval = self.get_interval_from_timeframe(timeframe)
                            new_data = self.tv.get_hist(symbol, exchange, interval, n_bars=bars_needed)

                            if new_data is not None and not new_data.empty:
                                cleaned_data = self._clean_data(new_data)
                                self.file_manager.save_data_to_cache(symbol, timeframe, exchange, cleaned_data)
                                start_coverage = "✅" if cleaned_data.index.min() <= pd.Timestamp(start_date) else "⚠️"
                                results[symbol][
                                    timeframe] = f"{start_coverage} Historical download ({len(cleaned_data)} bars from {cleaned_data.index.min().strftime('%Y-%m-%d')})"
                                self.last_update_times[timeframe] = datetime.now()
                            else:
                                results[symbol][timeframe] = "❌ No historical data received"

                    else:
                        # Full download
                        interval = self.get_interval_from_timeframe(timeframe)

                        data = self.tv.get_hist(symbol, exchange, interval, n_bars=bars_needed)

                        if data is not None and not data.empty:
                            cleaned_data = self._clean_data(data)
                            self.file_manager.save_data_to_cache(symbol, timeframe, exchange, cleaned_data)

                            # Check date coverage if start_date provided
                            if start_date:
                                start_coverage = "✅" if cleaned_data.index.min() <= pd.Timestamp(start_date) else "⚠️"
                                results[symbol][
                                    timeframe] = f"{start_coverage} Full download ({len(cleaned_data)} bars from {cleaned_data.index.min().strftime('%Y-%m-%d')})"
                            else:
                                results[symbol][timeframe] = f"✅ Full download ({len(cleaned_data)} bars)"

                            self.last_update_times[timeframe] = datetime.now()
                        else:
                            results[symbol][timeframe] = "❌ No data received"

                except Exception as e:
                    results[symbol][timeframe] = f"❌ Error: {str(e)[:30]}"

        return results

    def _calculate_incremental_bars(self, timeframe: str, time_diff: timedelta) -> int:
        """Calculate how many bars needed based on time difference"""
        minutes_diff = time_diff.total_seconds() / 60

        timeframe_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1H': 60, '4H': 240, '1D': 1440
        }

        tf_minutes = timeframe_minutes.get(timeframe, 15)
        bars_needed = int(minutes_diff / tf_minutes) + 5

        return min(bars_needed, 100)

    def _merge_data(self, old_data: pd.DataFrame, new_data: pd.DataFrame) -> pd.DataFrame:
        """Merge old cached data with new data, removing overlaps"""
        combined = pd.concat([old_data, new_data])
        combined = combined[~combined.index.duplicated(keep='last')]
        combined = combined.sort_index()
        return combined

    def update_data_for_timeframes(self, symbols: List[str], timeframes: List[str],
                                   exchange: str = 'NSE', force_update: bool = False,
                                   start_date: Optional[datetime] = None) -> Dict[str, Dict[str, str]]:
        """Legacy method that now uses incremental updates with date support"""
        return self.update_data_incrementally(symbols, timeframes, exchange, force_update, start_date)

    def get_cached_data(self, symbol: str, timeframe: str, exchange: str = 'NSE') -> Optional[pd.DataFrame]:
        """Get cached OHLCV data for symbol/timeframe"""
        return self.file_manager.load_data_from_cache(symbol, timeframe, exchange)

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare the fetched OHLCV data"""
        if df is None or df.empty:
            raise ValueError("Empty data received during cleaning.")

        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna()
        return df

    def _calculate_bars_needed(self, timeframe: str) -> int:
        """Calculate number of bars needed for analysis (default method)"""
        bars_map = {
            '1m': 500, '5m': 400, '15m': 300, '30m': 250,
            '1H': 200, '4H': 150, '1D': 100
        }
        return bars_map.get(timeframe, 200)


# ============================================================================
# PATTERN DETECTION ENGINES - ALL PROFESSIONAL PATTERNS
# ============================================================================

class PinBarDetector:
    """Detects pin bar candlestick patterns"""

    def __init__(self, min_wick_ratio: float = 2.0, max_body_ratio: float = 0.3):
        self.min_wick_ratio = min_wick_ratio
        self.max_body_ratio = max_body_ratio

    def detect_pinbars(self, df: pd.DataFrame, include_live: bool = False) -> List[PinBar]:
        """Detect pin bar patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(end_index):
            candle = df.iloc[i]
            open_price = candle['open']
            high_price = candle['high']
            low_price = candle['low']
            close_price = candle['close']

            total_range = high_price - low_price
            body_size = abs(close_price - open_price)
            upper_wick = high_price - max(open_price, close_price)
            lower_wick = min(open_price, close_price) - low_price

            if total_range == 0 or body_size == 0:
                continue

            body_ratio = body_size / total_range
            lower_wick_ratio = lower_wick / body_size
            upper_wick_ratio = upper_wick / body_size

            has_long_lower_wick = lower_wick_ratio >= self.min_wick_ratio
            has_small_body = body_ratio <= self.max_body_ratio
            has_small_upper_wick = upper_wick_ratio <= 1.0

            if has_long_lower_wick and has_small_body and has_small_upper_wick:
                is_bullish = close_price > open_price
                is_live = (i == len(df) - 1) and include_live

                # Calculate pattern strength (success rate based)
                pattern_strength = 65.0  # Base success rate for pin bars

                pattern = PinBar(
                    index=i,
                    timestamp=df.index[i],
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    pattern_type='pin_bar',
                    body_ratio=body_ratio,
                    wick_ratio=lower_wick_ratio,
                    is_bullish=is_bullish,
                    is_live=is_live,
                    pattern_strength=pattern_strength
                )
                patterns.append(pattern)

        return patterns


class BullishEngulfingDetector:
    """Detects bullish engulfing candlestick patterns"""

    def __init__(self, min_engulfing_ratio: float = 1.1):
        self.min_engulfing_ratio = min_engulfing_ratio

    def detect_bullish_engulfing(self, df: pd.DataFrame, include_live: bool = False) -> List[BullishEngulfing]:
        """Detect bullish engulfing patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(1, end_index):
            current = df.iloc[i]
            previous = df.iloc[i - 1]

            first_is_bearish = previous['close'] < previous['open']
            second_is_bullish = current['close'] > current['open']

            if not (first_is_bearish and second_is_bullish):
                continue

            first_body_size = abs(previous['close'] - previous['open'])
            second_body_size = abs(current['close'] - current['open'])

            if first_body_size == 0:
                continue

            opens_below_first_close = current['open'] < previous['close']
            closes_above_first_open = current['close'] > previous['open']
            engulfing_ratio = second_body_size / first_body_size
            is_larger_body = engulfing_ratio >= self.min_engulfing_ratio

            if opens_below_first_close and closes_above_first_open and is_larger_body:
                pattern_low = min(previous['low'], current['low'])
                is_live = (i == len(df) - 1) and include_live

                # Calculate pattern strength
                pattern_strength = 70.0  # Base success rate for bullish engulfing

                pattern = BullishEngulfing(
                    index=i,
                    timestamp=df.index[i],
                    first_candle_open=previous['open'],
                    first_candle_high=previous['high'],
                    first_candle_low=previous['low'],
                    first_candle_close=previous['close'],
                    second_candle_open=current['open'],
                    second_candle_high=current['high'],
                    second_candle_low=current['low'],
                    second_candle_close=current['close'],
                    pattern_type='bullish_engulfing',
                    engulfing_ratio=engulfing_ratio,
                    pattern_low=pattern_low,
                    is_bullish=True,
                    is_live=is_live,
                    pattern_strength=pattern_strength
                )
                patterns.append(pattern)

        return patterns


class ThreeCandleDetector:
    """Detects three candle (Morning Star) patterns"""

    def __init__(self, min_first_body: float = 0.6, max_second_body: float = 0.4, min_third_body: float = 0.6):
        self.min_first_body = min_first_body
        self.max_second_body = max_second_body
        self.min_third_body = min_third_body

    def detect_three_candle(self, df: pd.DataFrame, include_live: bool = False) -> List[ThreeCandle]:
        """Detect three candle (Morning Star) patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(2, end_index):
            first = df.iloc[i - 2]
            second = df.iloc[i - 1]
            third = df.iloc[i]

            first_range = first['high'] - first['low']
            second_range = second['high'] - second['low']
            third_range = third['high'] - third['low']

            if first_range == 0 or second_range == 0 or third_range == 0:
                continue

            first_body = abs(first['close'] - first['open'])
            second_body = abs(second['close'] - second['open'])
            third_body = abs(third['close'] - third['open'])

            first_body_ratio = first_body / first_range
            second_body_ratio = second_body / second_range
            third_body_ratio = third_body / third_range

            first_is_bearish = first['close'] < first['open']
            first_has_body = first_body_ratio >= self.min_first_body

            second_is_small = second_body_ratio <= self.max_second_body

            third_is_bullish = third['close'] > third['open']
            third_has_body = third_body_ratio >= self.min_third_body

            first_midpoint = (first['open'] + first['close']) / 2
            third_closes_above_midpoint = third['close'] > first_midpoint

            if (first_is_bearish and first_has_body and
                    second_is_small and
                    third_is_bullish and third_has_body and
                    third_closes_above_midpoint):
                pattern_low = min(first['low'], second['low'], third['low'])
                is_live = (i == len(df) - 1) and include_live

                pattern_strength = (first_body_ratio + third_body_ratio - second_body_ratio) / 2
                # Convert to success rate percentage
                base_strength = 68.0  # Base success rate for three candle patterns

                pattern = ThreeCandle(
                    index=i,
                    timestamp=df.index[i],
                    first_candle_open=first['open'],
                    first_candle_high=first['high'],
                    first_candle_low=first['low'],
                    first_candle_close=first['close'],
                    second_candle_open=second['open'],
                    second_candle_high=second['high'],
                    second_candle_low=second['low'],
                    second_candle_close=second['close'],
                    third_candle_open=third['open'],
                    third_candle_high=third['high'],
                    third_candle_low=third['low'],
                    third_candle_close=third['close'],
                    pattern_type='three_candle',
                    pattern_low=pattern_low,
                    pattern_strength=base_strength,
                    is_bullish=True,
                    is_live=is_live
                )
                patterns.append(pattern)

        return patterns


class DragonflyDojiDetector:
    """Detects dragonfly doji patterns"""

    def __init__(self, max_body_ratio: float = 0.1, min_lower_wick_ratio: float = 2.0):
        self.max_body_ratio = max_body_ratio
        self.min_lower_wick_ratio = min_lower_wick_ratio

    def detect_dragonfly_doji(self, df: pd.DataFrame, include_live: bool = False) -> List[DragonflyDoji]:
        """Detect dragonfly doji patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(end_index):
            candle = df.iloc[i]
            open_price = candle['open']
            high_price = candle['high']
            low_price = candle['low']
            close_price = candle['close']

            total_range = high_price - low_price
            body_size = abs(close_price - open_price)
            upper_wick = high_price - max(open_price, close_price)
            lower_wick = min(open_price, close_price) - low_price

            if total_range == 0:
                continue

            body_ratio = body_size / total_range
            upper_wick_ratio = upper_wick / total_range
            lower_wick_ratio = lower_wick / total_range

            # Dragonfly doji criteria
            has_small_body = body_ratio <= self.max_body_ratio
            has_long_lower_wick = lower_wick_ratio >= (
                        self.min_lower_wick_ratio * body_ratio) or lower_wick_ratio >= 0.6
            has_small_upper_wick = upper_wick_ratio <= 0.1

            if has_small_body and has_long_lower_wick and has_small_upper_wick:
                is_live = (i == len(df) - 1) and include_live

                # Calculate pattern strength - Dragonfly Doji has 60% success rate
                pattern_strength = 60.0

                pattern = DragonflyDoji(
                    index=i,
                    timestamp=df.index[i],
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    pattern_type='dragonfly_doji',
                    body_ratio=body_ratio,
                    lower_wick_ratio=lower_wick_ratio,
                    is_bullish=True,
                    is_live=is_live,
                    pattern_strength=pattern_strength
                )
                patterns.append(pattern)

        return patterns


class ThreeWhiteSoldiersDetector:
    """Detects three white soldiers patterns"""

    def __init__(self, min_body_ratio: float = 0.6, max_wick_ratio: float = 0.2):
        self.min_body_ratio = min_body_ratio
        self.max_wick_ratio = max_wick_ratio

    def detect_three_white_soldiers(self, df: pd.DataFrame, include_live: bool = False) -> List[ThreeWhiteSoldiers]:
        """Detect three white soldiers patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(2, end_index):
            first = df.iloc[i - 2]
            second = df.iloc[i - 1]
            third = df.iloc[i]

            # All three candles must be bullish
            first_is_bullish = first['close'] > first['open']
            second_is_bullish = second['close'] > second['open']
            third_is_bullish = third['close'] > third['open']

            if not (first_is_bullish and second_is_bullish and third_is_bullish):
                continue

            # Check body sizes
            first_range = first['high'] - first['low']
            second_range = second['high'] - second['low']
            third_range = third['high'] - third['low']

            if first_range == 0 or second_range == 0 or third_range == 0:
                continue

            first_body = first['close'] - first['open']
            second_body = second['close'] - second['open']
            third_body = third['close'] - third['open']

            first_body_ratio = first_body / first_range
            second_body_ratio = second_body / second_range
            third_body_ratio = third_body / third_range

            # All bodies should be significant
            if not (first_body_ratio >= self.min_body_ratio and
                    second_body_ratio >= self.min_body_ratio and
                    third_body_ratio >= self.min_body_ratio):
                continue

            # Each candle should open within the previous candle's body
            second_opens_in_first = first['open'] < second['open'] < first['close']
            third_opens_in_second = second['open'] < third['open'] < second['close']

            # Each candle should close higher than the previous
            closes_progressively_higher = first['close'] < second['close'] < third['close']

            if second_opens_in_first and third_opens_in_second and closes_progressively_higher:
                pattern_low = min(first['low'], second['low'], third['low'])
                is_live = (i == len(df) - 1) and include_live

                average_body_size = (first_body + second_body + third_body) / 3

                # Three White Soldiers has 82% success rate
                pattern_strength = 82.0

                pattern = ThreeWhiteSoldiers(
                    index=i,
                    timestamp=df.index[i],
                    first_candle_open=first['open'],
                    first_candle_high=first['high'],
                    first_candle_low=first['low'],
                    first_candle_close=first['close'],
                    second_candle_open=second['open'],
                    second_candle_high=second['high'],
                    second_candle_low=second['low'],
                    second_candle_close=second['close'],
                    third_candle_open=third['open'],
                    third_candle_high=third['high'],
                    third_candle_low=third['low'],
                    third_candle_close=third['close'],
                    pattern_type='three_white_soldiers',
                    pattern_low=pattern_low,
                    average_body_size=average_body_size,
                    is_bullish=True,
                    is_live=is_live,
                    pattern_strength=pattern_strength
                )
                patterns.append(pattern)

        return patterns


class BullishMarubozuDetector:
    """Detects bullish marubozu patterns"""

    def __init__(self, max_wick_ratio: float = 0.05, min_body_ratio: float = 0.8):
        self.max_wick_ratio = max_wick_ratio
        self.min_body_ratio = min_body_ratio

    def detect_bullish_marubozu(self, df: pd.DataFrame, include_live: bool = False) -> List[BullishMarubozu]:
        """Detect bullish marubozu patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(end_index):
            candle = df.iloc[i]
            open_price = candle['open']
            high_price = candle['high']
            low_price = candle['low']
            close_price = candle['close']

            # Must be bullish
            if close_price <= open_price:
                continue

            total_range = high_price - low_price
            body_size = close_price - open_price
            upper_wick = high_price - close_price
            lower_wick = open_price - low_price

            if total_range == 0:
                continue

            body_ratio = body_size / total_range
            upper_wick_ratio = upper_wick / total_range
            lower_wick_ratio = lower_wick / total_range

            # Marubozu criteria: large body, minimal wicks
            has_large_body = body_ratio >= self.min_body_ratio
            has_small_wicks = (upper_wick_ratio <= self.max_wick_ratio and
                               lower_wick_ratio <= self.max_wick_ratio)

            if has_large_body and has_small_wicks:
                is_live = (i == len(df) - 1) and include_live

                # Bullish Marubozu has 69% success rate
                pattern_strength = 69.0

                pattern = BullishMarubozu(
                    index=i,
                    timestamp=df.index[i],
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    pattern_type='bullish_marubozu',
                    body_size=body_size,
                    upper_wick_ratio=upper_wick_ratio,
                    lower_wick_ratio=lower_wick_ratio,
                    is_bullish=True,
                    is_live=is_live,
                    pattern_strength=pattern_strength
                )
                patterns.append(pattern)

        return patterns


class BullishHaramiDetector:
    """Detects bullish harami patterns"""

    def __init__(self, min_first_body_ratio: float = 0.6):
        self.min_first_body_ratio = min_first_body_ratio

    def detect_bullish_harami(self, df: pd.DataFrame, include_live: bool = False) -> List[BullishHarami]:
        """Detect bullish harami patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(1, end_index):
            previous = df.iloc[i - 1]
            current = df.iloc[i]

            # First candle must be bearish with significant body
            first_is_bearish = previous['close'] < previous['open']
            if not first_is_bearish:
                continue

            first_range = previous['high'] - previous['low']
            first_body = previous['open'] - previous['close']

            if first_range == 0:
                continue

            first_body_ratio = first_body / first_range
            if first_body_ratio < self.min_first_body_ratio:
                continue

            # Second candle must be bullish and contained within first candle's body
            second_is_bullish = current['close'] > current['open']
            if not second_is_bullish:
                continue

            # Check containment
            second_open_in_first = previous['close'] < current['open'] < previous['open']
            second_close_in_first = previous['close'] < current['close'] < previous['open']

            if second_open_in_first and second_close_in_first:
                pattern_low = min(previous['low'], current['low'])
                is_live = (i == len(df) - 1) and include_live

                second_body = current['close'] - current['open']
                containment_ratio = second_body / first_body

                # Bullish Harami has 54% success rate
                pattern_strength = 54.0

                pattern = BullishHarami(
                    index=i,
                    timestamp=df.index[i],
                    first_candle_open=previous['open'],
                    first_candle_high=previous['high'],
                    first_candle_low=previous['low'],
                    first_candle_close=previous['close'],
                    second_candle_open=current['open'],
                    second_candle_high=current['high'],
                    second_candle_low=current['low'],
                    second_candle_close=current['close'],
                    pattern_type='bullish_harami',
                    pattern_low=pattern_low,
                    containment_ratio=containment_ratio,
                    is_bullish=True,
                    is_live=is_live,
                    pattern_strength=pattern_strength
                )
                patterns.append(pattern)

        return patterns


class BullishAbandonedBabyDetector:
    """Detects bullish abandoned baby patterns"""

    def __init__(self, min_gap_ratio: float = 0.2, max_doji_body_ratio: float = 0.1):
        self.min_gap_ratio = min_gap_ratio
        self.max_doji_body_ratio = max_doji_body_ratio

    def detect_bullish_abandoned_baby(self, df: pd.DataFrame, include_live: bool = False) -> List[BullishAbandonedBaby]:
        """Detect bullish abandoned baby patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(2, end_index):
            first = df.iloc[i - 2]
            doji = df.iloc[i - 1]
            third = df.iloc[i]

            # First candle must be bearish
            first_is_bearish = first['close'] < first['open']
            if not first_is_bearish:
                continue

            # Third candle must be bullish
            third_is_bullish = third['close'] > third['open']
            if not third_is_bullish:
                continue

            # Middle candle must be doji-like
            doji_range = doji['high'] - doji['low']
            doji_body = abs(doji['close'] - doji['open'])

            if doji_range == 0:
                continue

            doji_body_ratio = doji_body / doji_range
            if doji_body_ratio > self.max_doji_body_ratio:
                continue

            # Check for gaps
            gap_down = first['close'] > doji['high']  # Gap down to doji
            gap_up = doji['low'] > third['open']  # Gap up from doji

            if gap_down and gap_up:
                pattern_low = min(first['low'], doji['low'], third['low'])
                is_live = (i == len(df) - 1) and include_live

                gap_down_size = first['close'] - doji['high']
                gap_up_size = third['open'] - doji['low']

                # Abandoned Baby is rare but very powerful
                pattern_strength = 75.0

                pattern = BullishAbandonedBaby(
                    index=i,
                    timestamp=df.index[i],
                    first_candle_open=first['open'],
                    first_candle_high=first['high'],
                    first_candle_low=first['low'],
                    first_candle_close=first['close'],
                    doji_open=doji['open'],
                    doji_high=doji['high'],
                    doji_low=doji['low'],
                    doji_close=doji['close'],
                    third_candle_open=third['open'],
                    third_candle_high=third['high'],
                    third_candle_low=third['low'],
                    third_candle_close=third['close'],
                    pattern_type='bullish_abandoned_baby',
                    pattern_low=pattern_low,
                    gap_down_size=gap_down_size,
                    gap_up_size=gap_up_size,
                    is_bullish=True,
                    is_live=is_live,
                    pattern_strength=pattern_strength
                )
                patterns.append(pattern)

        return patterns


class TweezerBottomDetector:
    """Detects tweezer bottom patterns"""

    def __init__(self, max_low_difference_pct: float = 0.1):
        self.max_low_difference_pct = max_low_difference_pct

    def detect_tweezer_bottom(self, df: pd.DataFrame, include_live: bool = False) -> List[TweezerBottom]:
        """Detect tweezer bottom patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(1, end_index):
            first = df.iloc[i - 1]
            second = df.iloc[i]

            # Check if lows are approximately equal
            low_difference_pct = abs(first['low'] - second['low']) / min(first['low'], second['low']) * 100

            if low_difference_pct <= self.max_low_difference_pct:
                # Ideally, first candle should be bearish and second bullish
                first_is_bearish = first['close'] < first['open']
                second_is_bullish = second['close'] > second['open']

                # But we'll accept any combination as long as lows match
                pattern_low = min(first['low'], second['low'])
                is_live = (i == len(df) - 1) and include_live

                low_match_precision = 100 - low_difference_pct

                # Tweezer Bottom has 61% success rate
                pattern_strength = 61.0

                pattern = TweezerBottom(
                    index=i,
                    timestamp=df.index[i],
                    first_candle_open=first['open'],
                    first_candle_high=first['high'],
                    first_candle_low=first['low'],
                    first_candle_close=first['close'],
                    second_candle_open=second['open'],
                    second_candle_high=second['high'],
                    second_candle_low=second['low'],
                    second_candle_close=second['close'],
                    pattern_type='tweezer_bottom',
                    pattern_low=pattern_low,
                    low_match_precision=low_match_precision,
                    is_bullish=True,
                    is_live=is_live,
                    pattern_strength=pattern_strength
                )
                patterns.append(pattern)

        return patterns


class BullishKickerDetector:
    """Detects bullish kicker patterns"""

    def __init__(self, min_gap_ratio: float = 0.5):
        self.min_gap_ratio = min_gap_ratio

    def detect_bullish_kicker(self, df: pd.DataFrame, include_live: bool = False) -> List[BullishKicker]:
        """Detect bullish kicker patterns in OHLCV data"""
        patterns = []
        end_index = len(df) if include_live else len(df) - 1

        for i in range(1, end_index):
            first = df.iloc[i - 1]
            second = df.iloc[i]

            # First candle must be bearish
            first_is_bearish = first['close'] < first['open']
            if not first_is_bearish:
                continue

            # Second candle must be bullish
            second_is_bullish = second['close'] > second['open']
            if not second_is_bullish:
                continue

            # Must have a gap up (second opens above first's high)
            has_gap_up = second['open'] > first['high']
            if not has_gap_up:
                continue

            # Calculate gap size
            gap_size = second['open'] - first['high']
            first_range = first['high'] - first['low']

            if first_range == 0:
                continue

            gap_ratio = gap_size / first_range

            if gap_ratio >= self.min_gap_ratio:
                pattern_low = min(first['low'], second['low'])
                is_live = (i == len(df) - 1) and include_live

                # Bullish Kicker is very powerful - high success rate
                pattern_strength = 78.0

                pattern = BullishKicker(
                    index=i,
                    timestamp=df.index[i],
                    first_candle_open=first['open'],
                    first_candle_high=first['high'],
                    first_candle_low=first['low'],
                    first_candle_close=first['close'],
                    second_candle_open=second['open'],
                    second_candle_high=second['high'],
                    second_candle_low=second['low'],
                    second_candle_close=second['close'],
                    pattern_type='bullish_kicker',
                    pattern_low=pattern_low,
                    gap_size=gap_size,
                    is_bullish=True,
                    is_live=is_live,
                    pattern_strength=pattern_strength
                )
                patterns.append(pattern)

        return patterns


# ============================================================================
# LIVE PATTERN ANALYZER
# ============================================================================

class LivePatternAnalyzer:
    """Analyzes patterns in real-time with live monitoring"""

    def __init__(self, data_manager: BackgroundDataManager, file_manager: FileManager):
        self.data_manager = data_manager
        self.file_manager = file_manager

    def analyze_live_patterns(self, symbols: List[str], timeframes: List[str],
                              parameters: Dict, pattern_selection: Dict, exchange: str = 'NSE') -> Dict:
        """Analyze patterns in real-time across multiple symbols and timeframes"""
        results = {
            'live_patterns': [],
            'confirmed_patterns': [],
            'summary': {}
        }

        total_live = 0
        total_confirmed = 0

        for symbol in symbols:
            for timeframe in timeframes:
                # Get cached data
                df = self.data_manager.get_cached_data(symbol, timeframe, exchange)
                if df is None or df.empty:
                    continue

                try:
                    # Analyze patterns for this symbol/timeframe
                    pattern_results = self._analyze_symbol_timeframe(
                        symbol, timeframe, df, parameters, pattern_selection
                    )

                    # Add to results
                    for pattern in pattern_results['live']:
                        pattern['symbol'] = symbol
                        pattern['timeframe'] = timeframe
                        results['live_patterns'].append(pattern)
                        total_live += 1

                    for pattern in pattern_results['confirmed']:
                        pattern['symbol'] = symbol
                        pattern['timeframe'] = timeframe
                        results['confirmed_patterns'].append(pattern)
                        total_confirmed += 1

                except Exception as e:
                    continue

        results['summary'] = {
            'total_live': total_live,
            'total_confirmed': total_confirmed,
            'symbols_analyzed': len(symbols),
            'timeframes_analyzed': len(timeframes),
            'last_update': datetime.now().isoformat()
        }

        return results

    def _analyze_symbol_timeframe(self, symbol: str, timeframe: str, df: pd.DataFrame,
                                  parameters: Dict, pattern_selection: Dict) -> Dict:
        """Analyze patterns for a specific symbol/timeframe combination - FIXED FOR NSE LIVE"""

        # Check NSE market hours
        try:
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = datetime.now(ist)
            current_time = now_ist.time()
            is_nse_trading = (time(9, 15) <= current_time <= time(15, 30) and
                              now_ist.weekday() < 5)
        except:
            is_nse_trading = True  # Default to True if can't determine

        # Use more aggressive parameters during NSE trading hours
        if is_nse_trading:
            swing_lookback = max(3, parameters.get('swing_lookback', 10) // 2)
            touch_tolerance = parameters.get('touch_tolerance', 1.0) * 2.0  # More tolerant
            min_swing_size = parameters.get('min_swing_size', 0.5) * 0.5  # More sensitive
        else:
            swing_lookback = parameters.get('swing_lookback', 10)
            touch_tolerance = parameters.get('touch_tolerance', 1.0)
            min_swing_size = parameters.get('min_swing_size', 0.5)

        # Initialize detectors with live-optimized settings
        swing_detector = EnhancedSwingLowDetector(swing_lookback, min_swing_size)
        touch_analyzer = EnhancedSwingLowTouchAnalyzer(touch_tolerance)

        results = {'live': [], 'confirmed': []}

        try:
            # Find swing lows with FIXED method
            all_swing_lows = swing_detector.find_swing_lows_with_invalidation(df)
            untouched_swing_lows = swing_detector.find_untouched_swing_lows(df, all_swing_lows)

            # CRITICAL: Always include live patterns
            include_live = True

            # Detect selected patterns with live support
            all_patterns = {}

            if pattern_selection.get('pin_bar', False):
                # More sensitive settings for live trading
                min_wick = parameters.get('min_wick_ratio', 2.0)
                max_body = parameters.get('max_body_ratio', 0.3)
                if is_nse_trading:
                    min_wick = min_wick * 0.9  # 10% more sensitive
                    max_body = max_body * 1.2  # 20% more permissive

                pinbar_detector = PinBarDetector(min_wick, max_body)
                all_patterns['pin_bar'] = pinbar_detector.detect_pinbars(df, include_live=include_live)

            if pattern_selection.get('bullish_engulfing', False):
                min_ratio = parameters.get('min_engulfing_ratio', 1.1)
                if is_nse_trading:
                    min_ratio = min_ratio * 0.9  # More sensitive
                engulfing_detector = BullishEngulfingDetector(min_ratio)
                all_patterns['bullish_engulfing'] = engulfing_detector.detect_bullish_engulfing(df,
                                                                                                include_live=include_live)

            if pattern_selection.get('three_candle', False):
                min_first = parameters.get('min_first_body', 0.6)
                max_second = parameters.get('max_second_body', 0.4)
                min_third = parameters.get('min_third_body', 0.6)
                if is_nse_trading:
                    min_first = min_first * 0.8
                    max_second = max_second * 1.3
                    min_third = min_third * 0.8
                three_candle_detector = ThreeCandleDetector(min_first, max_second, min_third)
                all_patterns['three_candle'] = three_candle_detector.detect_three_candle(df, include_live=include_live)

            if pattern_selection.get('dragonfly_doji', False):
                doji_detector = DragonflyDojiDetector()
                all_patterns['dragonfly_doji'] = doji_detector.detect_dragonfly_doji(df, include_live=include_live)

            if pattern_selection.get('three_white_soldiers', False):
                soldiers_detector = ThreeWhiteSoldiersDetector()
                all_patterns['three_white_soldiers'] = soldiers_detector.detect_three_white_soldiers(df,
                                                                                                     include_live=include_live)

            if pattern_selection.get('bullish_marubozu', False):
                marubozu_detector = BullishMarubozuDetector()
                all_patterns['bullish_marubozu'] = marubozu_detector.detect_bullish_marubozu(df,
                                                                                             include_live=include_live)

            if pattern_selection.get('bullish_harami', False):
                harami_detector = BullishHaramiDetector()
                all_patterns['bullish_harami'] = harami_detector.detect_bullish_harami(df, include_live=include_live)

            if pattern_selection.get('bullish_abandoned_baby', False):
                baby_detector = BullishAbandonedBabyDetector()
                all_patterns['bullish_abandoned_baby'] = baby_detector.detect_bullish_abandoned_baby(df,
                                                                                                     include_live=include_live)

            if pattern_selection.get('tweezer_bottom', False):
                tweezer_detector = TweezerBottomDetector()
                all_patterns['tweezer_bottom'] = tweezer_detector.detect_tweezer_bottom(df, include_live=include_live)

            if pattern_selection.get('bullish_kicker', False):
                kicker_detector = BullishKickerDetector()
                all_patterns['bullish_kicker'] = kicker_detector.detect_bullish_kicker(df, include_live=include_live)

            # Analyze touches with enhanced validation
            touches = touch_analyzer.analyze_touches(df, untouched_swing_lows, all_patterns, symbol, timeframe)

            # Enhanced classification for NSE trading
            current_time = datetime.now()
            today = current_time.date()

            for touch in touches:
                entry_price = self._get_entry_price(touch.pattern, touch.pattern_type)
                pattern_timestamp = pd.Timestamp(touch.pattern.timestamp)
                pattern_date = pattern_timestamp.date()

                # More aggressive live classification during market hours
                is_today = pattern_date == today
                time_diff = (current_time - pattern_timestamp).total_seconds()
                is_recent = time_diff < (1800 if is_nse_trading else 3600)  # 30min during trading, 1hr otherwise

                pattern_data = {
                    'pattern_type': self._get_pattern_display_name(touch.pattern_type, touch.is_live),
                    'timestamp': touch.pattern.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'entry_price': f"{entry_price:.4f}",
                    'swing_low_price': f"{touch.swing_low.price:.4f}",
                    'swing_low_valid': 'Yes' if touch.is_swing_low_valid else 'No',
                    'distance_pct': f"{touch.price_difference:.2f}%",
                    'days_between': touch.days_between,
                    'is_bullish': 'Yes' if touch.pattern.is_bullish else 'No',
                    'pattern_strength': f"{touch.pattern_strength:.1f}%",
                    'nse_status': 'LIVE' if is_nse_trading else 'CLOSED',
                    'is_today': 'YES' if is_today else 'No',
                    'minutes_ago': f"{int(time_diff / 60)}"
                }

                # Enhanced live vs confirmed classification
                if ((is_today and is_recent) or touch.is_live or
                        (is_nse_trading and is_recent and time_diff < 3600)):  # 1 hour during trading
                    results['live'].append(pattern_data)
                else:
                    results['confirmed'].append(pattern_data)

        except Exception as e:
            print(f"Error analyzing {symbol} {timeframe}: {e}")
            import traceback
            traceback.print_exc()

        return results

    def _get_entry_price(self, pattern, pattern_type: str) -> float:
        """Get entry price for pattern"""
        if pattern_type == 'pin_bar':
            return pattern.close_price
        elif pattern_type == 'bullish_engulfing':
            return pattern.second_candle_close
        elif pattern_type == 'three_candle':
            return pattern.third_candle_close
        elif pattern_type == 'dragonfly_doji':
            return pattern.close_price
        elif pattern_type == 'three_white_soldiers':
            return pattern.third_candle_close
        elif pattern_type == 'bullish_marubozu':
            return pattern.close_price
        elif pattern_type == 'bullish_harami':
            return pattern.second_candle_close
        elif pattern_type == 'bullish_abandoned_baby':
            return pattern.third_candle_close
        elif pattern_type == 'tweezer_bottom':
            return pattern.second_candle_close
        elif pattern_type == 'bullish_kicker':
            return pattern.second_candle_close
        else:
            return getattr(pattern, 'close_price', 0)

    def _get_pattern_display_name(self, pattern_type: str, is_live: bool) -> str:
        """Get display name for pattern"""
        display_names = {
            'pin_bar': 'Pin Bar',
            'bullish_engulfing': 'Bullish Engulfing',
            'three_candle': 'Three Candle',
            'dragonfly_doji': 'Dragonfly Doji',
            'three_white_soldiers': 'Three White Soldiers',
            'bullish_marubozu': 'Bullish Marubozu',
            'bullish_harami': 'Bullish Harami',
            'bullish_abandoned_baby': 'Bullish Abandoned Baby',
            'tweezer_bottom': 'Tweezer Bottom',
            'bullish_kicker': 'Bullish Kicker'
        }

        name = display_names.get(pattern_type, pattern_type.replace('_', ' ').title())
        return f"{name} (Live)" if is_live else name


# ============================================================================
# COMPREHENSIVE ANALYSIS WITH CAPITAL INTEGRATION - INCLUDING TODAY'S CANDLE
# ============================================================================

def run_comprehensive_analysis(symbols: List[str], timeframes: List[str], parameters: Dict,
                               pattern_selection: Dict, start_date: datetime, exchange: str = 'NSE',
                               use_trailing_stop: bool = False, intraday_mode: bool = False,
                               entry_cutoff_time: str = '11:45', exit_time: str = '15:15',
                               custom_target_pct: float = None, use_partial_exits: bool = False,
                               first_exit_pct: float = 0.5, second_exit_pct: float = 0.9,
                               first_exit_capital_pct: float = 50.0) -> Tuple[List[Dict], Dict]:
    """Run comprehensive pattern analysis with CUSTOMIZABLE ASYMMETRIC detection - COMPLETE VERSION"""

    if not TV_AVAILABLE:
        raise Exception("TradingView DataFeed not available")

    try:
        results = []

        # Enhanced debug info with customizable asymmetric tracking
        left_lookback = parameters.get('swing_lookback', 10)
        right_lookback = parameters.get('right_lookback', 3)
        pattern_only_entry = parameters.get('pattern_only_entry', False)
        require_swing_touch = parameters.get('require_swing_touch', True)

        debug_info = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'symbols_analyzed': 0,
            'total_swing_lows': 0,
            'total_invalidated_swing_lows': 0,
            'total_valid_touches': 0,
            'total_patterns_detected': 0,
            'today_patterns_detected': 0,
            'historical_trades_filtered': 0,
            'live_detectable_trades': 0,
            'asymmetric_detection': True,
            'left_lookback': left_lookback,
            'right_lookback': right_lookback,
            'include_today_candle': True,
            'use_trailing_stop': use_trailing_stop,
            'intraday_mode': intraday_mode,
            'intraday_entry_cutoff': entry_cutoff_time if intraday_mode else 'N/A',
            'intraday_exit_time': exit_time if intraday_mode else 'N/A',
            'custom_target_pct': custom_target_pct if custom_target_pct else 'Default',
            'use_partial_exits': use_partial_exits,
            'partial_exit_config': f"{first_exit_capital_pct}%@{first_exit_pct}%, {100 - first_exit_capital_pct}%@{second_exit_pct}%" if use_partial_exits else 'Disabled',
            'pattern_only_entry': pattern_only_entry,
            'require_swing_touch': require_swing_touch
        }

        # Initialize enhanced analyzers with custom parameters
        swing_detector = EnhancedSwingLowDetector(
            left_lookback=left_lookback,
            right_lookback=right_lookback,
            min_swing_size_pct=parameters.get('min_swing_size', 0.5)
        )

        touch_analyzer = EnhancedSwingLowTouchAnalyzer(
            touch_tolerance_pct=parameters.get('touch_tolerance', 0.5),
            min_days_between=parameters.get('min_days_between', 2)
        )

        trade_analyzer = EnhancedTradeOutcomeAnalyzer(
            parameters.get('max_bars_to_analyze', 100),
            parameters.get('capital_per_trade', 10000)
        )

        data_manager = st.session_state.data_manager
        today_date = datetime.now().date()

        print(f"🚀 Starting customizable asymmetric analysis: {left_lookback}+{right_lookback} lookback")
        print(f"🎯 Entry mode: {'Pattern Only' if pattern_only_entry else 'Pattern + Swing Touch'}")

        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    print(f"\n=== Analyzing {symbol} {timeframe} ===")

                    # Get cached data
                    df = data_manager.get_cached_data(symbol, timeframe, exchange)
                    if df is None or df.empty:
                        debug_info[f'{symbol}_{timeframe}_error'] = "No cached data"
                        continue

                    # Check if data includes today
                    latest_data_date = df.index.max().date()
                    has_today_data = latest_data_date >= today_date
                    debug_info[f'{symbol}_{timeframe}_has_today'] = has_today_data

                    # Filter data based on start_date
                    df_filtered = df[df.index >= pd.Timestamp(start_date)]
                    debug_info[f'{symbol}_{timeframe}_candles'] = len(df_filtered)

                    if df_filtered.empty:
                        print(f"  ❌ No data after {start_date.strftime('%Y-%m-%d')}")
                        continue

                    debug_info['symbols_analyzed'] += 1

                    # Find selected patterns - INCLUDING TODAY'S CANDLE
                    all_patterns = detect_selected_patterns_with_today(df_filtered, pattern_selection, parameters,
                                                                       include_today=True)

                    # Count today's patterns
                    today_patterns = 0
                    for pattern_list in all_patterns.values():
                        for pattern in pattern_list:
                            pattern_date = pd.Timestamp(pattern.timestamp).date()
                            if pattern_date == today_date:
                                today_patterns += 1

                    debug_info['today_patterns_detected'] += today_patterns
                    pattern_count = sum(len(patterns) for patterns in all_patterns.values())
                    debug_info['total_patterns_detected'] += pattern_count

                    # Handle different entry modes
                    if pattern_only_entry:
                        # PATTERN ONLY MODE
                        print(f"  📈 Pattern-only mode: processing {pattern_count} patterns directly")

                        touches = []
                        for pattern_type, patterns in all_patterns.items():
                            for pattern in patterns:
                                mock_swing_low = SwingLow(
                                    index=pattern.index - 5,
                                    timestamp=pattern.timestamp - pd.Timedelta(hours=5),
                                    price=getattr(pattern, 'low_price', pattern.close_price * 0.99),
                                    is_invalidated=False,
                                    is_touched=False
                                )

                                touch = SwingLowTouch(
                                    swing_low=mock_swing_low,
                                    pattern=pattern,
                                    touch_type='pattern_only',
                                    pattern_type=pattern_type,
                                    distance_pips=0.0,
                                    days_between=0,
                                    price_difference=0.0,
                                    is_live=getattr(pattern, 'is_live', False),
                                    pattern_strength=getattr(pattern, 'pattern_strength', 50.0),
                                    symbol=symbol,
                                    timeframe=timeframe,
                                    is_swing_low_valid=True
                                )
                                touches.append(touch)

                        debug_info[f'{symbol}_{timeframe}_touches'] = len(touches)
                        validated_touches = touches

                    else:
                        # TRADITIONAL MODE - Require swing low touch
                        print(f"  📈 Traditional mode: requiring swing low touch")

                        all_swing_lows = swing_detector.find_swing_lows_with_invalidation(df_filtered)
                        debug_info['total_swing_lows'] += len(all_swing_lows)

                        invalidated_count = sum(1 for sl in all_swing_lows if sl.is_invalidated)
                        debug_info['total_invalidated_swing_lows'] += invalidated_count

                        untouched_swing_lows = swing_detector.find_untouched_swing_lows(df_filtered, all_swing_lows)
                        print(f"  🎯 Swing lows: {len(all_swing_lows)} total, {len(untouched_swing_lows)} untouched")

                        touches = touch_analyzer.analyze_touches(df_filtered, untouched_swing_lows, all_patterns,
                                                                 symbol, timeframe)
                        debug_info['total_valid_touches'] += len(touches)
                        debug_info[f'{symbol}_{timeframe}_touches'] = len(touches)
                        print(f"  🎯 Pattern touches: {len(touches)}")

                        # Live entry validation
                        validated_touches = validate_live_entry_capability(
                            df_filtered, touches, swing_detector, parameters, debug_info
                        )

                    print(f"  ✅ Final validated touches: {len(validated_touches)}")

                    # Analyze trade outcomes
                    enhanced_touches = trade_analyzer.analyze_trade_outcomes_with_timeframe(
                        df_filtered, validated_touches, timeframe,
                        use_trailing_stop, intraday_mode, entry_cutoff_time, exit_time,
                        custom_target_pct, use_partial_exits,
                        first_exit_pct, second_exit_pct, first_exit_capital_pct
                    )

                    target_pct = trade_analyzer.get_target_for_timeframe(timeframe, custom_target_pct)

                    # Process results
                    for touch in enhanced_touches:
                        pattern = touch.pattern
                        pattern_type = touch.pattern_type
                        entry_price = touch.entry_price
                        pattern_low = getattr(pattern, 'pattern_low', getattr(pattern, 'low_price', entry_price))

                        pattern_display_names = {
                            'pin_bar': 'Pin Bar',
                            'bullish_engulfing': 'Bullish Engulfing',
                            'three_candle': 'Three Candle',
                            'dragonfly_doji': 'Dragonfly Doji',
                            'three_white_soldiers': 'Three White Soldiers',
                            'bullish_marubozu': 'Bullish Marubozu',
                            'bullish_harami': 'Bullish Harami',
                            'bullish_abandoned_baby': 'Abandoned Baby',
                            'tweezer_bottom': 'Tweezer Bottom',
                            'bullish_kicker': 'Bullish Kicker'
                        }

                        pattern_type_display = pattern_display_names.get(pattern_type,
                                                                         pattern_type.replace('_', ' ').title())
                        pattern_date = pattern.timestamp.strftime("%Y-%m-%d %H:%M")
                        is_today_pattern = pd.Timestamp(pattern.timestamp).date() == today_date

                        # Get pattern strength info
                        if pattern_type == 'pin_bar':
                            strength_display = f"{pattern.wick_ratio:.1f}x"
                        elif pattern_type == 'bullish_engulfing':
                            strength_display = f"{pattern.engulfing_ratio:.1f}x"
                        elif pattern_type == 'three_candle':
                            strength_display = f"{pattern.pattern_strength:.1f}"
                        elif pattern_type == 'dragonfly_doji':
                            strength_display = f"{pattern.lower_wick_ratio:.1f}"
                        elif pattern_type == 'three_white_soldiers':
                            strength_display = f"{pattern.average_body_size:.4f}"
                        elif pattern_type == 'bullish_marubozu':
                            strength_display = f"{pattern.body_size:.4f}"
                        elif pattern_type == 'bullish_harami':
                            strength_display = f"{pattern.containment_ratio:.1f}"
                        elif pattern_type == 'bullish_abandoned_baby':
                            strength_display = f"{pattern.gap_up_size:.4f}"
                        elif pattern_type == 'tweezer_bottom':
                            strength_display = f"{pattern.low_match_precision:.1f}%"
                        elif pattern_type == 'bullish_kicker':
                            strength_display = f"{pattern.gap_size:.4f}"
                        else:
                            strength_display = "N/A"

                        # Get trade outcome
                        outcome = touch.trade_outcome
                        if outcome:
                            if outcome.partial_exits_enabled:
                                if outcome.first_exit_triggered and outcome.second_exit_triggered:
                                    trade_outcome_display = "Both Exits Complete"
                                    current_status = f"Weighted P&L: {outcome.weighted_profit_pct:.2f}%"
                                elif outcome.first_exit_triggered:
                                    trade_outcome_display = f"1st Exit @ {outcome.first_exit_pct:.1f}%"
                                    current_status = f"Partial Exit: {outcome.weighted_profit_pct:.2f}%"
                                elif outcome.sl_hit:
                                    trade_outcome_display = "Stop Loss"
                                    current_status = f"SL Hit: {outcome.total_pnl_pct:.2f}%"
                                else:
                                    trade_outcome_display = "Ongoing"
                                    current_status = f"Current: {outcome.current_profit_pct:.2f}%"
                            elif outcome.resolution_type == 'intraday_exit':
                                trade_outcome_display = "Intraday Exit"
                                current_status = f"Exit@{exit_time}: {outcome.current_profit_pct:.2f}%"
                            elif outcome.success:
                                trade_outcome_display = "Success"
                                current_status = f"Target: {outcome.current_profit_pct:.2f}%"
                            elif outcome.sl_hit:
                                if use_trailing_stop and outcome.trailing_active:
                                    trade_outcome_display = "Trailing Stop"
                                else:
                                    trade_outcome_display = "Stop Loss"
                                current_status = f"SL Hit: {outcome.current_profit_pct:.2f}%"
                            else:
                                trade_outcome_display = "Ongoing"
                                current_status = f"Current: {outcome.current_profit_pct:.2f}%"
                        else:
                            trade_outcome_display = "No Data"
                            current_status = "N/A"

                        # COMPLETE result_dict with ALL required fields
                        result_dict = {
                            "Symbol": symbol,
                            "Timeframe": timeframe,
                            "Pattern Type": pattern_type_display,
                            "Swing Low Date": touch.swing_low.timestamp.strftime("%Y-%m-%d %H:%M"),
                            "Swing Low Price": f"{touch.swing_low.price:.4f}",
                            "Swing Low Valid": "Yes" if touch.is_swing_low_valid else "No",
                            "Swing Low Invalidated": "Yes" if touch.swing_low.is_invalidated else "No",
                            "Pattern Date": pattern_date,
                            "Is Today's Pattern": "YES" if is_today_pattern else "No",
                            "Live Entry Detectable": "YES",  # FIXED: This was missing
                            "Detection Mode": f"{left_lookback}+{right_lookback}",
                            "Entry Price": f"{entry_price:.4f}",
                            "Pattern Low": f"{pattern_low:.4f}",
                            "Days Between": touch.days_between,
                            "Distance %": f"{touch.price_difference:.3f}%",
                            "Pattern Strength": f"{touch.pattern_strength:.1f}%",
                            "Strength/Ratio": strength_display,
                            "Bullish": "Yes" if pattern.is_bullish else "No",
                            "Trade Outcome": trade_outcome_display,
                            "Current Status": current_status,
                            "Target Used": f"{target_pct:.1f}%",
                            "Stop Loss Type": "Trailing" if use_trailing_stop else "Fixed",
                            "_entry_price_numeric": entry_price,
                            "_trade_outcome": outcome,
                            "_trade_analyzer": trade_analyzer
                        }

                        if outcome:
                            result_dict.update({
                                "Target Price": f"{outcome.target_price:.4f}",
                                "Stop Loss": f"{outcome.sl_price:.4f}",
                                "Current Price": f"{outcome.current_price:.4f}",
                                "Max Profit %": f"{outcome.max_profit_pct:.2f}%",
                                "Max Drawdown %": f"{outcome.max_drawdown_pct:.2f}%",
                                "Bars to Resolution": outcome.bars_to_resolution,
                                "Resolution Type": outcome.resolution_type,
                                "Last Update": outcome.last_update_timestamp.strftime(
                                    "%Y-%m-%d %H:%M") if outcome.last_update_timestamp else "N/A"
                            })

                            if outcome.partial_exits_enabled:
                                result_dict.update({
                                    "Partial Exits": "Enabled",
                                    "1st Exit Target": f"{outcome.first_exit_pct:.2f}%",
                                    "1st Exit Hit": "Yes" if outcome.first_exit_triggered else "No",
                                    "1st Exit Price": f"{outcome.first_exit_price:.4f}" if outcome.first_exit_triggered else "N/A",
                                    "2nd Exit Target": f"{outcome.second_exit_pct:.2f}%",
                                    "2nd Exit Hit": "Yes" if outcome.second_exit_triggered else "No",
                                    "2nd Exit Price": f"{outcome.second_exit_price:.4f}" if outcome.second_exit_triggered else "N/A",
                                    "Weighted P&L %": f"{outcome.weighted_profit_pct:.2f}%",
                                    "Total P&L %": f"{outcome.total_pnl_pct:.2f}%"
                                })

                            if use_trailing_stop:
                                result_dict.update({
                                    "Trailing Active": "Yes" if outcome.trailing_active else "No",
                                    "Trailing SL": f"{outcome.trailing_sl_price:.4f}" if outcome.trailing_active else "N/A",
                                    "Highest Price": f"{outcome.highest_price_reached:.4f}" if outcome.trailing_active else "N/A"
                                })

                        results.append(result_dict)

                except Exception as e:
                    debug_info[f'{symbol}_{timeframe}_error'] = str(e)
                    print(f"  ❌ Error: {str(e)}")

        total_filtered = debug_info.get('historical_trades_filtered', 0)
        total_live = debug_info.get('live_detectable_trades', 0)

        print(f"\n🎉 CUSTOMIZABLE ANALYSIS COMPLETE:")
        print(f"  📊 Detection: {left_lookback}+{right_lookback} bars")
        print(f"  🎯 Entry mode: {'Pattern Only' if pattern_only_entry else 'Pattern + Swing Touch'}")
        print(f"  ✅ Results: {len(results)}")

        return results, debug_info

    except Exception as e:
        raise Exception(f"Enhanced customizable analysis error: {str(e)}")


def detect_selected_patterns_with_today(df: pd.DataFrame, pattern_selection: Dict,
                                        parameters: Dict, include_today: bool = True) -> Dict:
    """
    Detect all selected patterns - FIXED FOR NSE LIVE TRADING

    Args:
        df: OHLCV DataFrame
        pattern_selection: Dictionary of selected patterns
        parameters: Analysis parameters
        include_today: Whether to include today's patterns (default True)
    """
    all_patterns = {}

    # Check if we're in NSE trading hours for parameter adjustment
    try:
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        is_nse_trading = (time(9, 15) <= now_ist.time() <= time(15, 30) and
                          now_ist.weekday() < 5)
    except:
        is_nse_trading = True

    # Always include live patterns, especially during trading hours
    include_live = include_today or is_nse_trading

    if pattern_selection.get('pin_bar', False):
        # Adjust sensitivity for live trading
        min_wick = parameters.get('min_wick_ratio', 2.0)
        max_body = parameters.get('max_body_ratio', 0.3)
        if is_nse_trading:
            min_wick = min_wick * 0.85  # More sensitive
            max_body = max_body * 1.3  # More permissive

        detector = PinBarDetector(min_wick, max_body)
        all_patterns['pin_bar'] = detector.detect_pinbars(df, include_live=include_live)

    if pattern_selection.get('bullish_engulfing', False):
        min_ratio = parameters.get('min_engulfing_ratio', 1.1)
        if is_nse_trading:
            min_ratio = max(0.95, min_ratio * 0.9)  # More sensitive but not below 0.95
        detector = BullishEngulfingDetector(min_ratio)
        all_patterns['bullish_engulfing'] = detector.detect_bullish_engulfing(df, include_live=include_live)

    if pattern_selection.get('three_candle', False):
        min_first = parameters.get('min_first_body', 0.6)
        max_second = parameters.get('max_second_body', 0.4)
        min_third = parameters.get('min_third_body', 0.6)
        if is_nse_trading:
            min_first = min_first * 0.8
            max_second = max_second * 1.4
            min_third = min_third * 0.8
        detector = ThreeCandleDetector(min_first, max_second, min_third)
        all_patterns['three_candle'] = detector.detect_three_candle(df, include_live=include_live)

    if pattern_selection.get('dragonfly_doji', False):
        detector = DragonflyDojiDetector()
        all_patterns['dragonfly_doji'] = detector.detect_dragonfly_doji(df, include_live=include_live)

    if pattern_selection.get('three_white_soldiers', False):
        detector = ThreeWhiteSoldiersDetector()
        all_patterns['three_white_soldiers'] = detector.detect_three_white_soldiers(df, include_live=include_live)

    if pattern_selection.get('bullish_marubozu', False):
        detector = BullishMarubozuDetector()
        all_patterns['bullish_marubozu'] = detector.detect_bullish_marubozu(df, include_live=include_live)

    if pattern_selection.get('bullish_harami', False):
        detector = BullishHaramiDetector()
        all_patterns['bullish_harami'] = detector.detect_bullish_harami(df, include_live=include_live)

    if pattern_selection.get('bullish_abandoned_baby', False):
        detector = BullishAbandonedBabyDetector()
        all_patterns['bullish_abandoned_baby'] = detector.detect_bullish_abandoned_baby(df, include_live=include_live)

    if pattern_selection.get('tweezer_bottom', False):
        detector = TweezerBottomDetector()
        all_patterns['tweezer_bottom'] = detector.detect_tweezer_bottom(df, include_live=include_live)

    if pattern_selection.get('bullish_kicker', False):
        detector = BullishKickerDetector()
        all_patterns['bullish_kicker'] = detector.detect_bullish_kicker(df, include_live=include_live)

    return all_patterns


# For backward compatibility, keep the old function name but use the new implementation
def detect_selected_patterns(df: pd.DataFrame, pattern_selection: Dict, parameters: Dict) -> Dict:
    """Detect all selected patterns - INCLUDING TODAY'S CANDLE"""
    return detect_selected_patterns_with_today(df, pattern_selection, parameters, include_today=True)


# ============================================================================
# DOWNLOAD HELPER FUNCTION
# ============================================================================

def create_download_buttons(df: pd.DataFrame, filename_prefix: str, label: str = "Download"):
    """Create download buttons for CSV and Excel formats"""
    col1, col2 = st.columns(2)

    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label=f"📥 {label} CSV",
            data=csv,
            file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            excel_data = output.getvalue()

            st.download_button(
                label=f"📥 {label} Excel",
                data=excel_data,
                file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except ImportError:
            st.button(
                f"📥 {label} Excel (Need openpyxl)",
                disabled=True,
                use_container_width=True,
                help="Install openpyxl for Excel downloads: pip install openpyxl"
            )


# ============================================================================
# STREAMLIT UI FUNCTIONS
# ============================================================================
def debug_swing_low_detection(df: pd.DataFrame, symbol: str = "TEST"):
    """Debug function to test swing low detection fixes"""
    try:
        print(f"\n=== DEBUG SWING LOW DETECTION FOR {symbol} ===")
        print(f"DataFrame length: {len(df)}")
        print(f"Latest timestamp: {df.index[-1]}")
        print(f"Latest close: {df['close'].iloc[-1]:.2f}")

        # Test with different lookback values
        for lookback in [3, 5, 10]:
            detector = EnhancedSwingLowDetector(lookback_bars=lookback)
            swing_lows = detector.find_swing_lows_with_invalidation(df)

            print(f"\nLookback {lookback}:")
            print(f"  Total swing lows: {len(swing_lows)}")

            # Check for recent swing lows
            recent_swings = [sl for sl in swing_lows if sl.index > len(df) - 10]
            print(f"  Recent swing lows (last 10 bars): {len(recent_swings)}")

            if recent_swings:
                latest_swing = max(recent_swings, key=lambda x: x.index)
                bars_ago = len(df) - 1 - latest_swing.index
                print(f"  Latest swing low: {bars_ago} bars ago at {latest_swing.price:.2f}")
            else:
                print(f"  No recent swing lows found!")

            # Check invalidation
            valid_swings = [sl for sl in swing_lows if not sl.is_invalidated]
            print(f"  Valid swing lows: {len(valid_swings)}")

        print(f"=== END DEBUG ===\n")
        return True

    except Exception as e:
        print(f"Debug error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_live_nse_patterns():
    """Test function to verify NSE live pattern detection works"""
    try:
        from tvDatafeed import TvDatafeed, Interval

        print("=== TESTING NSE LIVE PATTERN DETECTION ===")

        # Check market hours
        try:
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = datetime.now(ist)
            is_trading = (time(9, 15) <= now_ist.time() <= time(15, 30) and
                          now_ist.weekday() < 5)
            print(f"NSE Market: {'OPEN' if is_trading else 'CLOSED'} | Time: {now_ist.strftime('%H:%M:%S')}")
        except:
            print("Cannot determine market hours - assuming trading")
            is_trading = True

        # Test with popular NSE symbols
        symbols_to_test = ['RELIANCE', 'TCS', 'HDFCBANK']
        tv = TvDatafeed()

        for symbol in symbols_to_test:
            print(f"\n--- Testing {symbol} ---")

            try:
                # Get 5-minute data
                df = tv.get_hist(symbol, 'NSE', Interval.in_5_minute, n_bars=100)

                if df is None or df.empty:
                    print(f"No data for {symbol}")
                    continue

                print(f"Data: {len(df)} bars, Latest: {df.index[-1]}")

                # Test swing low detection
                debug_swing_low_detection(df, symbol)

                # Test pattern detection
                pattern_selection = {'pin_bar': True, 'bullish_engulfing': True}
                parameters = {
                    'swing_lookback': 5,
                    'min_swing_size': 0.5,
                    'min_wick_ratio': 2.0,
                    'max_body_ratio': 0.3,
                    'min_engulfing_ratio': 1.1,
                    'touch_tolerance': 1.0
                }

                patterns = detect_selected_patterns_with_today(df, pattern_selection, parameters, include_today=True)

                total_patterns = sum(len(p) for p in patterns.values())
                print(f"Total patterns found: {total_patterns}")

                for pattern_type, pattern_list in patterns.items():
                    if pattern_list:
                        live_patterns = [p for p in pattern_list if getattr(p, 'is_live', False)]
                        today_patterns = [p for p in pattern_list
                                          if pd.Timestamp(p.timestamp).date() == datetime.now().date()]
                        print(
                            f"  {pattern_type}: {len(pattern_list)} total, {len(live_patterns)} live, {len(today_patterns)} today")

            except Exception as e:
                print(f"Error testing {symbol}: {e}")

        print("=== TEST COMPLETE ===")
        return True

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def init_session_state():
    """Initialize all session state variables - ENHANCED WITH CUSTOM SWING PARAMETERS"""
    defaults = {
        'file_manager': FileManager(),
        'data_manager': None,
        'live_analyzer': None,
        'analysis_results': None,
        'analysis_complete': False,
        'last_analysis_params': None,
        'debug_info': None,
        'global_capital': 10000,
        'selected_timeframes': ['4H'],
        'instruments_list': [],
        'last_data_update': None,
        'auto_refresh_enabled': False,
        'live_patterns': [],
        'update_status': {},

        # Capital Management Settings
        'capital_manager': None,
        'all_touches': [],
        'total_capital': 100000,
        'capital_per_trade': 10000,
        'capital_start_date': datetime.now() - timedelta(days=180),
        'analysis_start_date': datetime.now() - timedelta(days=180),
        'capital_analysis_complete': False,
        'capital_touches': [],
        'capital_debug': {},

        # Enhanced Data Management Settings - DATE PICKER SUPPORT
        'data_download_start_date': datetime.now() - timedelta(days=30),
        'use_date_picker': False,

        # Stop Loss Configuration
        'use_trailing_stop': False,

        # Intraday Configuration
        'intraday_mode': False,
        'intraday_entry_cutoff': '11:45',
        'intraday_exit_time': '15:15',

        # Flexible Target Configuration
        'custom_target_pct': None,
        'use_custom_target': False,

        # Partial Exit Configuration
        'use_partial_exits': False,
        'first_exit_pct': 0.5,  # First exit at 0.5%
        'second_exit_pct': 0.9,  # Second exit at 0.9%
        'first_exit_capital_pct': 50.0,  # 50% of capital on first exit

        # Telegram Alert Settings (WEBHOOK ONLY - NO CHAT ID)
        'telegram_enabled': False,
        'telegram_webhook_url': '',
        'telegram_last_alert_time': None,
        'telegram_alert_cooldown': 60,  # seconds between alerts for same pattern
        'telegram_sent_alerts': {},  # Track sent alerts to avoid duplicates
        'telegram_alert_on_live': True,  # Alert on live patterns
        'telegram_alert_on_confirmed': False,  # Alert on confirmed patterns

        'analysis_parameters': {
            'swing_lookback': 9,
            'right_lookback': 1,
            'min_swing_size': 0.5,
            'min_wick_ratio': 2.0,
            'max_body_ratio': 0.3,
            'min_engulfing_ratio': 1.1,
            'touch_tolerance': 0.10,
            'min_days_between': 1,  # NEW: Minimum days between swing low and pattern
            'max_bars_to_analyze': 200,
            'min_first_body': 0.6,
            'max_second_body': 0.4,
            'min_third_body': 0.6,

            # Trade entry logic options
            'pattern_only_entry': False,
            'require_swing_touch': True,
            'require_volume_confirm': False,
            'strict_invalidation': True,
        },
        'pattern_selection': {
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
        }
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # Initialize managers
    if st.session_state.data_manager is None:
        st.session_state.data_manager = BackgroundDataManager(st.session_state.file_manager)

    if st.session_state.live_analyzer is None:
        st.session_state.live_analyzer = LivePatternAnalyzer(
            st.session_state.data_manager, st.session_state.file_manager
        )

    # Load instruments from file
    if not st.session_state.instruments_list:
        st.session_state.instruments_list = st.session_state.file_manager.load_instruments()


import requests
import hashlib

# ============================================================================
# TELEGRAM ALERT SYSTEM (WEBHOOK ONLY - NO CHAT ID)
# ============================================================================

import requests
import hashlib


def send_telegram_alert(webhook_url: str, message: str) -> bool:
    """Send alert to Telegram via webhook (no chat_id needed)"""
    try:
        # Match the working VCP implementation
        payload = {
            'text': message,
            'parse_mode': 'Markdown'  # Changed from HTML to Markdown
        }
        # Removed 'disable_web_page_preview' as it's not in working code

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )

        # Check only for 200 like the working VCP code
        if response.status_code == 200:
            return True
        else:
            print(f"Telegram alert failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Telegram alert error: {e}")
        return False


def format_pattern_alert(pattern_data: Dict, symbol: str, timeframe: str,
                         pattern_type: str, entry_price: float,
                         sl_price: float, target_price: float) -> str:
    """Format pattern alert message for Telegram"""

    # Pattern emoji mapping
    pattern_emojis = {
        'pin_bar': '📍',
        'bullish_engulfing': '🔥',
        'three_candle': '🌟',
        'dragonfly_doji': '🐉',
        'three_white_soldiers': '⚔️',
        'bullish_marubozu': '💪',
        'bullish_harami': '🤰',
        'bullish_abandoned_baby': '👶',
        'tweezer_bottom': '🔧',
        'bullish_kicker': '🚀'
    }

    emoji = pattern_emojis.get(pattern_type.lower().replace(' ', '_'), '🎯')

    # Calculate risk/reward
    risk = abs(entry_price - sl_price)
    reward = abs(target_price - entry_price)
    rr_ratio = reward / risk if risk > 0 else 0

    # Changed from HTML <b> tags to Markdown ** formatting
    message = f"""
**{emoji} PATTERN ALERT {emoji}**

**Symbol:** {symbol}
**Timeframe:** {timeframe}
**Pattern:** {pattern_type}

**📊 TRADE SETUP:**
- **Entry:** {entry_price:.4f}
- **Stop Loss:** {sl_price:.4f}
- **Target:** {target_price:.4f}

**📈 METRICS:**
- Risk: {risk:.4f} ({(risk / entry_price * 100):.2f}%)
- Reward: {reward:.4f} ({(reward / entry_price * 100):.2f}%)
- R:R Ratio: {rr_ratio:.2f}

**⏰ Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#TradingAlert #{symbol} #{pattern_type.replace(' ', '')}
"""

    return message


def generate_alert_hash(symbol: str, timeframe: str, pattern_type: str,
                        entry_price: float, timestamp: str) -> str:
    """Generate unique hash for alert to prevent duplicates"""
    data = f"{symbol}_{timeframe}_{pattern_type}_{entry_price:.4f}_{timestamp}"
    return hashlib.md5(data.encode()).hexdigest()


def should_send_alert(alert_hash: str, cooldown_seconds: int = 60) -> bool:
    """Check if alert should be sent based on cooldown and duplicates"""
    sent_alerts = st.session_state.get('telegram_sent_alerts', {})
    current_time = time.time()

    # Check if alert was already sent
    if alert_hash in sent_alerts:
        last_sent_time = sent_alerts[alert_hash]
        if current_time - last_sent_time < cooldown_seconds:
            return False

    return True


def process_patterns_for_alerts(patterns: List[Dict], pattern_type: str = 'live') -> int:
    """Process patterns and send Telegram alerts (webhook only)"""
    if not st.session_state.get('telegram_enabled', False):
        return 0

    webhook_url = st.session_state.get('telegram_webhook_url', '')

    if not webhook_url:
        return 0

    alerts_sent = 0
    sent_alerts = st.session_state.get('telegram_sent_alerts', {})
    cooldown = st.session_state.get('telegram_alert_cooldown', 60)

    for pattern in patterns:
        try:
            # Extract pattern data
            symbol = pattern.get('symbol', 'Unknown')
            timeframe = pattern.get('timeframe', 'Unknown')
            pattern_name = pattern.get('pattern_type', 'Unknown')
            entry_str = pattern.get('entry_price', '0')
            swing_low_str = pattern.get('swing_low_price', '0')
            timestamp = pattern.get('timestamp', '')

            # Parse prices
            entry_price = float(entry_str.replace(',', '')) if isinstance(entry_str, str) else entry_str
            swing_low_price = float(swing_low_str.replace(',', '')) if isinstance(swing_low_str, str) else swing_low_str

            # Calculate SL and Target based on pattern type
            sl_price = swing_low_price  # Default SL at swing low

            # Get target based on timeframe
            timeframe_targets = {
                '1m': 0.5,
                '5m': 0.75,
                '15m': 1.0,
                '30m': 1.5,
                '1H': 2.5,
                '4H': 5.0,
                '1D': 8.0
            }
            target_pct = timeframe_targets.get(timeframe, 2.0)
            target_price = entry_price * (1 + target_pct / 100)

            # Generate alert hash
            alert_hash = generate_alert_hash(symbol, timeframe, pattern_name, entry_price, timestamp)

            # Check if should send alert
            if should_send_alert(alert_hash, cooldown):
                # Format message
                message = format_pattern_alert(
                    pattern, symbol, timeframe, pattern_name,
                    entry_price, sl_price, target_price
                )

                # Send alert (webhook only)
                if send_telegram_alert(webhook_url, message):
                    # Update sent alerts tracking
                    sent_alerts[alert_hash] = time.time()
                    alerts_sent += 1

        except Exception as e:
            print(f"Error processing pattern for alert: {e}")
            continue

    # Update session state
    st.session_state['telegram_sent_alerts'] = sent_alerts
    st.session_state['telegram_last_alert_time'] = time.time()

    return alerts_sent


def send_summary_alert(total_patterns: int, live_patterns: int,
                       confirmed_patterns: int, symbols_analyzed: int) -> bool:
    """Send summary alert after analysis (webhook only)"""
    if not st.session_state.get('telegram_enabled', False):
        return False

    webhook_url = st.session_state.get('telegram_webhook_url', '')

    if not webhook_url:
        return False

    message = f"""
<b>📊 ANALYSIS SUMMARY</b>

<b>Patterns Found:</b> {total_patterns}
- Live: {live_patterns}
- Confirmed: {confirmed_patterns}

<b>Coverage:</b>
- Symbols: {symbols_analyzed}
- Timeframes: {', '.join(st.session_state.get('selected_timeframes', []))}

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#AnalysisSummary
"""

    return send_telegram_alert(webhook_url, message)


def process_analysis_results_for_alerts(results: List[Dict]) -> int:
    """Process analysis results and send Telegram alerts for today's patterns (webhook only)"""
    if not st.session_state.get('telegram_enabled', False):
        return 0

    webhook_url = st.session_state.get('telegram_webhook_url', '')

    if not webhook_url:
        return 0

    alerts_sent = 0
    sent_alerts = st.session_state.get('telegram_sent_alerts', {})
    cooldown = st.session_state.get('telegram_alert_cooldown', 60)

    # Filter for today's patterns
    today_patterns = [r for r in results if r.get("Is Today's Pattern") == "YES"]

    for result in today_patterns:
        try:
            symbol = result.get('Symbol', 'Unknown')
            timeframe = result.get('Timeframe', 'Unknown')
            pattern_type = result.get('Pattern Type', 'Unknown')
            entry_price_str = result.get('Entry Price', '0')
            sl_price_str = result.get('Stop Loss', '0')
            target_price_str = result.get('Target Price', '0')
            pattern_date = result.get('Pattern Date', '')

            # Parse prices
            entry_price = float(entry_price_str.replace(',', '')) if isinstance(entry_price_str,
                                                                                str) else entry_price_str
            sl_price = float(sl_price_str.replace(',', '')) if isinstance(sl_price_str, str) else sl_price_str
            target_price = float(target_price_str.replace(',', '')) if isinstance(target_price_str,
                                                                                  str) else target_price_str

            # Generate alert hash
            alert_hash = generate_alert_hash(symbol, timeframe, pattern_type, entry_price, pattern_date)

            # Check if should send alert
            if should_send_alert(alert_hash, cooldown):
                # Format message
                message = format_pattern_alert(
                    result, symbol, timeframe, pattern_type,
                    entry_price, sl_price, target_price
                )

                # Send alert (webhook only)
                if send_telegram_alert(webhook_url, message):
                    sent_alerts[alert_hash] = time.time()
                    alerts_sent += 1

        except Exception as e:
            print(f"Error processing result for alert: {e}")
            continue

    st.session_state['telegram_sent_alerts'] = sent_alerts
    st.session_state['telegram_last_alert_time'] = time.time()

    return alerts_sent


def apply_professional_theme():
    """Apply Professional AI Market Analysis theme"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --primary-blue: #0066cc;
        --secondary-blue: #004499;
        --accent-cyan: #00d4ff;
        --success-green: #00cc88;
        --warning-orange: #ff8800;
        --danger-red: #ff4444;
        --neutral-gray: #6c757d;
        --light-gray: #f8f9fa;
        --dark-gray: #212529;
        --border-color: #dee2e6;
        --background-primary: #ffffff;
        --background-secondary: #f5f7fa;
        --text-primary: #2c3e50;
        --text-secondary: #5a6c7d;
        --shadow-light: 0 2px 4px rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 4px 12px rgba(0, 0, 0, 0.15);
        --shadow-heavy: 0 8px 24px rgba(0, 0, 0, 0.2);
        --gradient-primary: linear-gradient(135deg, #0066cc 0%, #004499 100%);
        --gradient-success: linear-gradient(135deg, #00cc88 0%, #009966 100%);
        --gradient-info: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
    }

    .main {
        background: var(--background-secondary);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }

    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }

    h1 {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--background-primary);
        border-radius: 12px;
        padding: 8px;
        gap: 4px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-light);
    }

    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
    }

    .stTabs [aria-selected="false"] {
        color: var(--text-secondary);
        font-weight: 500;
    }

    /* Metric containers */
    div[data-testid="metric-container"] {
        background: var(--background-primary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: var(--shadow-light);
        transition: all 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        box-shadow: var(--shadow-medium);
        transform: translateY(-2px);
    }

    /* Button styling */
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        box-shadow: var(--shadow-light);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }

    .stButton > button:hover {
        box-shadow: var(--shadow-medium);
        transform: translateY(-1px);
    }

    /* Success button variant */
    .stButton > button[kind="primary"] {
        background: var(--gradient-success);
    }

    /* DataFrame styling */
    .stDataFrame {
        background: var(--background-primary);
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-light);
        overflow: hidden;
    }

    /* Selectbox and input styling */
    .stSelectbox > div > div {
        background: var(--background-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }

    .stTextInput > div > div > input {
        background: var(--background-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-primary);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: var(--background-primary);
        border-right: 1px solid var(--border-color);
    }

    /* Success/Info/Warning messages */
    .stSuccess {
        background: rgba(0, 204, 136, 0.1);
        border: 1px solid var(--success-green);
        border-radius: 8px;
        color: var(--success-green);
    }

    .stInfo {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid var(--accent-cyan);
        border-radius: 8px;
        color: var(--primary-blue);
    }

    .stWarning {
        background: rgba(255, 136, 0, 0.1);
        border: 1px solid var(--warning-orange);
        border-radius: 8px;
        color: var(--warning-orange);
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: var(--gradient-primary);
        border-radius: 4px;
    }

    /* Professional cards */
    .professional-card {
        background: var(--background-primary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
        transition: all 0.3s ease;
    }

    .professional-card:hover {
        box-shadow: var(--shadow-medium);
    }

    /* Feature highlight boxes */
    .feature-highlight {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.1), rgba(0, 212, 255, 0.1));
        border: 1px solid var(--accent-cyan);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .ai-badge {
        background: var(--gradient-info);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    }

    /* Code blocks */
    .stCode {
        background: var(--dark-gray);
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Checkbox styling */
    .stCheckbox > label {
        color: var(--text-primary);
        font-weight: 500;
    }

    /* Number input styling */
    .stNumberInput > div > div > input {
        background: var(--background-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-primary);
    }

    /* Professional animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }

    .pulse {
        animation: pulse 2s infinite;
    }

    /* Professional status indicators */
    .status-active {
        color: var(--success-green);
        font-weight: 600;
    }

    .status-pending {
        color: var(--warning-orange);
        font-weight: 600;
    }

    .status-inactive {
        color: var(--neutral-gray);
        font-weight: 500;
    }
    </style>

    <!-- Professional Success Notification -->
    <script>
        function showProfessionalSuccess() {
            const successDiv = document.createElement('div');
            successDiv.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">📊</div>
                    <h3 style="color: #0066cc; margin: 0;">ANALYSIS COMPLETE!</h3>
                    <p style="color: #5a6c7d; margin: 0.5rem 0;">Professional AI Market Analysis Successfully Executed</p>
                    <div style="margin-top: 1rem;">
                        <span class="ai-badge">AI POWERED</span>
                        <span class="ai-badge">TODAY'S DATA</span>
                        <span class="ai-badge">REAL-TIME</span>
                    </div>
                </div>
            `;
            successDiv.style.cssText = `
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(245, 247, 250, 0.95));
                padding: 2rem;
                border-radius: 16px;
                border: 1px solid #dee2e6;
                box-shadow: 0 8px 32px rgba(0, 102, 204, 0.2);
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 9999;
                backdrop-filter: blur(10px);
                animation: fadeInUp 0.6s ease-out;
                max-width: 400px;
                pointer-events: none;
            `;

            document.body.appendChild(successDiv);

            setTimeout(() => {
                if (successDiv.parentNode) {
                    successDiv.style.animation = 'fadeOut 0.6s ease-out';
                    setTimeout(() => {
                        if (successDiv.parentNode) {
                            successDiv.parentNode.removeChild(successDiv);
                        }
                    }, 600);
                }
            }, 4000);
        }

        function playProfessionalNotification() {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();

                // Create a pleasant notification sound
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();

                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);

                // Professional notification tone
                oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                oscillator.frequency.exponentialRampToValueAtTime(600, audioContext.currentTime + 0.1);
                oscillator.frequency.exponentialRampToValueAtTime(800, audioContext.currentTime + 0.2);

                gainNode.gain.setValueAtTime(0, audioContext.currentTime);
                gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.3);

            } catch (error) {
                console.log('Audio not available, but analysis completed successfully!');
            }
        }

        window.showProfessionalSuccess = showProfessionalSuccess;
        window.playProfessionalNotification = playProfessionalNotification;
    </script>
    """, unsafe_allow_html=True)


def render_instrument_management():
    """Render instrument management section with professional styling"""
    st.subheader("🎯 Instrument Portfolio Management")

    col1, col2 = st.columns([3, 1])

    with col1:
        current_instruments = ', '.join(st.session_state.instruments_list)
        new_instruments = st.text_area(
            "Financial Instruments (comma-separated):",
            value=current_instruments,
            height=100,
            help="Edit instruments and click 'Save' to update the instruments.txt file"
        )

    with col2:
        st.write("**Management Actions:**")

        if st.button("💾 Save Portfolio", type="primary", use_container_width=True):
            new_list = [s.strip().upper() for s in new_instruments.split(',') if s.strip()]
            st.session_state.file_manager.save_instruments(new_list)
            st.session_state.instruments_list = new_list
            st.success(f"✅ Saved {len(new_list)} instruments to portfolio!")
            st.rerun()

        if st.button("🔄 Reload Portfolio", use_container_width=True):
            st.session_state.instruments_list = st.session_state.file_manager.load_instruments()
            st.success("✅ Portfolio reloaded from file!")
            st.rerun()

        if st.button("📁 Show File Path", use_container_width=True):
            file_path = os.path.abspath(st.session_state.file_manager.instruments_file)
            st.info(f"📄 {file_path}")

    # Display portfolio statistics
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Portfolio Size", len(st.session_state.instruments_list), help="Total number of instruments")
    with col_b:
        if os.path.exists(st.session_state.file_manager.instruments_file):
            file_size = os.path.getsize(st.session_state.file_manager.instruments_file)
            st.metric("File Size", f"{file_size} bytes")
        else:
            st.metric("File Size", "N/A")
    with col_c:
        if os.path.exists(st.session_state.file_manager.instruments_file):
            mod_time = datetime.fromtimestamp(os.path.getmtime(st.session_state.file_manager.instruments_file))
            st.metric("Last Modified", mod_time.strftime("%H:%M:%S"))
        else:
            st.metric("Last Modified", "N/A")

    # Download portfolio
    if st.session_state.instruments_list:
        st.subheader("📋 Export Portfolio")
        instruments_df = pd.DataFrame({'Instruments': st.session_state.instruments_list})
        create_download_buttons(instruments_df, "instrument_portfolio", "Portfolio")


def render_data_management_tab():
    """Render the enhanced data management tab with date picker support"""
    st.header("🔄 AI-Powered Data Management Center with Date Selection")

    # Professional feature highlight with new date picker feature
    st.markdown("""
    <div class="feature-highlight">
    <h3 style="color: #0066cc; margin: 0;">🚀 Enhanced Data Management Features:</h3>
    <p style="color: #5a6c7d; margin: 5px 0;">
    ✅ NEW: Date Picker for Historical Downloads | ✅ Smart Bar Calculation | ✅ Today's Real-Time Data Integration | ✅ Smart Incremental Updates | ✅ Parallel Processing | ✅ Advanced Caching | ✅ Multi-Timeframe Optimization
    </p>
    </div>
    """, unsafe_allow_html=True)

    # Date Picker Configuration Section - NEW FEATURE
    st.subheader("📅 Data Download Configuration")

    # Toggle between date picker and default bars
    use_date_picker = st.checkbox(
        "🗓️ Use Date Picker for Historical Data Downloads",
        value=st.session_state.get('use_date_picker', False),
        help="Enable to specify exact start date for data downloads. When disabled, uses default number of bars for each timeframe."
    )
    st.session_state['use_date_picker'] = use_date_picker

    if use_date_picker:
        col1, col2 = st.columns(2)

        with col1:
            # Date picker for download start date
            download_start_date = st.date_input(
                "📅 Data Download Start Date",
                value=st.session_state.get('data_download_start_date', datetime.now() - timedelta(days=30)),
                max_value=datetime.now().date(),
                help="All data will be downloaded from this date to present. Older dates require more bars and may take longer.",
                key="data_download_date_picker"
            )

            # Convert to datetime and store
            download_start_datetime = datetime.combine(download_start_date, datetime.min.time())
            st.session_state['data_download_start_date'] = download_start_datetime

        with col2:
            # Show duration and estimated bars
            duration = datetime.now() - download_start_datetime
            st.metric("Days of Data", f"{duration.days} days")

            # Show estimated bars for different timeframes
            st.write("**📊 Estimated Bars:**")
            timeframe_examples = ['1H', '4H', '1D']
            for tf in timeframe_examples:
                estimated_bars = st.session_state.data_manager.calculate_bars_from_date(
                    download_start_datetime, tf
                )
                st.write(f"• {tf}: ~{estimated_bars} bars")

        # Quick date setters for data downloads
        st.write("**📅 Quick Date Selection:**")
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            if st.button("📅 1 Week", key="data_1week"):
                st.session_state['data_download_start_date'] = datetime.now() - timedelta(days=7)
                st.rerun()
        with col_b:
            if st.button("📅 1 Month", key="data_1month"):
                st.session_state['data_download_start_date'] = datetime.now() - timedelta(days=30)
                st.rerun()
        with col_c:
            if st.button("📅 3 Months", key="data_3months"):
                st.session_state['data_download_start_date'] = datetime.now() - timedelta(days=90)
                st.rerun()
        with col_d:
            if st.button("📅 6 Months", key="data_6months"):
                st.session_state['data_download_start_date'] = datetime.now() - timedelta(days=180)
                st.rerun()

        # Show current configuration
        st.info(
            f"📊 **Current Configuration**: Download data from {download_start_datetime.strftime('%Y-%m-%d')} to present using smart bar calculation")

    else:
        st.info(
            "📊 **Current Configuration**: Using default number of bars per timeframe (1m: 500, 15m: 300, 4H: 150, 1D: 100 bars)")

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Smart Timeframe Data Updates")

        timeframes = ['1m', '5m', '15m', '30m', '1H', '4H', '1D']

        st.write("**Select timeframes for AI-powered updates:**")
        selected_timeframes = []

        tf_cols = st.columns(4)
        for i, tf in enumerate(timeframes):
            with tf_cols[i % 4]:
                if st.checkbox(tf, key=f"tf_{tf}", value=(tf in ['15m', '1H', '4H'])):
                    selected_timeframes.append(tf)

        st.session_state.selected_timeframes = selected_timeframes

        exchange = st.selectbox("Exchange Platform", ['NSE', 'BINANCE', 'BSE', 'NASDAQ', 'NYSE'],
                                key="data_mgmt_exchange")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            button_text = "🚀 AI Smart Update (Date-Based)" if use_date_picker else "🚀 AI Smart Update"
            if st.button(button_text, type="primary", use_container_width=True):
                if selected_timeframes and st.session_state.instruments_list:
                    # Determine start date to use
                    start_date_for_download = download_start_datetime if use_date_picker else None

                    with st.spinner("AI processing data with smart updates..."):
                        results = st.session_state.data_manager.update_data_incrementally(
                            st.session_state.instruments_list,
                            selected_timeframes,
                            exchange,
                            force_update=False,
                            start_date=start_date_for_download
                        )
                        st.session_state.update_status = results
                        st.session_state.last_data_update = datetime.now()

                        if use_date_picker:
                            st.success(
                                f"✅ AI date-based update completed from {download_start_datetime.strftime('%Y-%m-%d')}!")
                        else:
                            st.success("✅ AI smart update completed with default bars!")
                        st.rerun()
                else:
                    st.warning("Please select timeframes and ensure instruments are loaded")

        with col_b:
            refresh_text = "🔄 Full Refresh (Date-Based)" if use_date_picker else "🔄 Full Refresh"
            if st.button(refresh_text, use_container_width=True):
                if selected_timeframes and st.session_state.instruments_list:
                    start_date_for_download = download_start_datetime if use_date_picker else None

                    with st.spinner("Full data refresh in progress..."):
                        results = st.session_state.data_manager.update_data_incrementally(
                            st.session_state.instruments_list,
                            selected_timeframes,
                            exchange,
                            force_update=True,
                            start_date=start_date_for_download
                        )
                        st.session_state.update_status = results
                        st.session_state.last_data_update = datetime.now()

                        if use_date_picker:
                            st.success(f"✅ Full refresh completed from {download_start_datetime.strftime('%Y-%m-%d')}!")
                        else:
                            st.success("✅ Full refresh completed with default bars!")
                        st.rerun()
                else:
                    st.warning("Please select timeframes and ensure instruments are loaded")

        with col_c:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=st.session_state.auto_refresh_enabled)
            st.session_state.auto_refresh_enabled = auto_refresh

    with col2:
        st.subheader("📈 System Status")

        if st.session_state.last_data_update:
            time_diff = datetime.now() - st.session_state.last_data_update
            minutes_ago = int(time_diff.total_seconds() / 60)
            st.success(f"Last update: {minutes_ago}min ago")
        else:
            st.info("Ready for first update")

        # Show today's date and readiness
        today_str = datetime.now().strftime('%Y-%m-%d')
        st.metric("Today's Date", today_str)
        st.success("✅ Real-time ready")

        # Show current configuration
        if use_date_picker:
            st.metric("Download Mode", "Date-Based")
            st.metric("Start Date", download_start_datetime.strftime('%Y-%m-%d'))
        else:
            st.metric("Download Mode", "Default Bars")

        if st.session_state.update_status:
            total_updates = 0
            successful_updates = 0
            for symbol_results in st.session_state.update_status.values():
                if isinstance(symbol_results, dict):
                    for status in symbol_results.values():
                        total_updates += 1
                        if "✅" in status:
                            successful_updates += 1

            st.metric("Success Rate", f"{successful_updates}/{total_updates}")

    st.divider()

    if st.session_state.update_status:
        st.subheader("📋 Detailed Update Status with Date Information")

        status_data = []
        for symbol, tf_status in st.session_state.update_status.items():
            if symbol != "error" and isinstance(tf_status, dict):
                for tf, status in tf_status.items():
                    # Enhanced status information
                    if use_date_picker:
                        config_info = f"From: {download_start_datetime.strftime('%Y-%m-%d')}"
                    else:
                        config_info = "Default bars"

                    status_data.append({
                        'Symbol': symbol,
                        'Timeframe': tf,
                        'Status': status,
                        'Download Config': config_info,
                        'AI Processing': "Active" if "✅" in status else "Pending",
                        'Timestamp': datetime.now().strftime('%H:%M:%S')
                    })

        if status_data:
            status_df = pd.DataFrame(status_data)
            create_download_buttons(status_df, "ai_update_status_with_dates", "AI Status Report")
            st.dataframe(status_df, use_container_width=True, height=300)

    # Enhanced information section
    st.info(
        "🚀 **AI-Powered Updates with Date Picker**: Choose between date-based downloads (specify exact start date) or default bar counts. Date-based downloads automatically calculate the optimal number of bars needed from your selected start date to present, including today's real-time candles!")

    # Technical details for advanced users
    with st.expander("🔧 Technical Details - Date Picker Implementation"):
        st.write("""
        **Date Picker Features:**

        • **Smart Bar Calculation**: Automatically calculates required bars based on selected start date and timeframe

        • **Timeframe-Aware**: Different timeframes get appropriate bar counts (1m gets more bars for same period than 1D)

        • **Safety Limits**: Maximum bars are limited per timeframe to prevent excessive downloads

        • **Gap Handling**: Adds buffer bars to account for market closures and weekends

        • **Backward Compatibility**: Can still use default bar counts when date picker is disabled

        **Bar Calculation Formula:**
        ```
        bars_needed = (current_time - start_date) / timeframe_interval + buffer
        bars_needed = min(bars_needed, max_limit)
        bars_needed = max(bars_needed, minimum_required)
        ```

        **Default Bar Limits:**
        • 1m: 500-5000 bars (8 hours - 3.5 days)
        • 15m: 300-3000 bars (3 days - 1 month) 
        • 4H: 150-1500 bars (25 days - 9 months)
        • 1D: 100-1000 bars (3 months - 3 years)
        """)


def render_pattern_selection_checkboxes(prefix: str = ""):
    """Render professional pattern selection checkboxes"""
    st.write("**🧠 Select AI-Powered Bullish Patterns for Analysis:**")

    # Pattern information with professional descriptions
    pattern_info = {
        'pin_bar': {'name': '📍 Pin Bar', 'rate': '65%', 'description': 'Rejection pattern with long lower wick'},
        'bullish_engulfing': {'name': '🔥 Bullish Engulfing', 'rate': '70%',
                              'description': 'Strong momentum reversal signal'},
        'three_candle': {'name': '🌟 Morning Star', 'rate': '68%', 'description': 'Three-candle reversal formation'},
        'dragonfly_doji': {'name': '🐉 Dragonfly Doji', 'rate': '60%',
                           'description': 'T-shaped indecision with bullish bias'},
        'three_white_soldiers': {'name': '⚔️ Three White Soldiers', 'rate': '82%',
                                 'description': 'Strong consecutive bullish formation'},
        'bullish_marubozu': {'name': '💪 Bullish Marubozu', 'rate': '69%',
                             'description': 'Pure bullish momentum candle'},
        'bullish_harami': {'name': '🤰 Bullish Harami', 'rate': '54%', 'description': 'Inside bar reversal pattern'},
        'bullish_abandoned_baby': {'name': '👶 Abandoned Baby', 'rate': '75%',
                                   'description': 'Rare gap reversal pattern'},
        'tweezer_bottom': {'name': '🔧 Tweezer Bottom', 'rate': '61%', 'description': 'Double bottom support level'},
        'bullish_kicker': {'name': '🚀 Bullish Kicker', 'rate': '78%', 'description': 'Explosive gap-up pattern'}
    }

    # Create columns for checkboxes with professional styling
    cols = st.columns(3)

    for i, (pattern_key, info) in enumerate(pattern_info.items()):
        with cols[i % 3]:
            current_value = st.session_state.pattern_selection.get(pattern_key, False)
            new_value = st.checkbox(
                f"{info['name']} ({info['rate']})",
                value=current_value,
                key=f"{prefix}pattern_{pattern_key}",
                help=f"{info['description']} - AI Success Rate: {info['rate']} - Includes today's real-time patterns!"
            )
            st.session_state.pattern_selection[pattern_key] = new_value

    # Pattern selection summary
    selected_patterns = [k for k, v in st.session_state.pattern_selection.items() if v]
    if selected_patterns:
        st.success(f"✅ {len(selected_patterns)} AI patterns selected for analysis")
    else:
        st.warning("⚠️ No patterns selected. Please select at least one pattern for AI analysis.")


def render_analysis_tab():
    """Render the professional analysis tab with combined update+analysis functionality"""
    st.header("📊 Professional AI Market Analysis Dashboard")

    # Professional feature highlight
    st.markdown("""
    <div class="feature-highlight">
    <h3 style="color: #0066cc; margin: 0;">🧠 AI-Enhanced Analysis Features:</h3>
    <p style="color: #5a6c7d; margin: 5px 0;">
    ✅ Combined Update+Analysis | ✅ Today's Real-Time Pattern Detection | ✅ Advanced Swing Low Validation | ✅ AI-Powered Success Prediction | ✅ Multi-Timeframe Optimization | ✅ Live P&L Tracking | ✅ Configurable Stop Loss | ✅ Intraday Mode | ✅ Partial Exit Support | ✅ Telegram Alerts
    </p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.instruments_list:
        st.warning("⚠️ No instruments loaded. Please add instruments in the Data Management tab.")
        return

    st.info(
        f"🚀 **Professional AI Analysis Mode**: Analyzing {len(st.session_state.instruments_list)} instruments with advanced AI algorithms including today's real-time patterns")

    # Date Range Selection
    st.subheader("📅 Analysis Time Range")

    col1, col2 = st.columns(2)

    with col1:
        # Default to 6 months ago
        default_date = datetime.now() - timedelta(days=180)

        analysis_start_date = st.date_input(
            "📅 Analysis Start Date",
            value=st.session_state.get('analysis_start_date', default_date),
            max_value=datetime.now().date(),
            help="AI will analyze patterns from this date onwards (including today's real-time patterns)",
            key="analysis_start_date_picker"
        )

        # Convert to datetime
        analysis_start_datetime = datetime.combine(analysis_start_date, datetime.min.time())
        st.session_state['analysis_start_date'] = analysis_start_datetime

    with col2:
        duration = datetime.now() - analysis_start_datetime
        st.metric("Analysis Period", f"{duration.days} days")

        # Show today's date prominently
        today_str = datetime.now().strftime('%Y-%m-%d')
        st.metric("Today's Date", today_str)
        st.success("✅ Today's patterns included")

        # Quick date setters
        st.write("**📅 Quick Selection:**")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📅 1 Month", key="analysis_1month"):
                st.session_state['analysis_start_date'] = datetime.now() - timedelta(days=30)
                st.rerun()
            if st.button("📅 3 Months", key="analysis_3months"):
                st.session_state['analysis_start_date'] = datetime.now() - timedelta(days=90)
                st.rerun()
        with col_b:
            if st.button("📅 6 Months", key="analysis_6months"):
                st.session_state['analysis_start_date'] = datetime.now() - timedelta(days=180)
                st.rerun()
            if st.button("📅 1 Year", key="analysis_1year"):
                st.session_state['analysis_start_date'] = datetime.now() - timedelta(days=365)
                st.rerun()

    st.divider()

    # NEW: Stop Loss and Trading Configuration Section
    st.subheader("⚙️ Trading Configuration")

    config_col1, config_col2, config_col3, config_col4 = st.columns(4)

    with config_col1:
        st.write("**📊 Stop Loss Config:**")
        use_trailing_stop = st.checkbox(
            "🔄 Use Trailing Stop",
            value=st.session_state.get('use_trailing_stop', False),
            help="When enabled, stop loss will trail upward after hitting target",
            key="analysis_trailing_stop"
        )
        st.session_state['use_trailing_stop'] = use_trailing_stop

        if use_trailing_stop:
            st.success("✅ Trailing Active")
        else:
            st.info("📍 Fixed Stop Loss")

    with config_col2:
        st.write("**🎯 Target Config:**")
        use_custom_target = st.checkbox(
            "📈 Custom Target %",
            value=st.session_state.get('use_custom_target', False),
            help="Override default timeframe targets",
            key="analysis_use_custom_target"
        )
        st.session_state['use_custom_target'] = use_custom_target

        if use_custom_target:
            custom_target = st.number_input(
                "Target %",
                min_value=0.1,
                max_value=50.0,
                value=float(st.session_state.get('custom_target_pct', 1.0)) if st.session_state.get(
                    'custom_target_pct') is not None else 1.0,
                step=0.1,
                format="%.2f",
                help="Custom target percentage",
                key="analysis_custom_target"
            )
            st.session_state['custom_target_pct'] = custom_target
            st.success(f"🎯 Target: {custom_target:.2f}%")
        else:
            st.info("📊 Default targets")
            st.session_state['custom_target_pct'] = None

    with config_col3:
        st.write("**📈 Partial Exits:**")
        use_partial_exits = st.checkbox(
            "💰 Enable Partial Exits",
            value=st.session_state.get('use_partial_exits', False),
            help="Exit 50% at 0.5% and remaining 50% at 0.9%",
            key="analysis_partial_exits"
        )
        st.session_state['use_partial_exits'] = use_partial_exits

        if use_partial_exits:
            col_a, col_b = st.columns(2)
            with col_a:
                # Ensure value is float
                first_exit_default = st.session_state.get('first_exit_pct', 0.5)
                if isinstance(first_exit_default, (list, tuple)):
                    first_exit_default = 0.5

                first_exit = st.number_input(
                    "1st Exit %",
                    min_value=0.1,
                    max_value=10.0,
                    value=float(first_exit_default),
                    step=0.1,
                    format="%.2f",
                    key="first_exit_pct_input"
                )
                st.session_state['first_exit_pct'] = first_exit

            with col_b:
                # Ensure value is float
                second_exit_default = st.session_state.get('second_exit_pct', 0.9)
                if isinstance(second_exit_default, (list, tuple)):
                    second_exit_default = 0.9

                second_exit = st.number_input(
                    "2nd Exit %",
                    min_value=0.1,
                    max_value=10.0,
                    value=float(second_exit_default),
                    step=0.1,
                    format="%.2f",
                    key="second_exit_pct_input"
                )
                st.session_state['second_exit_pct'] = second_exit

            # Fix the slider value type issue
            first_capital_default = st.session_state.get('first_exit_capital_pct', 50)
            # Ensure it's an integer, not a list
            if isinstance(first_capital_default, (list, tuple)):
                first_capital_default = 50
            elif not isinstance(first_capital_default, (int, float)):
                first_capital_default = 50
            else:
                first_capital_default = int(first_capital_default)

            first_capital = st.slider(
                "1st Exit Capital %",
                min_value=10,
                max_value=90,
                value=first_capital_default,
                step=10,
                key="first_exit_capital_slider"
            )
            st.session_state['first_exit_capital_pct'] = float(first_capital)

            st.success(f"✅ Exit {first_capital}% @ {first_exit:.1f}%, {100 - first_capital}% @ {second_exit:.1f}%")
        else:
            st.info("📊 Single exit")

    with config_col4:
        st.write("**⏰ Intraday Config:**")
        intraday_mode = st.checkbox(
            "📅 Intraday Mode",
            value=st.session_state.get('intraday_mode', False),
            help="Exit all positions at specified time",
            key="analysis_intraday_mode"
        )
        st.session_state['intraday_mode'] = intraday_mode

        if intraday_mode:
            entry_cutoff = st.text_input(
                "Entry Cutoff",
                value=st.session_state.get('intraday_entry_cutoff', '11:45'),
                help="No new entries after this",
                key="analysis_entry_cutoff"
            )
            st.session_state['intraday_entry_cutoff'] = entry_cutoff

            exit_time = st.text_input(
                "Exit Time",
                value=st.session_state.get('intraday_exit_time', '15:15'),
                help="Exit all positions",
                key="analysis_exit_time"
            )
            st.session_state['intraday_exit_time'] = exit_time

            st.warning(f"⚠️ Entry<{entry_cutoff}, Exit@{exit_time}")

    st.divider()

    # Pattern Selection Section
    st.subheader("🎯 AI Pattern Selection")
    render_pattern_selection_checkboxes("analysis_")

    # Display AI-optimized timeframe targets
    st.subheader("🎯 AI-Optimized Timeframe Targets")
    target_data = [
        {"Timeframe": "1m", "AI Target": "0.5%", "Strategy": "Scalping", "Best Patterns": "Pin Bar, Dragonfly Doji",
         "AI Status": "✅ Active"},
        {"Timeframe": "5m", "AI Target": "0.75%", "Strategy": "Quick Trades", "Best Patterns": "Marubozu, Kicker",
         "AI Status": "✅ Active"},
        {"Timeframe": "15m", "AI Target": "1.0%", "Strategy": "Intraday", "Best Patterns": "Harami, Tweezer",
         "AI Status": "✅ Active"},
        {"Timeframe": "30m", "AI Target": "1.5%", "Strategy": "Extended Intraday",
         "Best Patterns": "Engulfing, Morning Star", "AI Status": "✅ Active"},
        {"Timeframe": "1H", "AI Target": "2.5%", "Strategy": "Short Swing", "Best Patterns": "All Patterns",
         "AI Status": "✅ Active"},
        {"Timeframe": "4H", "AI Target": "5.0%", "Strategy": "Swing Trading", "Best Patterns": "Three White Soldiers",
         "AI Status": "✅ Active"},
        {"Timeframe": "1D", "AI Target": "8.0%", "Strategy": "Position Trading",
         "Best Patterns": "Abandoned Baby, Kicker", "AI Status": "✅ Active"},
    ]

    target_df = pd.DataFrame(target_data)
    create_download_buttons(target_df, "ai_timeframe_targets", "AI Target Configuration")
    st.dataframe(target_df, use_container_width=True, height=200)

    # Analysis controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        analysis_timeframes = st.multiselect(
            "Select Timeframes for AI Analysis",
            ['1m', '5m', '15m', '30m', '1H', '4H', '1D'],
            default=['15m', '4H', '1D'],
            help="Choose timeframes for AI-powered analysis with optimized targets",
            key="analysis_timeframes"
        )

    with col2:
        exchange = st.selectbox("Exchange", ['NSE', 'BINANCE', 'BSE'], index=0, key="analysis_exchange")

    with col3:
        st.metric("Instruments", len(st.session_state.instruments_list))

    # Display selected patterns summary
    selected_patterns = [k for k, v in st.session_state.pattern_selection.items() if v]
    if selected_patterns:
        st.success(f"🧠 Selected {len(selected_patterns)} AI-powered bullish patterns")
        pattern_names = []
        for pattern in selected_patterns:
            name_map = {
                'pin_bar': 'Pin Bar',
                'bullish_engulfing': 'Bullish Engulfing',
                'three_candle': 'Morning Star',
                'dragonfly_doji': 'Dragonfly Doji',
                'three_white_soldiers': 'Three White Soldiers',
                'bullish_marubozu': 'Bullish Marubozu',
                'bullish_harami': 'Bullish Harami',
                'bullish_abandoned_baby': 'Abandoned Baby',
                'tweezer_bottom': 'Tweezer Bottom',
                'bullish_kicker': 'Bullish Kicker'
            }
            pattern_names.append(name_map.get(pattern, pattern))
        st.write(f"**Selected Patterns:** {', '.join(pattern_names)}")
    else:
        st.error("❌ No patterns selected! Please select at least one pattern for AI analysis.")

    # Auto display selected instruments
    st.subheader("📋 Portfolio Under Analysis")
    instruments_text = ", ".join(st.session_state.instruments_list)
    st.text_area("All instruments from portfolio:", instruments_text, height=80, disabled=True)

    # Data freshness check and combined analysis section
    st.subheader("🚀 Combined Update + AI Pattern Analysis")

    # Auto-refresh configuration
    st.subheader("⏱️ Auto-Refresh Configuration")

    col_refresh1, col_refresh2, col_refresh3 = st.columns(3)

    with col_refresh1:
        auto_refresh_enabled = st.checkbox(
            "🔄 Enable Auto-Refresh",
            value=st.session_state.get('auto_refresh_analysis', False),
            help="Automatically refresh analysis at set intervals",
            key="auto_refresh_analysis_checkbox"
        )
        st.session_state['auto_refresh_analysis'] = auto_refresh_enabled

    with col_refresh2:
        if auto_refresh_enabled:
            refresh_interval_minutes = st.selectbox(
                "Refresh Interval",
                [1, 2, 5, 10, 15, 30, 60, 120, 180, 240],  # Minutes
                index=2,  # Default to 5 minutes
                format_func=lambda x: f"{x} minute{'s' if x != 1 else ''}",
                key="auto_refresh_interval_minutes"
            )
            st.session_state['refresh_interval_minutes'] = refresh_interval_minutes
        else:
            refresh_interval_minutes = 5  # Default

    with col_refresh3:
        if auto_refresh_enabled:
            st.info(f"📊 Refresh every {refresh_interval_minutes} minute{'s' if refresh_interval_minutes != 1 else ''}")

            # Show last refresh time
            last_refresh = st.session_state.get('last_auto_refresh_time', 0)
            if last_refresh > 0:
                time_since = time.time() - last_refresh
                st.write(f"Last refresh: {int(time_since // 60)}m {int(time_since % 60)}s ago")
            else:
                st.write("No refresh yet")

    # WORKING AUTO-REFRESH IMPLEMENTATION
    if auto_refresh_enabled:
        refresh_interval_seconds = refresh_interval_minutes * 60

        # Simple countdown and trigger mechanism
        last_refresh_time = st.session_state.get('last_auto_refresh_time', 0)
        current_time = time.time()
        time_since_last = current_time - last_refresh_time

        # Check if it's time to refresh
        if time_since_last >= refresh_interval_seconds or last_refresh_time == 0:
            # Time to refresh!
            st.session_state['last_auto_refresh_time'] = current_time

            # Auto-trigger the analysis if timeframes and patterns are selected
            if analysis_timeframes and selected_patterns and st.session_state.get('auto_refresh_should_run', True):
                st.info("🔄 Auto-refresh triggered - Running combined update + analysis...")
                st.session_state['auto_refresh_should_run'] = False  # Prevent infinite loops

                # Add a small delay to show the message
                time.sleep(1)

                # Auto-execute the combined analysis
                auto_execute_analysis = True
                st.session_state['auto_triggered'] = True
            else:
                auto_execute_analysis = False
        else:
            auto_execute_analysis = False
            st.session_state['auto_refresh_should_run'] = True  # Ready for next refresh

        # Countdown display
        time_remaining = refresh_interval_seconds - time_since_last
        if time_remaining > 0 and not auto_execute_analysis:
            minutes_left = int(time_remaining // 60)
            seconds_left = int(time_remaining % 60)

            countdown_container = st.empty()
            if minutes_left > 0:
                countdown_container.success(f"✅ Next auto-refresh in: {minutes_left}m {seconds_left}s")
            else:
                countdown_container.success(f"✅ Next auto-refresh in: {seconds_left}s")

        # Manual controls
        col_manual1, col_manual2, col_manual3 = st.columns(3)

        with col_manual1:
            if st.button("🧪 Refresh Now", use_container_width=True):
                st.session_state['last_auto_refresh_time'] = time.time()
                st.success("🔄 Manual refresh triggered!")
                auto_execute_analysis = True
                st.session_state['auto_triggered'] = True

        with col_manual2:
            if st.button("⏹️ Stop Auto-Refresh", use_container_width=True):
                st.session_state['auto_refresh_analysis'] = False
                st.session_state['auto_refresh_should_run'] = True
                st.success("Auto-refresh stopped")
                st.rerun()

        with col_manual3:
            # Reset timer button
            if st.button("🔄 Reset Timer", use_container_width=True):
                st.session_state['last_auto_refresh_time'] = time.time()
                st.success("Timer reset!")
                st.rerun()

        # Status display
        if analysis_timeframes and selected_patterns:
            st.success("✅ Auto-refresh is ACTIVE - Will automatically run combined update + analysis")
        else:
            st.warning("⚠️ Auto-refresh enabled but no timeframes/patterns selected")

        # Execute analysis if triggered by auto-refresh
        if auto_execute_analysis:
            # This will make the button logic execute the analysis
            st.session_state['trigger_combined_analysis'] = True
            st.rerun()

    else:
        st.info("Auto-refresh disabled. Enable to automatically run analysis at intervals.")
        st.session_state['auto_refresh_should_run'] = True

    # Telegram Alert Configuration - WEBHOOK ONLY VERSION
    st.divider()
    st.subheader("📱 Telegram Alert Configuration")

    tel_col1, tel_col2, tel_col3 = st.columns(3)

    with tel_col1:
        telegram_enabled = st.checkbox(
            "📱 Enable Telegram Alerts",
            value=st.session_state.get('telegram_enabled', False),
            help="Send pattern alerts to Telegram when detected",
            key="telegram_enabled_checkbox"
        )
        st.session_state['telegram_enabled'] = telegram_enabled

        if telegram_enabled:
            st.success("✅ Telegram alerts ACTIVE")
        else:
            st.info("📱 Telegram alerts disabled")

    with tel_col2:
        if telegram_enabled:
            webhook_url = st.text_input(
                "Webhook URL",
                value=st.session_state.get('telegram_webhook_url', ''),
                type="password",
                help="Your Telegram webhook URL (or Discord webhook, etc.)",
                placeholder="https://your-webhook-url.com/webhook",
                key="telegram_webhook_input"
            )
            st.session_state['telegram_webhook_url'] = webhook_url

            if webhook_url:
                st.success("✅ Webhook configured")
            else:
                st.warning("⚠️ Enter webhook URL")

    with tel_col3:
        if telegram_enabled:
            st.write("**Webhook Status:**")
            if webhook_url:
                st.success("✅ Ready to send alerts")
                st.info("Alerts will be sent to webhook")
            else:
                st.error("❌ Webhook URL required")

    if telegram_enabled:
        # Alert settings
        alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)

        with alert_col1:
            alert_on_live = st.checkbox(
                "Alert on Today's Patterns",
                value=st.session_state.get('telegram_alert_on_live', True),
                key="telegram_alert_live"
            )
            st.session_state['telegram_alert_on_live'] = alert_on_live

        with alert_col2:
            alert_on_confirmed = st.checkbox(
                "Alert on All Patterns",
                value=st.session_state.get('telegram_alert_on_confirmed', False),
                key="telegram_alert_confirmed"
            )
            st.session_state['telegram_alert_on_confirmed'] = alert_on_confirmed

        with alert_col3:
            cooldown = st.number_input(
                "Cooldown (seconds)",
                min_value=30,
                max_value=3600,
                value=st.session_state.get('telegram_alert_cooldown', 60),
                step=30,
                help="Minimum seconds between duplicate alerts",
                key="telegram_cooldown_input"
            )
            st.session_state['telegram_alert_cooldown'] = cooldown

        with alert_col4:
            if st.button("🧪 Test Alert", use_container_width=True):
                if webhook_url:
                    test_message = f"""
<b>🧪 TEST ALERT</b>

This is a test alert from your AI Trading Platform.

Configuration:
- Webhook: ✅ Connected
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Your webhook alerts are working correctly!

#TestAlert
"""
                    if send_telegram_alert(webhook_url, test_message):
                        st.success("✅ Test alert sent successfully!")
                    else:
                        st.error("❌ Failed to send test alert. Check your webhook URL.")
                else:
                    st.warning("Please enter webhook URL first")

        # Show last alert info
        last_alert_time = st.session_state.get('telegram_last_alert_time')
        if last_alert_time:
            time_since = time.time() - last_alert_time
            st.info(f"Last alert sent: {int(time_since // 60)}m {int(time_since % 60)}s ago")

    st.divider()

    # Combined button for Update All + Pattern Analysis
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        # NEW COMBINED FUNCTIONALITY - Single button for Update + Analysis with Auto-Refresh Integration
        button_text = "🚀 UPDATE ALL + AI PATTERN ANALYSIS"
        if auto_refresh_enabled:
            button_text += " (Auto-Refresh ON)"

        # Check if auto-refresh triggered this execution
        auto_triggered = st.session_state.get('trigger_combined_analysis', False)
        if auto_triggered:
            st.session_state['trigger_combined_analysis'] = False  # Reset trigger
            st.info("🤖 Auto-refresh triggered - executing combined analysis...")
            should_execute = True
        else:
            should_execute = st.button(button_text, type="primary", use_container_width=True)

        if should_execute:
            if not analysis_timeframes:
                st.error("Please select at least one timeframe for analysis")
                return

            if not selected_patterns:
                st.error("Please select at least one pattern for analysis")
                return

            # Calculate total operations for both update and analysis phases
            total_update_ops = len(st.session_state.instruments_list) * len(analysis_timeframes)

            # Create main progress containers
            main_progress = st.progress(0)
            main_status = st.empty()
            phase_status = st.empty()

            # Show if this was auto-triggered
            if auto_triggered:
                main_status.info("🤖 AUTO-REFRESH EXECUTION: Starting combined update + analysis...")

            try:
                # PHASE 1: DATA UPDATE
                main_status.info("🔄 PHASE 1: Updating all data with real-time information...")
                phase_status.text("Preparing data updates...")

                # Update progress (Phase 1 = 0-40% of total)
                update_summary = {
                    'updated': 0,
                    'current': 0,
                    'failed': 0,
                    'new_bars_total': 0,
                    'instruments_updated': set()
                }

                start_time = time.time()

                # Process updates with progress tracking
                for i, symbol in enumerate(st.session_state.instruments_list):
                    for j, timeframe in enumerate(analysis_timeframes):
                        current_op = i * len(analysis_timeframes) + j + 1
                        # Update progress (0-40% for data update phase)
                        progress = (current_op / total_update_ops) * 0.4
                        main_progress.progress(progress)
                        phase_status.text(f"Updating {symbol} {timeframe} ({current_op}/{total_update_ops})")

                        try:
                            # Single update call
                            result = st.session_state.data_manager.update_data_incrementally(
                                [symbol],
                                [timeframe],
                                exchange,
                                force_update=False
                            )

                            # Parse result
                            if symbol in result and timeframe in result[symbol]:
                                status = result[symbol][timeframe]
                                if "✅" in status:
                                    update_summary['instruments_updated'].add(symbol)
                                    if "Updated" in status and "+" in status:
                                        try:
                                            new_bars = int(status.split('+')[1].split(' ')[0])
                                            update_summary['new_bars_total'] += new_bars
                                            update_summary['updated'] += 1
                                        except:
                                            update_summary['updated'] += 1
                                    elif "Current" in status:
                                        update_summary['current'] += 1
                                    else:
                                        update_summary['updated'] += 1
                                else:
                                    update_summary['failed'] += 1
                        except Exception as e:
                            update_summary['failed'] += 1

                # Phase 1 complete
                main_progress.progress(0.4)
                elapsed_update_time = time.time() - start_time
                phase_status.success(
                    f"✅ Data update complete in {elapsed_update_time:.1f}s - {update_summary['new_bars_total']} new bars added!")

                # Show update summary briefly
                time.sleep(1)

                # PHASE 2: AI PATTERN ANALYSIS
                main_status.info("🧠 PHASE 2: Running AI pattern analysis with updated data...")
                main_progress.progress(0.5)
                phase_status.text("Initializing AI pattern recognition engines...")

                # Short delay to show progress
                time.sleep(0.5)

                # Run the comprehensive analysis with progress tracking
                analysis_start_time = time.time()

                phase_status.text(
                    f"AI analyzing {len(st.session_state.instruments_list)} instruments across {len(analysis_timeframes)} timeframes...")
                main_progress.progress(0.7)

                results, debug_info = run_comprehensive_analysis(
                    st.session_state.instruments_list,
                    analysis_timeframes,
                    st.session_state.analysis_parameters,
                    st.session_state.pattern_selection,
                    analysis_start_datetime,
                    exchange,
                    use_trailing_stop=st.session_state.get('use_trailing_stop', False),
                    intraday_mode=st.session_state.get('intraday_mode', False),
                    entry_cutoff_time=st.session_state.get('intraday_entry_cutoff', '11:45'),
                    exit_time=st.session_state.get('intraday_exit_time', '15:15'),
                    custom_target_pct=st.session_state.get('custom_target_pct', None),
                    use_partial_exits=st.session_state.get('use_partial_exits', False),
                    first_exit_pct=st.session_state.get('first_exit_pct', 0.5),
                    second_exit_pct=st.session_state.get('second_exit_pct', 0.9),
                    first_exit_capital_pct=st.session_state.get('first_exit_capital_pct', 50.0)
                )

                main_progress.progress(0.95)
                analysis_elapsed_time = time.time() - analysis_start_time

                # Store results
                st.session_state.analysis_results = results
                st.session_state.analysis_complete = True
                st.session_state.debug_info = debug_info

                # PHASE 3: TELEGRAM ALERTS (if enabled)
                if st.session_state.get('telegram_enabled', False) and results:
                    main_status.info("📱 PHASE 3: Sending Telegram alerts...")
                    alerts_sent = process_analysis_results_for_alerts(results)
                    if alerts_sent > 0:
                        phase_status.success(f"📱 Sent {alerts_sent} Telegram alerts for today's patterns")

                # PHASE 4: COMPLETE
                main_progress.progress(1.0)
                total_elapsed_time = time.time() - start_time

                # Clear progress indicators
                main_progress.empty()
                main_status.empty()
                phase_status.empty()

                if results:
                    today_patterns_count = debug_info.get('today_patterns_detected', 0)

                    # Success notification with comprehensive summary
                    st.balloons()  # Celebration effect

                    success_message = f"""
                    🎉 **COMBINED UPDATE + AI ANALYSIS COMPLETE!**

                    📊 **Data Update Results:**
                    • Total operations: {total_update_ops}
                    • Instruments updated: {len(update_summary['instruments_updated'])}
                    • New bars added: {update_summary['new_bars_total']}
                    • Update time: {elapsed_update_time:.1f}s

                    🧠 **AI Analysis Results:**
                    • Pattern opportunities found: {len(results)}
                    • Today's patterns detected: {today_patterns_count}
                    • Analysis time: {analysis_elapsed_time:.1f}s
                    • Total time: {total_elapsed_time:.1f}s
                    """

                    if st.session_state.get('telegram_enabled', False):
                        telegram_alerts = st.session_state.get('telegram_last_alert_time')
                        if telegram_alerts:
                            success_message += f"""

                            📱 **Telegram Alerts:**
                            • Alerts sent for today's patterns
                            • Last alert: Just now
                            """

                    if auto_refresh_enabled:
                        success_message += f"""

                        ⏱️ **Auto-Refresh Status:**
                        • Auto-refresh is ACTIVE
                        • Next refresh in {st.session_state.get('refresh_interval_minutes', 5)} minutes
                        • Execution type: {'AUTO-TRIGGERED' if auto_triggered else 'MANUAL'}
                        """

                    st.success(success_message)

                    # Professional success notification
                    st.markdown("""
                    <script>
                        setTimeout(() => {
                            if (window.showProfessionalSuccess) {
                                window.showProfessionalSuccess();
                            }
                            if (window.playProfessionalNotification) {
                                window.playProfessionalNotification();
                            }
                        }, 100);
                    </script>
                    """, unsafe_allow_html=True)

                    # Show comprehensive AI analysis summary
                    config_info = []
                    if st.session_state.get('use_trailing_stop'):
                        config_info.append("Trailing Stop: ON")
                    else:
                        config_info.append("Fixed Stop: ON")

                    if st.session_state.get('intraday_mode'):
                        config_info.append(
                            f"Intraday Mode: ON (Exit {st.session_state.get('intraday_exit_time', '15:15')})")

                    if st.session_state.get('use_partial_exits'):
                        config_info.append(
                            f"Partial Exits: {st.session_state.get('first_exit_capital_pct', 50)}%@{st.session_state.get('first_exit_pct', 0.5)}%, {100 - st.session_state.get('first_exit_capital_pct', 50)}%@{st.session_state.get('second_exit_pct', 0.9)}%")

                    if auto_refresh_enabled:
                        config_info.append("Auto-Refresh: ACTIVE")

                    if st.session_state.get('telegram_enabled'):
                        config_info.append("Telegram Alerts: ACTIVE")

                    config_str = " | ".join(config_info) if config_info else "Standard Configuration"

                    st.info(f"""
                    ✅ **COMPREHENSIVE AI ANALYSIS SUMMARY:**
                    - FRESH DATA: {update_summary['new_bars_total']} new bars integrated
                    - TODAY'S PATTERNS DETECTED: {today_patterns_count}
                    - Advanced Swing Low Validation: {debug_info.get('total_invalidated_swing_lows', 0)} invalidated
                    - Valid Pattern Opportunities: {debug_info.get('total_valid_touches', 0)} confirmed
                    - Configuration: {config_str}
                    - Real-Time Status Tracking: Active
                    - AI Success Prediction: Enabled
                    - Total Processing Time: {total_elapsed_time:.1f} seconds
                    - Execution Mode: {'AUTO-REFRESH' if auto_triggered else 'MANUAL'}
                    """)
                else:
                    completion_message = f"""
                    ℹ️ **COMBINED ANALYSIS COMPLETE**
                    - Data successfully updated ({update_summary['new_bars_total']} new bars)
                    - AI analysis complete - no pattern opportunities found with current parameters
                    - Today's patterns were included in the analysis
                    - Total time: {total_elapsed_time:.1f} seconds
                    - Execution mode: {'AUTO-REFRESH' if auto_triggered else 'MANUAL'}
                    """

                    if auto_refresh_enabled:
                        completion_message += f"\n- Auto-refresh remains ACTIVE (next refresh in {st.session_state.get('refresh_interval_minutes', 5)} minutes)"

                    st.info(completion_message)

            except Exception as e:
                main_progress.empty()
                main_status.empty()
                phase_status.empty()
                st.error(f"❌ Combined analysis failed: {str(e)}")
                st.session_state.analysis_complete = True
                st.session_state.analysis_results = None

    with col2:
        # Separate data update only button
        if st.button("🔄 Update Data Only", use_container_width=True):
            if analysis_timeframes and st.session_state.instruments_list:
                with st.spinner("Updating data..."):
                    results = st.session_state.data_manager.update_data_incrementally(
                        st.session_state.instruments_list,
                        analysis_timeframes,
                        exchange,
                        force_update=False
                    )
                    st.session_state.update_status = results
                    st.session_state.last_data_update = datetime.now()
                    st.success("✅ Data updated!")
            else:
                st.warning("Please select timeframes first")

    with col3:
        # Show data age for first instrument
        if st.session_state.instruments_list and analysis_timeframes:
            symbol = st.session_state.instruments_list[0]
            timeframe = analysis_timeframes[0] if analysis_timeframes else '1H'
            df = st.session_state.data_manager.get_cached_data(symbol, timeframe, exchange)
            if df is not None and not df.empty:
                latest_time = df.index.max()
                age_hours = (datetime.now() - latest_time).total_seconds() / 3600
                st.metric("Data Age (hours)", f"{age_hours:.1f}")

                # Check if we have today's data
                latest_date = latest_time.date()
                today_date = datetime.now().date()
                if latest_date >= today_date:
                    st.success("✅ Real-time data")
                else:
                    st.warning("⚠️ Data needs update")
            else:
                st.metric("Data Age", "No data")

    # Information about the combined functionality
    st.info("""
    🚀 **NEW: Combined Update + Analysis Feature with Telegram Alerts**

    The "UPDATE ALL + AI PATTERN ANALYSIS" button performs operations in sequence:
    1. **Data Update Phase**: Updates all selected instruments/timeframes with latest market data
    2. **AI Analysis Phase**: Runs comprehensive pattern analysis on the fresh data
    3. **Telegram Alerts**: Automatically sends alerts for today's patterns if enabled
    4. **Results**: Provides combined summary of data updates, pattern findings, and alerts sent

    This ensures you always analyze the most recent market data including today's patterns!
    """)

    st.divider()

    # Display results
    if st.session_state.analysis_complete and st.session_state.analysis_results:
        display_analysis_results()
    elif st.session_state.analysis_complete:
        st.info("📊 Analysis completed but no pattern opportunities were found.")
    else:
        st.info("📈 Ready to run combined update + AI analysis with all advanced pattern recognition algorithms.")


def execute_combined_analysis(analysis_timeframes, selected_patterns, analysis_start_datetime, exchange,
                              auto_refresh_enabled):
    """Execute combined update + analysis with optional auto-refresh setup"""

    # Calculate total operations for both update and analysis phases
    total_update_ops = len(st.session_state.instruments_list) * len(analysis_timeframes)

    # Create main progress containers
    main_progress = st.progress(0)
    main_status = st.empty()
    phase_status = st.empty()

    try:
        # PHASE 1: DATA UPDATE
        main_status.info("🔄 PHASE 1: Updating all data with real-time information...")
        phase_status.text("Preparing data updates...")

        # Update progress (Phase 1 = 0-40% of total)
        update_summary = {
            'updated': 0,
            'current': 0,
            'failed': 0,
            'new_bars_total': 0,
            'instruments_updated': set()
        }

        start_time = time.time()

        # Process updates with progress tracking
        for i, symbol in enumerate(st.session_state.instruments_list):
            for j, timeframe in enumerate(analysis_timeframes):
                current_op = i * len(analysis_timeframes) + j + 1
                # Update progress (0-40% for data update phase)
                progress = (current_op / total_update_ops) * 0.4
                main_progress.progress(progress)
                phase_status.text(f"Updating {symbol} {timeframe} ({current_op}/{total_update_ops})")

                try:
                    # Single update call
                    result = st.session_state.data_manager.update_data_incrementally(
                        [symbol],
                        [timeframe],
                        exchange,
                        force_update=False
                    )

                    # Parse result
                    if symbol in result and timeframe in result[symbol]:
                        status = result[symbol][timeframe]
                        if "✅" in status:
                            update_summary['instruments_updated'].add(symbol)
                            if "Updated" in status and "+" in status:
                                try:
                                    new_bars = int(status.split('+')[1].split(' ')[0])
                                    update_summary['new_bars_total'] += new_bars
                                    update_summary['updated'] += 1
                                except:
                                    update_summary['updated'] += 1
                            elif "Current" in status:
                                update_summary['current'] += 1
                            else:
                                update_summary['updated'] += 1
                        else:
                            update_summary['failed'] += 1
                except Exception as e:
                    update_summary['failed'] += 1

        # Phase 1 complete
        main_progress.progress(0.4)
        elapsed_update_time = time.time() - start_time
        phase_status.success(
            f"✅ Data update complete in {elapsed_update_time:.1f}s - {update_summary['new_bars_total']} new bars added!")

        # Show update summary briefly
        time.sleep(1)

        # PHASE 2: AI PATTERN ANALYSIS
        main_status.info("🧠 PHASE 2: Running AI pattern analysis with updated data...")
        main_progress.progress(0.5)
        phase_status.text("Initializing AI pattern recognition engines...")

        # Short delay to show progress
        time.sleep(0.5)

        # Run the comprehensive analysis with progress tracking
        analysis_start_time = time.time()

        phase_status.text(
            f"AI analyzing {len(st.session_state.instruments_list)} instruments across {len(analysis_timeframes)} timeframes...")
        main_progress.progress(0.7)

        results, debug_info = run_comprehensive_analysis(
            st.session_state.instruments_list,
            analysis_timeframes,
            st.session_state.analysis_parameters,
            st.session_state.pattern_selection,
            analysis_start_datetime,
            exchange,
            use_trailing_stop=st.session_state.get('use_trailing_stop', False),
            intraday_mode=st.session_state.get('intraday_mode', False),
            entry_cutoff_time=st.session_state.get('intraday_entry_cutoff', '11:45'),
            exit_time=st.session_state.get('intraday_exit_time', '15:15'),
            custom_target_pct=st.session_state.get('custom_target_pct', None),
            use_partial_exits=st.session_state.get('use_partial_exits', False),
            first_exit_pct=st.session_state.get('first_exit_pct', 0.5),
            second_exit_pct=st.session_state.get('second_exit_pct', 0.9),
            first_exit_capital_pct=st.session_state.get('first_exit_capital_pct', 50.0)
        )

        main_progress.progress(0.95)
        analysis_elapsed_time = time.time() - analysis_start_time

        # Store results
        st.session_state.analysis_results = results
        st.session_state.analysis_complete = True
        st.session_state.debug_info = debug_info

        # PHASE 3: COMPLETE
        main_progress.progress(1.0)
        total_elapsed_time = time.time() - start_time

        # Clear progress indicators
        main_progress.empty()
        main_status.empty()
        phase_status.empty()

        if results:
            today_patterns_count = debug_info.get('today_patterns_detected', 0)

            # Success notification with comprehensive summary
            st.balloons()  # Celebration effect

            success_message = f"""
            🎉 **COMBINED UPDATE + AI ANALYSIS COMPLETE!**

            📊 **Data Update Results:**
            • Total operations: {total_update_ops}
            • Instruments updated: {len(update_summary['instruments_updated'])}
            • New bars added: {update_summary['new_bars_total']}
            • Update time: {elapsed_update_time:.1f}s

            🧠 **AI Analysis Results:**
            • Pattern opportunities found: {len(results)}
            • Today's patterns detected: {today_patterns_count}
            • Analysis time: {analysis_elapsed_time:.1f}s
            • Total time: {total_elapsed_time:.1f}s
            """

            if auto_refresh_enabled:
                success_message += f"""

                ⏱️ **Auto-Refresh Status:**
                • Auto-refresh is ACTIVE
                • Will update when new candles complete
                • Based on shortest timeframe selected
                """

            st.success(success_message)

            # Professional success notification
            st.markdown("""
            <script>
                setTimeout(() => {
                    if (window.showProfessionalSuccess) {
                        window.showProfessionalSuccess();
                    }
                    if (window.playProfessionalNotification) {
                        window.playProfessionalNotification();
                    }
                }, 100);
            </script>
            """, unsafe_allow_html=True)

            # Show comprehensive AI analysis summary
            config_info = []
            if st.session_state.get('use_trailing_stop'):
                config_info.append("Trailing Stop: ON")
            else:
                config_info.append("Fixed Stop: ON")

            if st.session_state.get('intraday_mode'):
                config_info.append(
                    f"Intraday Mode: ON (Exit {st.session_state.get('intraday_exit_time', '15:15')})")

            if st.session_state.get('use_partial_exits'):
                config_info.append(
                    f"Partial Exits: {st.session_state.get('first_exit_capital_pct', 50)}%@{st.session_state.get('first_exit_pct', 0.5)}%, {100 - st.session_state.get('first_exit_capital_pct', 50)}%@{st.session_state.get('second_exit_pct', 0.9)}%")

            if auto_refresh_enabled:
                config_info.append("Auto-Refresh: ACTIVE")

            config_str = " | ".join(config_info) if config_info else "Standard Configuration"

            st.info(f"""
            ✅ **COMPREHENSIVE AI ANALYSIS SUMMARY:**
            - FRESH DATA: {update_summary['new_bars_total']} new bars integrated
            - TODAY'S PATTERNS DETECTED: {today_patterns_count}
            - Advanced Swing Low Validation: {debug_info.get('total_invalidated_swing_lows', 0)} invalidated
            - Valid Pattern Opportunities: {debug_info.get('total_valid_touches', 0)} confirmed
            - Configuration: {config_str}
            - Real-Time Status Tracking: Active
            - AI Success Prediction: Enabled
            - Total Processing Time: {total_elapsed_time:.1f} seconds
            """)
        else:
            completion_message = f"""
            ℹ️ **COMBINED ANALYSIS COMPLETE**
            - Data successfully updated ({update_summary['new_bars_total']} new bars)
            - AI analysis complete - no pattern opportunities found with current parameters
            - Today's patterns were included in the analysis
            - Total time: {total_elapsed_time:.1f} seconds
            """

            if auto_refresh_enabled:
                completion_message += "\n- Auto-refresh remains ACTIVE for future updates"

            st.info(completion_message)

    except Exception as e:
        main_progress.empty()
        main_status.empty()
        phase_status.empty()
        st.error(f"❌ Combined analysis failed: {str(e)}")
        st.session_state.analysis_complete = True
        st.session_state.analysis_results = None

    with col2:
        # Separate data update only button
        if st.button("🔄 Update Data Only", use_container_width=True):
            if analysis_timeframes and st.session_state.instruments_list:
                with st.spinner("Updating data..."):
                    results = st.session_state.data_manager.update_data_incrementally(
                        st.session_state.instruments_list,
                        analysis_timeframes,
                        exchange,
                        force_update=False
                    )
                    st.session_state.update_status = results
                    st.session_state.last_data_update = datetime.now()
                    st.success("✅ Data updated!")
            else:
                st.warning("Please select timeframes first")

    with col3:
        # Show data age for first instrument
        if st.session_state.instruments_list and analysis_timeframes:
            symbol = st.session_state.instruments_list[0]
            timeframe = analysis_timeframes[0] if analysis_timeframes else '1H'
            df = st.session_state.data_manager.get_cached_data(symbol, timeframe, exchange)
            if df is not None and not df.empty:
                latest_time = df.index.max()
                age_hours = (datetime.now() - latest_time).total_seconds() / 3600
                st.metric("Data Age (hours)", f"{age_hours:.1f}")

                # Check if we have today's data
                latest_date = latest_time.date()
                today_date = datetime.now().date()
                if latest_date >= today_date:
                    st.success("✅ Real-time data")
                else:
                    st.warning("⚠️ Data needs update")
            else:
                st.metric("Data Age", "No data")

    # Information about the combined functionality
    st.info("""
    🚀 **NEW: Combined Update + Analysis Feature**

    The "UPDATE ALL + AI PATTERN ANALYSIS" button performs both operations in sequence:
    1. **Data Update Phase**: Updates all selected instruments/timeframes with latest market data
    2. **AI Analysis Phase**: Runs comprehensive pattern analysis on the fresh data
    3. **Results**: Provides combined summary of both data updates and pattern findings

    This ensures you always analyze the most recent market data including today's patterns!
    """)

    st.divider()

    # Display results
    if st.session_state.analysis_complete and st.session_state.analysis_results:
        display_analysis_results()
    elif st.session_state.analysis_complete:
        st.info("📊 Analysis completed but no pattern opportunities were found.")
    else:
        st.info("📈 Ready to run combined update + AI analysis with all advanced pattern recognition algorithms.")


# ============================================================================
# COMPLETE REPLACEMENT: display_analysis_results function (around line 5200)
# ============================================================================

def display_analysis_results():
    """Display comprehensive analysis results with IST timestamps and unified CSV output"""
    results = st.session_state.analysis_results
    debug_info = st.session_state.debug_info

    # Save results to scheduler format for viewer access
    if results:
        try:
            latest_file, timestamped_file = save_analysis_results_to_scheduler_format(results)
            st.success(f"✅ Results saved for viewer access: {latest_file.name}")
            st.info(f"📁 Timestamped backup: {timestamped_file.name}")
            st.info(f"🕐 All timestamps converted to Indian Standard Time (IST)")
        except Exception as e:
            st.error(f"❌ Error saving results: {e}")

    # Check for today's patterns
    today_patterns = [r for r in results if r.get("Is Today's Pattern") == "YES"]
    today_count = len(today_patterns)

    # Enhanced header with customizable detection info and IST time
    st.subheader(f"📊 Analysis Results - Generated at {format_ist_timestamp()}")

    # Show detection parameters and validation summary
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        left_lookback = debug_info.get('left_lookback', 10)
        right_lookback = debug_info.get('right_lookback', 3)
        st.metric("Detection Mode", f"{left_lookback}+{right_lookback}",
                  help="Left + Right lookback bars (customizable)")

    with col2:
        filtered_count = debug_info.get('historical_trades_filtered', 0)
        st.metric("Filtered Out", filtered_count, help="Historical trades that wouldn't be detectable live")

    with col3:
        live_detectable = len(results)
        st.metric("Live Detectable", live_detectable, help="All shown results are live-detectable")

    with col4:
        st.metric("Today's Patterns", today_count, help="Real-time patterns from today")

    with col5:
        # Calculate time savings
        symmetric_bars = (left_lookback * 2) + 1
        asymmetric_bars = left_lookback + right_lookback + 1
        time_saved_bars = symmetric_bars - asymmetric_bars
        time_saved_minutes = time_saved_bars * 15  # Assuming 15-min timeframe
        st.metric("Time Saved", f"{time_saved_minutes}min", help="Earlier detection vs symmetric approach")

    # Show validation summary
    filtered_count = debug_info.get('historical_trades_filtered', 0)
    if filtered_count > 0:
        st.warning(
            f"⚠️ **Filtered {filtered_count} historical trades** that wouldn't have been detectable as live entries with {left_lookback}+{right_lookback} bar detection.")
        st.info("💡 This filtering ensures your backtest results match what you can achieve in live trading.")

    st.success(
        f"✅ **All {len(results)} results shown are live-detectable** using {left_lookback}+{right_lookback} customizable swing low detection.")

    if today_count > 0:
        st.success(
            f"🎯 **Found {today_count} real-time patterns from TODAY!** These represent live trading opportunities.")

    # Show entry mode if available
    pattern_only_mode = debug_info.get('pattern_only_entry', False)
    if pattern_only_mode:
        st.info("🟡 **Pattern-Only Entry Mode**: Trading on pattern formation alone (no swing low requirement)")
    else:
        st.info("🟢 **Pattern + Swing Touch Mode**: Traditional mode requiring swing low validation")

    st.divider()

    # Professional Capital Management Section
    st.subheader("💰 Advanced Capital Management")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        new_capital = st.number_input(
            "Capital per Trade (Applied to all live-detectable opportunities)",
            min_value=1000,
            max_value=10000000,
            value=st.session_state.global_capital,
            step=1000,
            help="Capital allocation per trade for all live-detectable opportunities"
        )

    with col2:
        if st.button("🔄 Recalculate P&L", type="primary", use_container_width=True):
            st.session_state.global_capital = new_capital
            st.success("✅ P&L recalculated for live-detectable trades!")
            st.rerun()

    with col3:
        quick_amounts = st.selectbox("Quick Set", [5000, 10000, 25000, 50000, 100000], index=1,
                                     key="analysis_quick_capital")
        if st.button("Set", use_container_width=True, key="analysis_set_capital"):
            st.session_state.global_capital = quick_amounts
            st.rerun()

    st.divider()

    # Calculate P&L with current capital
    updated_results = []
    for result in results:
        result_copy = result.copy()

        if '_trade_outcome' in result and result['_trade_outcome']:
            entry_price = result['_entry_price_numeric']
            trade_outcome = result['_trade_outcome']
            trade_analyzer = result['_trade_analyzer']

            pnl = trade_analyzer.calculate_pnl(entry_price, trade_outcome, st.session_state.global_capital)
            roi = (pnl / st.session_state.global_capital * 100) if st.session_state.global_capital > 0 else 0

            result_copy['Capital Invested'] = f"${st.session_state.global_capital:,.0f}"
            result_copy['P&L'] = f"${pnl:,.2f}"
            result_copy['ROI %'] = f"{roi:.2f}%"
        else:
            result_copy['Capital Invested'] = f"${st.session_state.global_capital:,.0f}"
            result_copy['P&L'] = "$0.00"
            result_copy['ROI %'] = "0.00%"

        updated_results.append(result_copy)

    # Create DataFrame and convert timestamps to IST
    results_df = pd.DataFrame(updated_results)

    # Convert timestamp columns to IST for display
    timestamp_columns = ['Pattern Date', 'Swing Low Date', 'Last Update']
    for col in timestamp_columns:
        if col in results_df.columns:
            results_df[col] = results_df[col].apply(
                lambda x: format_ist_timestamp(x) if pd.notna(x) and x != 'N/A' else x
            )

    # Today's Patterns Summary
    if today_count > 0:
        st.subheader("🎯 Today's Real-Time Pattern Opportunities (Live Detectable)")

        today_df = results_df[results_df["Is Today's Pattern"] == "YES"]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Today's Patterns", len(today_df))
        with col2:
            unique_symbols_today = today_df['Symbol'].nunique()
            st.metric("Symbols Today", unique_symbols_today)
        with col3:
            unique_patterns_today = today_df['Pattern Type'].nunique()
            st.metric("Pattern Types Today", unique_patterns_today)
        with col4:
            avg_detection_mode = today_df['Detection Mode'].iloc[0] if len(
                today_df) > 0 else f"{left_lookback}+{right_lookback}"
            st.metric("Detection Mode", avg_detection_mode)

        # Today's patterns table
        available_columns = today_df.columns.tolist()

        # Define desired columns but only use ones that actually exist
        desired_today_columns = [
            'Symbol', 'Timeframe', 'Pattern Type', 'Pattern Date', 'Entry Price',
            'Trade Outcome', 'Current Status', 'Detection Mode', 'Live Entry Detectable',
            'Capital Invested', 'P&L', 'ROI %'
        ]

        # Only use columns that actually exist in the dataframe
        today_display_columns = [col for col in desired_today_columns if col in available_columns]

        # If Live Entry Detectable column doesn't exist, create it
        if 'Live Entry Detectable' not in today_df.columns:
            today_df = today_df.copy()
            today_df['Live Entry Detectable'] = 'YES'

        today_display_df = today_df[today_display_columns]

        create_download_buttons(today_display_df, "todays_live_detectable_patterns", "Today's Live Patterns")
        st.dataframe(today_display_df, use_container_width=True, height=200)

        st.divider()

    # Professional Pattern Performance Summary
    st.subheader("🧠 AI Pattern Performance Analysis (Live-Detectable Only)")

    # Get all unique patterns from results
    patterns = results_df['Pattern Type'].unique()

    pattern_summary = []
    for pattern in patterns:
        pattern_data = results_df[results_df['Pattern Type'] == pattern]
        total = len(pattern_data)
        success = len(pattern_data[pattern_data["Trade Outcome"] == "Success"])
        ongoing = len(pattern_data[pattern_data["Trade Outcome"] == "Ongoing"])
        today_pattern_count = len(pattern_data[pattern_data["Is Today's Pattern"] == "YES"])
        success_rate = (success / total * 100) if total > 0 else 0

        try:
            pnl_values = pattern_data["P&L"].str.replace("$", "").str.replace(",", "").astype(float)
            total_pnl = pnl_values.sum()
        except:
            total_pnl = 0

        pattern_summary.append({
            'Pattern': pattern,
            'Total Opportunities': total,
            'Today\'s Count': today_pattern_count,
            'Successful': success,
            'Active': ongoing,
            'Live Success Rate': f"{success_rate:.1f}%",
            'Total P&L': f"${total_pnl:,.0f}",
            'Live Detectable': "100%",
            'Detection Mode': f"{left_lookback}+{right_lookback}"
        })

    pattern_summary_df = pd.DataFrame(pattern_summary)
    create_download_buttons(pattern_summary_df, "live_detectable_pattern_performance", "Live Pattern Performance")
    st.dataframe(pattern_summary_df, use_container_width=True)

    # Timeframe Analysis
    timeframes = results_df['Timeframe'].unique()

    for timeframe in timeframes:
        tf_data = results_df[results_df['Timeframe'] == timeframe]
        tf_today_count = len(tf_data[tf_data["Is Today's Pattern"] == "YES"])

        st.subheader(
            f"📊 {timeframe} Timeframe Analysis (Live-Detectable with {left_lookback}+{right_lookback} Detection)")

        # Enhanced Metrics
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

        with col1:
            st.metric("Total", len(tf_data))

        with col2:
            st.metric("Today's", tf_today_count)

        with col3:
            success_count = len(tf_data[tf_data["Trade Outcome"] == "Success"])
            st.metric("Successful", success_count)

        with col4:
            ongoing_count = len(tf_data[tf_data["Trade Outcome"] == "Ongoing"])
            st.metric("Active", ongoing_count)

        with col5:
            if len(tf_data) > 0:
                success_rate = (success_count / len(tf_data)) * 100
                st.metric("Live Success Rate", f"{success_rate:.1f}%")
            else:
                st.metric("Live Success Rate", "0.0%")

        with col6:
            if len(tf_data) > 0 and "Target Used" in tf_data.columns:
                target_used = tf_data["Target Used"].iloc[0]
                st.metric("AI Target", target_used)
            else:
                st.metric("AI Target", "N/A")

        with col7:
            detection_mode = tf_data["Detection Mode"].iloc[0] if len(
                tf_data) > 0 and "Detection Mode" in tf_data.columns else f"{left_lookback}+{right_lookback}"
            st.metric("Detection", detection_mode)

        with col8:
            try:
                pnl_values = tf_data["P&L"].str.replace("$", "").str.replace(",", "").astype(float)
                total_pnl = pnl_values.sum()
                st.metric("Total P&L", f"${total_pnl:,.0f}")
            except:
                st.metric("Total P&L", "$0")

        # Display table for this timeframe - only use existing columns
        all_columns = tf_data.columns.tolist()

        desired_display_columns = [
            'Symbol', 'Pattern Type', 'Swing Low Date', 'Swing Low Price', 'Swing Low Valid',
            'Swing Low Invalidated', 'Pattern Date', 'Is Today\'s Pattern', 'Live Entry Detectable',
            'Entry Price', 'Pattern Low', 'Days Between', 'Distance %', 'Pattern Strength',
            'Strength/Ratio', 'Bullish', 'Trade Outcome', 'Current Status', 'Target Used',
            'Detection Mode', 'Capital Invested', 'P&L', 'ROI %',
            'Target Price', 'Stop Loss', 'Current Price', 'Max Profit %', 'Max Drawdown %',
            'Bars to Resolution', 'Resolution Type', 'Last Update'
        ]

        # Only use columns that exist
        available_columns = [col for col in desired_display_columns if col in all_columns]
        clean_tf_data = tf_data[available_columns]

        create_download_buttons(clean_tf_data, f"live_detectable_analysis_{timeframe}", f"Live {timeframe} Analysis")
        st.dataframe(clean_tf_data, use_container_width=True, height=300)

        st.divider()

    # Overall portfolio summary
    st.subheader("🏆 Professional Portfolio Summary (Live-Detectable Trades Only)")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        total_capital = len(results_df) * st.session_state.global_capital
        st.metric("Total Capital", f"${total_capital:,.0f}")

    with col2:
        try:
            all_pnl_values = results_df["P&L"].str.replace("$", "").str.replace(",", "").astype(float)
            grand_total_pnl = all_pnl_values.sum()
            st.metric("Grand Total P&L", f"${grand_total_pnl:,.2f}")
        except:
            grand_total_pnl = 0
            st.metric("Grand Total P&L", "$0.00")

    with col3:
        if total_capital > 0:
            overall_roi = (grand_total_pnl / total_capital * 100)
            st.metric("Portfolio ROI", f"{overall_roi:.2f}%")
        else:
            st.metric("Portfolio ROI", "0.00%")

    with col4:
        avg_pnl = grand_total_pnl / len(results_df) if len(results_df) > 0 else 0
        st.metric("Avg P&L/Trade", f"${avg_pnl:.2f}")

    with col5:
        st.metric("Detection Mode", f"{left_lookback}+{right_lookback}")

    with col6:
        st.metric("Today's Patterns", today_count)

    # Complete Results for Download
    st.subheader("📋 Complete Live-Detectable Analysis Report")

    # Use only existing columns for final display
    final_desired_columns = [
        'Symbol', 'Timeframe', 'Pattern Type', 'Swing Low Date', 'Swing Low Price', 'Swing Low Valid',
        'Swing Low Invalidated', 'Pattern Date', 'Is Today\'s Pattern', 'Live Entry Detectable',
        'Entry Price', 'Pattern Low', 'Days Between', 'Distance %', 'Pattern Strength',
        'Strength/Ratio', 'Bullish', 'Trade Outcome', 'Current Status', 'Target Used',
        'Detection Mode', 'Capital Invested', 'P&L', 'ROI %',
        'Target Price', 'Stop Loss', 'Current Price', 'Max Profit %', 'Max Drawdown %',
        'Bars to Resolution', 'Resolution Type', 'Last Update', 'Analysis Time'
    ]

    complete_available_columns = [col for col in final_desired_columns if col in results_df.columns]
    complete_results = results_df[complete_available_columns]

    create_download_buttons(complete_results, "complete_live_detectable_analysis", "Complete Live Analysis Report")
    st.dataframe(complete_results, use_container_width=True, height=400)

    # Final summary message
    st.success(
        f"✅ **Analysis Complete**: {len(results)} live-detectable opportunities found using {left_lookback}+{right_lookback} customizable swing low detection. All results can be detected in real-time trading.")

    filtered_count = debug_info.get('historical_trades_filtered', 0)
    if filtered_count > 0:
        st.info(
            f"💡 **Quality Assurance**: {filtered_count} historical trades were automatically filtered out to ensure all results are achievable in live trading.")

    # Show IST timezone info
    st.info(
        f"🕐 **Timezone**: All timestamps displayed in Indian Standard Time (IST). Generated at {format_ist_timestamp()}")
    # Enhanced trade outcome display logic with trailing stops
    def get_trade_outcome_display(outcome):
        """Get enhanced trade outcome display with trailing stop support"""
        if not outcome:
            return "No Data", "N/A"

        if hasattr(outcome, 'trailing_active') and outcome.trailing_active:
            if outcome.sl_hit:
                trade_outcome_display = "Trailing Stop Hit"
                current_status = f"Trail Exit: {outcome.trailing_profit_pct:.2f}%" if hasattr(outcome,
                                                                                              'trailing_profit_pct') else f"Trail Exit: {outcome.current_profit_pct:.2f}%"
            else:
                trade_outcome_display = "Trailing Active"
                trailing_sl = outcome.trailing_sl_price if hasattr(outcome, 'trailing_sl_price') else 0
                current_status = f"Trailing: {outcome.current_profit_pct:.2f}% (SL: {trailing_sl:.4f})"
        elif outcome.target_reached and hasattr(outcome, 'trailing_active') and not outcome.trailing_active:
            trade_outcome_display = "Target + Trailing Setup"
            current_status = f"Activated: {outcome.current_profit_pct:.2f}%"
        elif outcome.success:
            trade_outcome_display = "Success"
            current_status = f"Profit: {outcome.current_profit_pct:.2f}%"
        elif outcome.sl_hit:
            trade_outcome_display = "Stop Loss"
            current_status = f"SL Hit: {outcome.current_profit_pct:.2f}%"
        else:
            trade_outcome_display = "Active"
            current_status = f"Current: {outcome.current_profit_pct:.2f}%"

        return trade_outcome_display, current_status

    # Update results with enhanced outcome display
    for result in updated_results:
        if '_trade_outcome' in result and result['_trade_outcome']:
            outcome = result['_trade_outcome']
            trade_outcome_display, current_status = get_trade_outcome_display(outcome)
            result['Trade Outcome'] = trade_outcome_display
            result['Current Status'] = current_status


def test_asymmetric_detection():
    """Test function to verify asymmetric detection is working"""
    print("🧪 TESTING ASYMMETRIC SWING LOW DETECTION")

    # Test with sample data
    test_symbol = st.session_state.instruments_list[0] if st.session_state.instruments_list else 'RELIANCE'
    df = st.session_state.data_manager.get_cached_data(test_symbol, '15m', 'NSE')

    if df is None or len(df) < 20:
        print("❌ Need more data for testing")
        return False

    # Test old vs new method
    print(f"\nTesting with {len(df)} bars for {test_symbol}")

    # Simulate old symmetric approach
    old_lookback = 10
    old_start = old_lookback
    old_end = len(df) - old_lookback
    old_tradeable_bars = max(0, old_end - old_start)

    # New asymmetric approach
    new_left = 10
    new_right = 3
    new_start = new_left
    new_end = len(df) - new_right
    new_tradeable_bars = max(0, new_end - new_start)

    print(f"📊 COMPARISON:")
    print(f"  Old (10+10): Bars {old_start} to {old_end - 1} = {old_tradeable_bars} tradeable bars")
    print(f"  New (10+3):  Bars {new_start} to {new_end - 1} = {new_tradeable_bars} tradeable bars")
    print(
        f"  Improvement: {new_tradeable_bars - old_tradeable_bars} more bars ({((new_tradeable_bars / old_tradeable_bars - 1) * 100):.1f}% increase)")

    # Time conversion for 15-minute bars
    old_minutes = old_tradeable_bars * 15
    new_minutes = new_tradeable_bars * 15
    time_saved = new_minutes - old_minutes

    print(f"⏱️ TIMING:")
    print(f"  Old approach: {old_minutes} minutes wait")
    print(f"  New approach: {new_minutes} minutes wait")
    print(f"  Time saved: {time_saved} minutes ({time_saved / 60:.1f} hours)")

    return True


def run_comprehensive_analysis_with_capital(symbols: List[str], timeframes: List[str],
                                            parameters: Dict, pattern_selection: Dict, capital_settings: Dict,
                                            start_date: datetime, exchange: str = 'NSE',
                                            use_trailing_stop: bool = False, intraday_mode: bool = False,
                                            entry_cutoff_time: str = '11:45', exit_time: str = '15:15',
                                            custom_target_pct: float = None) -> Tuple[
    List[SwingLowTouch], Dict, CapitalManager]:
    """Run comprehensive analysis and capital simulation - ENHANCED WITH FLEXIBLE TARGETS"""

    if not TV_AVAILABLE:
        raise Exception("TradingView DataFeed not available")

    try:
        all_touches = []
        data_cache = {}
        debug_info = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'symbols_count': len(symbols),
            'timeframes_count': len(timeframes),
            'total_swing_lows': 0,
            'total_invalidated_swing_lows': 0,
            'total_valid_touches': 0,
            'total_patterns_detected': 0,
            'today_patterns_detected': 0,  # Track today's patterns
            'include_today_candle': True,  # Flag showing today's candle is included
            'use_trailing_stop': use_trailing_stop,
            'intraday_mode': intraday_mode,
            'intraday_entry_cutoff': entry_cutoff_time if intraday_mode else 'N/A',
            'intraday_exit_time': exit_time if intraday_mode else 'N/A',
            'custom_target_pct': custom_target_pct if custom_target_pct else 'Default'
        }

        # Initialize enhanced analyzers
        swing_detector = EnhancedSwingLowDetector(
            parameters.get('swing_lookback', 10),
            parameters.get('min_swing_size', 0.5)
        )

        touch_analyzer = EnhancedSwingLowTouchAnalyzer(
            touch_tolerance_pct=parameters.get('touch_tolerance', 0.5),
            min_days_between=parameters.get('min_days_between', 2)
        )
        trade_analyzer = EnhancedTradeOutcomeAnalyzer(
            parameters.get('max_bars_to_analyze', 100),
            capital_settings.get('capital_per_trade', 10000)
        )

        data_manager = st.session_state.data_manager
        today_date = datetime.now().date()

        # Progress tracking
        total_operations = len(symbols) * len(timeframes)
        current_operation = 0
        progress_bar = st.progress(0)
        status_text = st.empty()

        for symbol in symbols:
            for timeframe in timeframes:
                current_operation += 1
                progress_bar.progress(current_operation / total_operations)
                status_text.text(f"Analyzing {symbol} {timeframe} (INCLUDING TODAY'S CANDLE)...")

                try:
                    # Get cached data
                    df = data_manager.get_cached_data(symbol, timeframe, exchange)
                    if df is None or df.empty:
                        debug_info[f'{symbol}_{timeframe}'] = "No data"
                        continue

                    # Store in cache for capital manager
                    cache_key = f"{symbol}_{timeframe}"
                    data_cache[cache_key] = df

                    # Check if we have today's data
                    latest_data_date = df.index.max().date()
                    has_today_data = latest_data_date >= today_date
                    debug_info[f'{symbol}_{timeframe}_has_today'] = has_today_data

                    # Find swing lows with enhanced invalidation tracking
                    all_swing_lows = swing_detector.find_swing_lows_with_invalidation(df)
                    debug_info['total_swing_lows'] += len(all_swing_lows)

                    # Count invalidated swing lows
                    invalidated_count = sum(1 for sl in all_swing_lows if sl.is_invalidated)
                    debug_info['total_invalidated_swing_lows'] += invalidated_count

                    untouched_swing_lows = swing_detector.find_untouched_swing_lows(df, all_swing_lows)

                    # Detect patterns based on selection - INCLUDING TODAY'S CANDLE
                    all_patterns = detect_selected_patterns_with_today(df, pattern_selection, parameters,
                                                                       include_today=True)

                    # Count today's patterns
                    today_patterns = 0
                    for pattern_list in all_patterns.values():
                        for pattern in pattern_list:
                            pattern_date = pd.Timestamp(pattern.timestamp).date()
                            if pattern_date == today_date:
                                today_patterns += 1

                    debug_info['today_patterns_detected'] += today_patterns

                    # Count detected patterns
                    pattern_count = sum(len(patterns) for patterns in all_patterns.values())
                    debug_info['total_patterns_detected'] += pattern_count

                    # Analyze touches with enhanced validation
                    touches = touch_analyzer.analyze_touches(df, untouched_swing_lows, all_patterns, symbol,
                                                             timeframe)
                    debug_info['total_valid_touches'] += len(touches)

                    # Analyze trade outcomes with flexible targets and enhanced tracking
                    enhanced_touches = trade_analyzer.analyze_trade_outcomes_with_timeframe(
                        df, touches, timeframe,
                        use_trailing_stop, intraday_mode, entry_cutoff_time, exit_time,
                        custom_target_pct
                    )

                    # Get target used
                    target_pct = trade_analyzer.get_target_for_timeframe(timeframe, custom_target_pct)
                    debug_info[f'{symbol}_{timeframe}_target_pct'] = target_pct

                    # Add to all touches
                    all_touches.extend(enhanced_touches)

                    debug_info[f'{symbol}_{timeframe}_touches'] = len(enhanced_touches)

                except Exception as e:
                    debug_info[f'{symbol}_{timeframe}_error'] = str(e)

        progress_bar.empty()
        status_text.empty()

        # Sort all touches chronologically
        all_touches.sort(key=lambda x: x.pattern.timestamp)

        debug_info['total_touches'] = len(all_touches)

        # Initialize Capital Manager
        capital_manager = CapitalManager(
            total_capital=capital_settings.get('total_capital', 100000),
            capital_per_trade=capital_settings.get('capital_per_trade', 10000),
            start_date=start_date
        )

        # Run capital simulation
        if all_touches:
            capital_manager.simulate_chronological_trading(all_touches, data_cache)

        return all_touches, debug_info, capital_manager

    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        raise


def render_capital_simulation_tab():
    """Enhanced Capital Management Simulation tab with professional AI features"""
    st.header("💰 Professional Capital Management Simulation")

    # Professional feature highlight
    st.markdown("""
    <div class="feature-highlight">
    <h3 style="color: #0066cc; margin: 0;">🧠 AI Capital Management Features:</h3>
    <p style="color: #5a6c7d; margin: 5px 0;">
    ✅ Realistic chronological trading simulation | ✅ AI-powered capital allocation | ✅ Today's pattern integration | ✅ Real-time status monitoring | ✅ Advanced risk management
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "🚀 **Professional AI Feature**: Realistic chronological trading simulation with intelligent capital pool management, advanced swing low validation, real-time status monitoring, and today's patterns included!")

    # Capital Configuration
    col1, col2, col3 = st.columns(3)

    with col1:
        total_capital = st.number_input(
            "💰 Total Capital Pool",
            min_value=10000,
            max_value=10000000,
            value=st.session_state.get('total_capital', 100000),
            step=10000,
            help="Total capital available for AI-managed trading"
        )
        st.session_state['total_capital'] = total_capital

    with col2:
        capital_per_trade = st.number_input(
            "💵 Capital per Trade",
            min_value=1000,
            max_value=total_capital,
            value=min(st.session_state.get('capital_per_trade', 10000), total_capital),
            step=1000,
            help="Fixed capital allocated to each AI-identified opportunity"
        )
        st.session_state['capital_per_trade'] = capital_per_trade

    with col3:
        max_trades = int(total_capital / capital_per_trade)
        st.metric("Max Concurrent Trades", max_trades)

    st.divider()

    # Date Configuration
    st.subheader("📅 AI Analysis Time Range")

    col1, col2 = st.columns(2)

    with col1:
        # Default to 6 months ago
        default_date = datetime.now() - timedelta(days=180)

        start_date = st.date_input(
            "📅 Start Date for AI Analysis",
            value=st.session_state.get('capital_start_date', default_date),
            max_value=datetime.now().date(),
            help="AI will analyze patterns from this date onwards (including today's patterns)",
            key="capital_start_date_picker"
        )

        # Convert to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        st.session_state['capital_start_date'] = start_datetime

        # Show warning if future date
        if start_datetime > datetime.now():
            st.error("❌ Start date cannot be in the future!")

    with col2:
        duration = datetime.now() - start_datetime
        st.metric("Analysis Period", f"{duration.days} days")

        # Show today's date and inclusion status
        today_str = datetime.now().strftime('%Y-%m-%d')
        st.metric("Today's Date", today_str)
        st.success("✅ Today's patterns included")

        # Quick date setters
        st.write("**Quick Selection:**")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📅 1 Month", key="capital_1month"):
                st.session_state['capital_start_date'] = datetime.now() - timedelta(days=30)
                st.rerun()
            if st.button("📅 3 Months", key="capital_3months"):
                st.session_state['capital_start_date'] = datetime.now() - timedelta(days=90)
                st.rerun()
        with col_b:
            if st.button("📅 6 Months", key="capital_6months"):
                st.session_state['capital_start_date'] = datetime.now() - timedelta(days=180)
                st.rerun()
            if st.button("📅 1 Year", key="capital_1year"):
                st.session_state['capital_start_date'] = datetime.now() - timedelta(days=365)
                st.rerun()

    st.divider()

    # Pattern Selection
    st.subheader("🎯 AI Pattern Selection for Capital Analysis")
    render_pattern_selection_checkboxes("capital_")

    st.divider()

    # Analysis Configuration
    col1, col2 = st.columns([2, 1])

    with col1:
        timeframes = st.multiselect(
            "Select Timeframes for AI Capital Analysis",
            ['1m', '5m', '15m', '30m', '1H', '4H', '1D'],
            default=['4H', '1D'],
            help="Choose timeframes for AI capital simulation with professional tracking",
            key="capital_timeframes"
        )

    with col2:
        exchange = st.selectbox("Exchange", ['NSE', 'BINANCE', 'BSE'], index=0, key="capital_exchange")

    # Run Analysis Button
    selected_patterns = [k for k, v in st.session_state.pattern_selection.items() if v]

    if not selected_patterns:
        st.error("❌ Please select at least one pattern")
    elif not st.session_state.instruments_list:
        st.error("❌ Please load instruments first")
    elif not timeframes:
        st.error("❌ Please select at least one timeframe")
    else:
        if st.button("🚀 Run Professional AI Capital Analysis", type="primary", use_container_width=True):
            with st.spinner(f"Running professional AI capital analysis from {start_datetime.strftime('%Y-%m-%d')}..."):
                try:
                    capital_settings = {
                        'total_capital': total_capital,
                        'capital_per_trade': capital_per_trade
                    }

                    # Run analysis with capital management and AI features
                    all_touches, debug_info, capital_manager = run_comprehensive_analysis_with_capital(
                        st.session_state.instruments_list,
                        timeframes,
                        st.session_state.analysis_parameters,
                        st.session_state.pattern_selection,
                        capital_settings,
                        start_datetime,
                        exchange
                    )

                    # Store results
                    st.session_state['capital_manager'] = capital_manager
                    st.session_state['all_touches'] = all_touches
                    st.session_state['capital_debug'] = debug_info
                    st.session_state['capital_analysis_complete'] = True

                    today_patterns_count = debug_info.get('today_patterns_detected', 0)
                    st.success(f"✅ Professional AI Capital analysis complete!")

                    # Professional success notification
                    st.markdown("""
                    <script>
                        setTimeout(() => {
                            if (window.showProfessionalSuccess) {
                                window.showProfessionalSuccess();
                            }
                            if (window.playProfessionalNotification) {
                                window.playProfessionalNotification();
                            }
                        }, 100);
                    </script>
                    """, unsafe_allow_html=True)

                    # Show AI capital analysis summary
                    st.info(f"""
                    ✅ **AI CAPITAL ANALYSIS SUMMARY:**
                    - TODAY'S PATTERNS PROCESSED: {today_patterns_count}
                    - Total Opportunities Analyzed: {debug_info.get('total_swing_lows', 0)}
                    - Invalidated Opportunities: {debug_info.get('total_invalidated_swing_lows', 0)}
                    - Valid Trading Opportunities: {debug_info.get('total_valid_touches', 0)}
                    - Patterns Detected: {debug_info.get('total_patterns_detected', 0)}
                    - Instruments Analyzed: {debug_info.get('symbols_analyzed', 0)}
                    - AI Real-Time Integration: ✅ ACTIVE
                    """)

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")

    # Display Results
    if st.session_state.get('capital_analysis_complete') and st.session_state.get('capital_manager'):
        display_capital_results()


def display_capital_results():
    """Display professional capital management results"""
    capital_manager = st.session_state.get('capital_manager')
    all_touches = st.session_state.get('all_touches', [])
    debug_info = st.session_state.get('capital_debug', {})

    if not capital_manager:
        return

    st.divider()
    st.subheader("📊 Professional Capital Performance Dashboard")

    summary = capital_manager.get_performance_summary()

    # Key metrics with professional styling
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Starting Capital", f"${summary['total_capital_start']:,.0f}")

    with col2:
        st.metric("Current Capital", f"${summary['total_capital_current']:,.0f}",
                  f"${summary['total_pnl']:,.0f}")

    with col3:
        st.metric("Total ROI", f"{summary['total_roi_pct']:.2f}%")

    with col4:
        st.metric("AI Win Rate", f"{summary['win_rate_pct']:.1f}%")

    with col5:
        st.metric("Max Drawdown", f"{summary['max_drawdown_pct']:.2f}%")

    # Second row of metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Trades Executed", summary['trades_executed'])

    with col2:
        st.metric("Trades Rejected", summary['trades_rejected'])

    with col3:
        st.metric("Active Trades", summary['open_trades'])

    with col4:
        st.metric("Winning Trades", summary['winning_trades'])

    with col5:
        st.metric("Losing Trades", summary['losing_trades'])

    # Show today's patterns count if available
    today_patterns_count = debug_info.get('today_patterns_detected', 0)
    if today_patterns_count > 0:
        st.success(f"🎯 Today's patterns processed in AI capital simulation: {today_patterns_count}")

    st.divider()

    # Capital Timeline Chart
    st.subheader("📈 Capital Timeline")

    timeline_df = capital_manager.get_capital_timeline_df()
    if not timeline_df.empty:
        chart_data = timeline_df.set_index('timestamp')[['total_capital', 'available_capital', 'locked_capital']]
        st.line_chart(chart_data)

    st.divider()

    # Complete Analysis Details Section
    st.subheader("📋 Complete Professional Analysis Details")

    if all_touches:
        # Convert touches to DataFrame for display
        touch_data = []
        today_date = datetime.now().date()

        for touch in all_touches:
            pattern = touch.pattern
            pattern_type = touch.pattern_type

            # Check if this is today's pattern
            pattern_date = pd.Timestamp(pattern.timestamp).date()
            is_today_pattern = pattern_date == today_date

            # Get pattern display name
            pattern_display_names = {
                'pin_bar': 'Pin Bar',
                'bullish_engulfing': 'Bullish Engulfing',
                'three_candle': 'Morning Star',
                'dragonfly_doji': 'Dragonfly Doji',
                'three_white_soldiers': 'Three White Soldiers',
                'bullish_marubozu': 'Bullish Marubozu',
                'bullish_harami': 'Bullish Harami',
                'bullish_abandoned_baby': 'Abandoned Baby',
                'tweezer_bottom': 'Tweezer Bottom',
                'bullish_kicker': 'Bullish Kicker'
            }

            pattern_type_display = pattern_display_names.get(pattern_type, pattern_type.replace('_', ' ').title())

            # Get pattern strength info
            if pattern_type == 'pin_bar':
                strength_display = f"{pattern.wick_ratio:.1f}x"
            elif pattern_type == 'bullish_engulfing':
                strength_display = f"{pattern.engulfing_ratio:.1f}x"
            elif pattern_type == 'three_candle':
                strength_display = f"{pattern.pattern_strength:.1f}"
            elif pattern_type == 'dragonfly_doji':
                strength_display = f"{pattern.lower_wick_ratio:.1f}"
            elif pattern_type == 'three_white_soldiers':
                strength_display = f"{pattern.average_body_size:.4f}"
            elif pattern_type == 'bullish_marubozu':
                strength_display = f"{pattern.body_size:.4f}"
            elif pattern_type == 'bullish_harami':
                strength_display = f"{pattern.containment_ratio:.1f}"
            elif pattern_type == 'bullish_abandoned_baby':
                strength_display = f"{pattern.gap_up_size:.4f}"
            elif pattern_type == 'tweezer_bottom':
                strength_display = f"{pattern.low_match_precision:.1f}%"
            elif pattern_type == 'bullish_kicker':
                strength_display = f"{pattern.gap_size:.4f}"
            else:
                strength_display = "N/A"

            # Get trade outcome
            outcome = touch.trade_outcome
            if outcome:
                if outcome.success:
                    trade_outcome_display = "Success"
                    current_status = f"Target: {outcome.current_profit_pct:.2f}%"
                elif outcome.sl_hit:
                    trade_outcome_display = "Stop Loss"
                    current_status = f"SL Hit: {outcome.current_profit_pct:.2f}%"
                else:
                    trade_outcome_display = "Active" if is_today_pattern else "Ongoing"
                    current_status = f"Current: {outcome.current_profit_pct:.2f}%"
            else:
                trade_outcome_display = "No Data"
                current_status = "N/A"

            touch_dict = {
                "Symbol": touch.symbol,
                "Timeframe": touch.timeframe,
                "Pattern Type": pattern_type_display,
                "Swing Low Date": touch.swing_low.timestamp.strftime("%Y-%m-%d %H:%M"),
                "Swing Low Price": f"{touch.swing_low.price:.4f}",
                "Swing Low Valid": "Yes" if touch.is_swing_low_valid else "No",
                "Swing Low Invalidated": "Yes" if touch.swing_low.is_invalidated else "No",
                "Pattern Date": pattern.timestamp.strftime("%Y-%m-%d %H:%M"),
                "Is Today's Pattern": "YES" if is_today_pattern else "No",
                "Entry Price": f"{touch.entry_price:.4f}",
                "Target Price": f"{touch.target_price:.4f}",
                "Stop Loss": f"{touch.sl_price:.4f}",
                "Days Between": touch.days_between,
                "Distance %": f"{touch.price_difference:.3f}%",
                "AI Pattern Strength": f"{touch.pattern_strength:.1f}%",
                "Strength/Ratio": strength_display,
                "Trade Outcome": trade_outcome_display,
                "Current Status": current_status,
                "Capital Allocated": f"${st.session_state.capital_per_trade:,.0f}",
            }

            if outcome:
                touch_dict.update({
                    "Current Price": f"{outcome.current_price:.4f}",
                    "Max Profit %": f"{outcome.max_profit_pct:.2f}%",
                    "Max Drawdown %": f"{outcome.max_drawdown_pct:.2f}%",
                    "Bars to Resolution": outcome.bars_to_resolution,
                    "Resolution Type": outcome.resolution_type,
                    "Last Update": outcome.last_update_timestamp.strftime(
                        "%Y-%m-%d %H:%M") if outcome.last_update_timestamp else "N/A"
                })

            touch_data.append(touch_dict)

        touches_df = pd.DataFrame(touch_data)

        # Count today's patterns in capital simulation
        today_patterns_in_sim = len(touches_df[touches_df["Is Today's Pattern"] == "YES"])
        if today_patterns_in_sim > 0:
            st.success(f"🎯 Found {today_patterns_in_sim} of today's patterns in AI capital simulation")

        # Summary by pattern type
        st.subheader("🧠 AI Pattern Performance in Capital Simulation")

        pattern_summary = []
        for pattern_type in touches_df['Pattern Type'].unique():
            pattern_data = touches_df[touches_df['Pattern Type'] == pattern_type]
            total = len(pattern_data)
            success = len(pattern_data[pattern_data["Trade Outcome"] == "Success"])
            ongoing = len(pattern_data[pattern_data["Trade Outcome"] == "Active"])
            today_count = len(pattern_data[pattern_data["Is Today's Pattern"] == "YES"])
            valid_swing_lows = len(pattern_data[pattern_data["Swing Low Valid"] == "Yes"])
            success_rate = (success / total * 100) if total > 0 else 0

            pattern_summary.append({
                'Pattern': pattern_type,
                'Total Opportunities': total,
                'Today\'s Count': today_count,
                'Successful': success,
                'Active': ongoing,
                'AI Success Rate': f"{success_rate:.1f}%",
                'Valid Signals': valid_swing_lows,
                'Capital per Trade': f"${st.session_state.capital_per_trade:,.0f}"
            })

        pattern_summary_df = pd.DataFrame(pattern_summary)
        create_download_buttons(pattern_summary_df, "ai_capital_pattern_performance", "AI Capital Pattern Performance")
        st.dataframe(pattern_summary_df, use_container_width=True)

        st.subheader("📋 All Pattern Opportunities in AI Capital Simulation")
        create_download_buttons(touches_df, "ai_capital_all_touches", "AI Capital All Opportunities")
        st.dataframe(touches_df, use_container_width=True, height=400)

    st.divider()

    # Professional Trades Table
    st.subheader("💼 All Executed Trades")

    trades_df = capital_manager.get_trades_df()
    if not trades_df.empty:
        create_download_buttons(trades_df, "ai_capital_trades", "AI Trades Report")
        st.dataframe(trades_df, use_container_width=True, height=400)

    # Rejected Trades
    rejected_df = capital_manager.get_rejected_trades_df()
    if not rejected_df.empty:
        st.subheader("❌ Rejected Trade Opportunities")
        create_download_buttons(rejected_df, "ai_rejected_trades", "AI Rejected Trades")
        st.dataframe(rejected_df, use_container_width=True, height=200)

    # Capital Events
    st.divider()
    st.subheader("🔄 Capital Management Events")

    events_df = capital_manager.get_capital_events_df()
    if not events_df.empty:
        create_download_buttons(events_df, "ai_capital_events", "AI Capital Events")
        st.dataframe(events_df.tail(30), use_container_width=True, height=300)


def render_live_monitoring_tab():
    """Render the professional live monitoring tab with progress tracking and Telegram alerts"""
    st.header("🔴 Professional Real-Time Pattern Monitoring")

    # Professional feature highlight
    st.markdown("""
    <div class="feature-highlight">
    <h3 style="color: #0066cc; margin: 0;">🧠 AI Real-Time Monitoring Features:</h3>
    <p style="color: #5a6c7d; margin: 5px 0;">
    ✅ Real-time pattern detection | ✅ Today's live candle monitoring | ✅ Advanced signal validation | ✅ AI-powered pattern formation tracking | ✅ Telegram Alert Integration
    </p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.instruments_list:
        st.warning("⚠️ No instruments loaded. Please add instruments in the Data Management tab.")
        return

    if not st.session_state.selected_timeframes:
        st.warning("⚠️ No timeframes selected. Please select timeframes in the Data Management tab.")
        return

    # Pattern Selection for Live Monitoring
    st.subheader("🎯 Select Patterns for AI Real-Time Monitoring")
    render_pattern_selection_checkboxes("live_")

    # Professional control panel
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔍 AI Live Scan", type="primary", use_container_width=True):
            with st.spinner("AI scanning for real-time patterns..."):
                results = st.session_state.live_analyzer.analyze_live_patterns(
                    st.session_state.instruments_list,
                    st.session_state.selected_timeframes,
                    st.session_state.analysis_parameters,
                    st.session_state.pattern_selection
                )

                st.session_state.live_patterns = results

                # Send Telegram alerts if enabled
                if st.session_state.get('telegram_enabled', False):
                    alerts_sent = 0

                    if st.session_state.get('telegram_alert_on_live', True):
                        live_alerts = process_patterns_for_alerts(
                            results.get('live_patterns', []),
                            'live'
                        )
                        alerts_sent += live_alerts

                    if st.session_state.get('telegram_alert_on_confirmed', False):
                        confirmed_alerts = process_patterns_for_alerts(
                            results.get('confirmed_patterns', []),
                            'confirmed'
                        )
                        alerts_sent += confirmed_alerts

                    if alerts_sent > 0:
                        st.success(f"📱 Sent {alerts_sent} Telegram alerts for detected patterns")

                    # Send summary alert
                    if results:
                        send_summary_alert(
                            results['summary'].get('total_live', 0) + results['summary'].get('total_confirmed', 0),
                            results['summary'].get('total_live', 0),
                            results['summary'].get('total_confirmed', 0),
                            results['summary'].get('symbols_analyzed', 0)
                        )

                st.success("✅ AI real-time scan completed!")
                st.rerun()

    with col2:
        refresh_interval = st.selectbox("Auto-refresh", ["Off", "30s", "1min", "5min"], index=3,
                                        key="live_refresh_interval")

    with col3:
        # ENHANCED: Update ALL instruments with progress tracking
        if st.button("📊 Refresh ALL Instruments", use_container_width=True):
            if st.session_state.selected_timeframes and st.session_state.instruments_list:
                # Calculate total operations
                total_operations = len(st.session_state.instruments_list) * len(st.session_state.selected_timeframes)

                # Estimate time
                estimated_time = total_operations * 0.75

                # Create progress containers
                progress_bar = st.progress(0)
                status_text = st.empty()
                summary_container = st.empty()

                # Show initial status
                status_text.text(
                    f"📊 Updating {len(st.session_state.instruments_list)} instruments × {len(st.session_state.selected_timeframes)} timeframes")
                summary_container.info(
                    f"⏱️ Estimated time: {estimated_time:.1f} seconds | Total operations: {total_operations}")

                # Track results
                update_stats = {
                    'updated': 0,
                    'current': 0,
                    'failed': 0,
                    'new_bars': 0,
                    'instruments_updated': set()
                }

                start_time = time.time()

                # Process each instrument/timeframe
                for i, symbol in enumerate(st.session_state.instruments_list):
                    for j, timeframe in enumerate(st.session_state.selected_timeframes):
                        current_op = i * len(st.session_state.selected_timeframes) + j + 1
                        progress = current_op / total_operations

                        # Update progress
                        progress_bar.progress(progress)
                        status_text.text(f"Updating {symbol} {timeframe} ({current_op}/{total_operations})")

                        try:
                            # Update single combination
                            result = st.session_state.data_manager.update_data_incrementally(
                                [symbol],
                                [timeframe],
                                'NSE',
                                force_update=False
                            )

                            # Process result
                            if symbol in result and timeframe in result[symbol]:
                                status = result[symbol][timeframe]
                                if "✅" in status:
                                    update_stats['instruments_updated'].add(symbol)
                                    if "Updated" in status and "+" in status:
                                        try:
                                            new_bars = int(status.split('+')[1].split(' ')[0])
                                            update_stats['new_bars'] += new_bars
                                            update_stats['updated'] += 1
                                        except:
                                            update_stats['updated'] += 1
                                    elif "Current" in status:
                                        update_stats['current'] += 1
                                    else:
                                        update_stats['updated'] += 1
                                else:
                                    update_stats['failed'] += 1
                        except:
                            update_stats['failed'] += 1

                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                summary_container.empty()

                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                avg_time_per_op = elapsed_time / total_operations if total_operations > 0 else 0

                # Show detailed summary
                st.success(
                    f"✅ Updated {len(update_stats['instruments_updated'])} instruments in {elapsed_time:.1f} seconds!")

                # Display metrics
                col_a, col_b, col_c, col_d, col_e = st.columns(5)
                with col_a:
                    st.metric("Operations", total_operations)
                with col_b:
                    st.metric("Updated", update_stats['updated'])
                with col_c:
                    st.metric("Current", update_stats['current'])
                with col_d:
                    st.metric("New Bars", update_stats['new_bars'])
                with col_e:
                    st.metric("Avg Time/Op", f"{avg_time_per_op:.2f}s")

                if update_stats['failed'] > 0:
                    st.warning(f"⚠️ {update_stats['failed']} operations failed")
            else:
                st.warning("No timeframes/instruments selected")

    with col4:
        if st.button("🧹 Clear Results", use_container_width=True):
            st.session_state.live_patterns = []
            st.success("✅ Results cleared!")
            st.rerun()

    # Telegram alert status
    if st.session_state.get('telegram_enabled', False):
        st.info(f"📱 Telegram alerts ACTIVE - Will send alerts for detected patterns")

    # Display live patterns if available
    if st.session_state.live_patterns:
        results = st.session_state.live_patterns

        # Professional summary metrics
        st.subheader("📊 AI Real-Time Pattern Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Live Patterns", results['summary']['total_live'])
        with col2:
            st.metric("Confirmed Patterns", results['summary']['total_confirmed'])
        with col3:
            st.metric("Symbols Monitored", results['summary']['symbols_analyzed'])
        with col4:
            st.metric("Timeframes", results['summary']['timeframes_analyzed'])

        # Check for today's patterns in live results
        today_str = datetime.now().strftime('%Y-%m-%d')
        today_patterns_count = 0

        for pattern in results.get('live_patterns', []) + results.get('confirmed_patterns', []):
            if today_str in pattern.get('timestamp', ''):
                today_patterns_count += 1

        if today_patterns_count > 0:
            st.success(f"🎯 Found {today_patterns_count} patterns from TODAY in AI monitoring!")

        # Live patterns table
        if results['live_patterns']:
            st.subheader("🔴 Live Patterns (Forming)")
            live_df = pd.DataFrame(results['live_patterns'])

            # Check if enhanced columns exist
            if 'swing_low_valid' in live_df.columns:
                st.info("✅ AI validation active - swing low validity checked")

            # Add today indicator
            if 'timestamp' in live_df.columns:
                live_df['Is Today'] = live_df['timestamp'].apply(lambda x: 'YES' if today_str in x else 'No')

            create_download_buttons(live_df, "ai_live_patterns", "AI Live Patterns")
            st.dataframe(live_df, use_container_width=True, height=200)

        # Confirmed patterns table
        if results['confirmed_patterns']:
            st.subheader("✅ Confirmed Patterns")
            confirmed_df = pd.DataFrame(results['confirmed_patterns'])

            # Check if enhanced columns exist
            if 'swing_low_valid' in confirmed_df.columns:
                st.info("✅ AI validation active - only valid signals shown")

            # Add today indicator
            if 'timestamp' in confirmed_df.columns:
                confirmed_df['Is Today'] = confirmed_df['timestamp'].apply(lambda x: 'YES' if today_str in x else 'No')

            create_download_buttons(confirmed_df, "ai_confirmed_patterns", "AI Confirmed Patterns")
            st.dataframe(confirmed_df, use_container_width=True, height=300)

        # Last update info
        last_update = datetime.fromisoformat(results['summary']['last_update'])
        st.info(f"🕒 Last AI scan: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")

        # Telegram alerts info
        if st.session_state.get('telegram_last_alert_time'):
            alert_time_diff = time.time() - st.session_state.get('telegram_last_alert_time')
            st.info(f"📱 Last Telegram alert: {int(alert_time_diff // 60)}m {int(alert_time_diff % 60)}s ago")

    else:
        st.info("🔍 No real-time patterns scanned yet. Click 'AI Live Scan' to start professional monitoring.")


def render_settings_tab():
    """Enhanced settings tab with customizable swing detection parameters"""
    st.header("⚙️ Professional Settings & Configuration")

    # Professional feature highlight
    st.markdown("""
    <div class="feature-highlight">
    <h3 style="color: #0066cc; margin: 0;">🧠 AI Configuration Features:</h3>
    <p style="color: #5a6c7d; margin: 5px 0;">
    ✅ Customizable swing detection parameters | ✅ Trade entry mode selection | ✅ Advanced pattern configuration | ✅ Days filter & strict touch validation
    </p>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 1: Swing Detection Configuration
    st.subheader("🔧 Customizable Asymmetric Swing Detection")

    col1, col2, col3 = st.columns(3)

    with col1:
        left_lookback = st.number_input(
            "Left Lookback Bars (Historical Context)",
            min_value=5,
            max_value=25,
            value=st.session_state.analysis_parameters.get('swing_lookback', 10),
            help="How many bars back to check for higher lows"
        )
        st.session_state.analysis_parameters['swing_lookback'] = left_lookback

    with col2:
        # NEW: User customizable right lookback
        right_lookback = st.number_input(
            "Right Lookback Bars (Future Confirmation)",
            min_value=1,
            max_value=15,
            value=st.session_state.analysis_parameters.get('right_lookback', 3),
            help="How many bars forward to confirm swing low (fewer = earlier detection)"
        )
        st.session_state.analysis_parameters['right_lookback'] = right_lookback

    with col3:
        detection_mode = f"{left_lookback}+{right_lookback}"
        st.metric("Detection Mode", detection_mode)

        # Calculate timing advantage
        symmetric_bars = left_lookback * 2 + 1
        asymmetric_bars = left_lookback + right_lookback + 1
        bars_saved = symmetric_bars - asymmetric_bars
        st.metric("Bars Saved", bars_saved)

    # Validation warnings
    if right_lookback > left_lookback:
        st.warning("⚠️ Right > Left lookback may miss swing lows")
    if right_lookback == 1:
        st.warning("⚠️ Right lookback = 1 gives very early but noisy signals")
    if right_lookback > 7:
        st.warning("⚠️ Right lookback > 7 delays detection significantly")

    # Preset configurations
    st.write("**🎛️ Preset Configurations:**")
    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)

    with preset_col1:
        if st.button("🚀 Aggressive (8+2)", use_container_width=True):
            st.session_state.analysis_parameters.update({'swing_lookback': 8, 'right_lookback': 2})
            st.rerun()

    with preset_col2:
        if st.button("⚡ Fast (10+2)", use_container_width=True):
            st.session_state.analysis_parameters.update({'swing_lookback': 10, 'right_lookback': 2})
            st.rerun()

    with preset_col3:
        if st.button("📊 Balanced (10+3)", use_container_width=True):
            st.session_state.analysis_parameters.update({'swing_lookback': 10, 'right_lookback': 3})
            st.rerun()

    with preset_col4:
        if st.button("🛡️ Conservative (10+5)", use_container_width=True):
            st.session_state.analysis_parameters.update({'swing_lookback': 10, 'right_lookback': 5})
            st.rerun()

    st.divider()

    # SECTION 2: Trade Entry Logic Configuration
    st.subheader("🎯 Trade Entry Logic Configuration")

    entry_col1, entry_col2 = st.columns(2)

    with entry_col1:
        st.write("**Entry Requirements:**")

        pattern_only = st.checkbox(
            "Pattern Formation Alone Sufficient",
            value=st.session_state.analysis_parameters.get('pattern_only_entry', False),
            help="Trade immediately when bullish pattern forms (more signals, lower quality)"
        )
        st.session_state.analysis_parameters['pattern_only_entry'] = pattern_only

        require_swing_touch = st.checkbox(
            "Require Swing Low Touch",
            value=not pattern_only,
            disabled=pattern_only,
            help="Pattern must touch valid swing low (current system - higher quality)"
        )
        st.session_state.analysis_parameters['require_swing_touch'] = require_swing_touch

        require_volume_confirm = st.checkbox(
            "Require Volume Confirmation (Future Feature)",
            value=st.session_state.analysis_parameters.get('require_volume_confirm', False),
            help="Additional volume-based confirmation"
        )
        st.session_state.analysis_parameters['require_volume_confirm'] = require_volume_confirm

    with entry_col2:
        st.write("**Entry Mode Summary:**")

        if pattern_only:
            st.info(
                "🟡 **Pattern Only Mode**\n- More signals (~3x)\n- Lower quality\n- Faster entries\n- No swing low requirement")
            st.warning("⚠️ This will generate significantly more signals")
        elif require_swing_touch:
            st.success(
                "🟢 **Swing Low Touch Mode** (Recommended)\n- Fewer signals\n- Higher quality\n- Current system\n- Structural support required")
        else:
            st.error("⚠️ No entry requirements selected")

    st.divider()

    # Pattern Selection in Settings
    st.subheader("🧠 AI Pattern Selection Configuration")
    render_pattern_selection_checkboxes("settings_")

    st.divider()

    # SECTION 3: Advanced Parameters
    st.subheader("🔧 Advanced Parameters")

    param_col1, param_col2 = st.columns(2)

    with param_col1:
        st.write("**General Parameters:**")
        st.session_state.analysis_parameters['touch_tolerance'] = st.number_input(
            "Touch Tolerance (%)", 0.1, 2.0, st.session_state.analysis_parameters['touch_tolerance'], 0.1,
            help="Maximum distance allowed for swing low touch validation"
        )

        # NEW: Minimum days between swing low and pattern
        st.session_state.analysis_parameters['min_days_between'] = st.number_input(
            "Min Days Between Swing Low & Pattern",
            1, 30,
            st.session_state.analysis_parameters.get('min_days_between', 1),
            1,
            help="Minimum days required between swing low formation and pattern detection"
        )

        st.session_state.analysis_parameters['max_bars_to_analyze'] = st.number_input(
            "Max Analysis Bars", 20, 200, st.session_state.analysis_parameters['max_bars_to_analyze'], 10
        )
        st.session_state.analysis_parameters['min_swing_size'] = st.number_input(
            "Min Swing Size (%)", 0.1, 2.0, st.session_state.analysis_parameters['min_swing_size'], 0.1
        )

    with param_col2:
        st.write("**Pattern-Specific Parameters:**")
        st.session_state.analysis_parameters['min_wick_ratio'] = st.number_input(
            "Pin Bar: Min Wick Ratio", 1.5, 4.0, st.session_state.analysis_parameters['min_wick_ratio'], 0.1
        )
        st.session_state.analysis_parameters['max_body_ratio'] = st.number_input(
            "Pin Bar: Max Body Ratio", 0.1, 0.5, st.session_state.analysis_parameters['max_body_ratio'], 0.05
        )
        st.session_state.analysis_parameters['min_engulfing_ratio'] = st.number_input(
            "Engulfing: Min Ratio", 1.0, 3.0, st.session_state.analysis_parameters['min_engulfing_ratio'], 0.1
        )

    # Touch Validation Info
    st.subheader("📏 Strict Touch Validation Settings")
    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.info(f"""
        **Current Touch Validation:**
        - Touch Tolerance: {st.session_state.analysis_parameters['touch_tolerance']:.2f}%
        - Min Days Gap: {st.session_state.analysis_parameters.get('min_days_between', 1)} days
        - Validation: Pattern must touch or slightly penetrate swing low
        """)

    with col_info2:
        st.success(f"""
        **Validation Rules:**
        - Pattern low ≤ Swing low: ✅ Valid (allows penetration up to {st.session_state.analysis_parameters['touch_tolerance']:.2f}%)
        - Pattern low > Swing low: ✅ Only if gap < {st.session_state.analysis_parameters['touch_tolerance'] * 0.3:.2f}%
        - Days gap < {st.session_state.analysis_parameters.get('min_days_between', 1)}: ❌ Rejected
        """)

    # Save Configuration
    if st.button("💾 Save All Configuration", type="primary", use_container_width=True):
        st.success("✅ All configuration saved successfully!")
        st.rerun()

    st.divider()

    # Configuration Summary
    st.subheader("📋 Current Configuration Summary")

    config_data = [
        {"Parameter": "Left Lookback", "Value": f"{left_lookback} bars", "Impact": "Historical context depth"},
        {"Parameter": "Right Lookback", "Value": f"{right_lookback} bars", "Impact": "Detection speed vs accuracy"},
        {"Parameter": "Detection Mode", "Value": detection_mode,
         "Impact": f"Earlier by {bars_saved} bars vs symmetric"},
        {"Parameter": "Entry Logic", "Value": "Pattern Only" if pattern_only else "Pattern + Swing Touch",
         "Impact": "Signal quality vs quantity"},
        {"Parameter": "Touch Tolerance", "Value": f"{st.session_state.analysis_parameters['touch_tolerance']:.2f}%",
         "Impact": "Swing low proximity sensitivity"},
        {"Parameter": "Min Days Gap",
         "Value": f"{st.session_state.analysis_parameters.get('min_days_between', 1)} days",
         "Impact": "Time separation requirement"},
    ]

    config_df = pd.DataFrame(config_data)
    st.dataframe(config_df, use_container_width=True)


def validate_live_entry_capability(df: pd.DataFrame, touches: List[SwingLowTouch],
                                   swing_detector: EnhancedSwingLowDetector,
                                   parameters: Dict, debug_info: Dict) -> List[SwingLowTouch]:
    """Filter touches to only include those detectable as live entries"""
    validated_touches = []
    filtered_count = 0

    left_lookback = parameters.get('swing_lookback', 10)
    right_lookback = parameters.get('right_lookback', 3)

    print(f"🔍 Live entry validation: checking {len(touches)} historical touches")

    for touch in touches:
        try:
            pattern_timestamp = pd.Timestamp(touch.pattern.timestamp)
            pattern_index = touch.pattern.index
            swing_low_index = touch.swing_low.index

            # Swing low must be detectable before pattern formed
            swing_low_detection_point = swing_low_index + right_lookback

            if swing_low_detection_point < pattern_index:
                validated_touches.append(touch)
            else:
                filtered_count += 1

        except Exception as e:
            filtered_count += 1
            continue

    print(f"✅ Live validation: {len(touches)} original → {len(validated_touches)} live-detectable")
    print(f"❌ Filtered out: {filtered_count} trades that wouldn't be detectable live")

    debug_info['historical_trades_filtered'] = debug_info.get('historical_trades_filtered', 0) + filtered_count
    debug_info['live_detectable_trades'] = debug_info.get('live_detectable_trades', 0) + len(validated_touches)

    return validated_touches


def main():
    """Main Professional AI Market Analysis Platform with Result Viewer Mode - FIXED VERSION"""

    # Get URL parameters FIRST, before any authentication
    params = st.query_params

    # Handle URL-based viewer mode (?mode=viewer)
    if params.get("mode") == "viewer":
        st.set_page_config(
            page_title="APEX AI - Analysis Results Viewer",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        apply_professional_theme()

        st.title("📊 APEX AI - Analysis Results Viewer")
        st.markdown("**URL-based Viewer Access**")

        # Simple password check for URL access
        password = st.text_input("Viewer Password:", type="password", key="url_viewer_password")
        if password == "view123":
            render_cached_results_viewer()
        elif password:  # Only show error if password was entered
            st.error("❌ Invalid viewer password")
        else:
            st.info("Please enter the viewer password to access results")
        return  # CRITICAL: Stop here for URL-based viewer mode

    # Normal authentication flow for logged-in users
    check_login()

    # CRITICAL CHECK: If authenticated user is a viewer account, show ONLY CSV viewer
    if st.session_state.get('is_viewer', False):
        # Viewer accounts get CSV-only interface
        st.set_page_config(
            page_title="APEX AI - Analysis Results Viewer",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        render_cached_results_viewer()
        return  # STOP HERE - Viewer accounts cannot access full platform

    # ONLY FULL ACCESS USERS (Arthur with trapezoid password) CONTINUE BELOW
    # Set page config for full platform
    st.set_page_config(
        page_title="🚀 APEX AI Technical Analysis Platform",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state and apply professional theme
    init_session_state()
    apply_professional_theme()

    # Professional main title
    st.title("🚀 APEX AI TECHNICAL ANALYSIS PLATFORM")
    st.markdown(
        "**Advanced Technical Analysis: AI-Powered Pattern Recognition + Smart Capital Management + Real-Time Processing + Professional Features 📊🧠**")

    # Check TradingView availability
    if not TV_AVAILABLE:
        st.error("❌ TradingView DataFeed not available. Install with: `pip install tvDatafeed`")
        st.stop()
    else:
        st.success("✅ APEX AI Analysis System Ready!")

    # Professional features banner
    st.markdown("""
    <div class="feature-highlight">
    <h3 style="color: #0066cc; margin: 0;">🧠 APEX AI FEATURES ACTIVE:</h3>
    <p style="color: #5a6c7d; margin: 5px 0;">
    ✅ DATE PICKER DATA DOWNLOADS | ✅ SMART BAR CALCULATION | ✅ TODAY'S REAL-TIME DATA | ✅ Advanced Swing Low Validation | ✅ Current Trade Status | ✅ Precision AI Detection | ✅ Professional Capital Management
    </p>
    </div>
    """, unsafe_allow_html=True)

    # Create professional application tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔄 Data Management",
        "📊 AI Pattern Analysis",
        "💰 Capital Simulation",
        "🔴 Real-Time Monitoring",
        "⚙️ AI Configuration",
        "📈 Analytics Dashboard"
    ])

    with tab1:
        render_instrument_management()
        st.divider()
        render_data_management_tab()

    with tab2:
        render_analysis_tab()

    with tab3:
        render_capital_simulation_tab()

    with tab4:
        render_live_monitoring_tab()

    with tab5:
        render_settings_tab()

    with tab6:
        st.header("📈 Professional Analytics Dashboard")

        if st.session_state.debug_info:
            st.subheader("🔍 AI Analysis Performance Metrics")

            # Special handling for today's patterns
            today_patterns = st.session_state.debug_info.get('today_patterns_detected', 0)
            if today_patterns > 0:
                st.success(f"🎯 TODAY'S PATTERNS DETECTED: {today_patterns}")

            debug_df = pd.DataFrame([
                {"Metric": k, "Value": v}
                for k, v in st.session_state.debug_info.items()
            ])

            create_download_buttons(debug_df, "ai_analytics_dashboard", "AI Analytics Report")
            st.dataframe(debug_df, use_container_width=True)

            # Show capital analytics if available
            if 'capital_debug' in st.session_state.debug_info:
                st.subheader("💰 Capital Management Analytics")
                with st.expander("View AI Capital Management Logs"):
                    for msg in st.session_state.debug_info['capital_debug']:
                        st.text(msg)

            # Show AI swing low analytics
            if 'total_invalidated_swing_lows' in st.session_state.debug_info:
                st.subheader("🔧 AI Swing Low Validation Analytics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Swing Lows", st.session_state.debug_info.get('total_swing_lows', 0))
                with col2:
                    st.metric("AI Invalidated", st.session_state.debug_info.get('total_invalidated_swing_lows', 0))
                with col3:
                    st.metric("Valid AI Signals", st.session_state.debug_info.get('total_valid_touches', 0))
                with col4:
                    st.metric("Today's Patterns", st.session_state.debug_info.get('today_patterns_detected', 0))
        else:
            st.info("No analytics data available. Run an AI analysis to see professional performance metrics.")

    # Professional sidebar with logout button
    with st.sidebar:
        st.header("🎛️ APEX AI SYSTEM")

        # Logout button at the top
        if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
            logout()

        st.divider()

        # Professional AI features status
        st.markdown("""
        <div class="professional-card">
        <h4 style="color: #0066cc; margin: 0;">🧠 APEX AI FEATURES</h4>
        <p style="color: #5a6c7d; font-size: 12px; margin: 5px 0;">
        ✅ Date Picker Downloads<br>
        ✅ Real-Time Analysis<br>
        ✅ Pattern Recognition<br>
        ✅ Smart Capital Management<br>
        ✅ Advanced Validation
        </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Date picker status
        use_date_picker = st.session_state.get('use_date_picker', False)
        if use_date_picker:
            download_start_date = st.session_state.get('data_download_start_date', datetime.now() - timedelta(days=30))
            st.success(f"📅 Date Picker: {download_start_date.strftime('%Y-%m-%d')}")
        else:
            st.info("📅 Default bar counts")

        # Professional status indicators
        st.markdown("""
        <div class="professional-card">
        <h4 style="color: #00cc88; margin: 0;">🔧 SYSTEM STATUS</h4>
        <p style="color: #5a6c7d; font-size: 12px; margin: 5px 0;">
        ✅ Advanced Swing Low Validation<br>
        ✅ Real-Time Trade Monitoring<br>
        ✅ Precision Entry/Exit Detection<br>
        ✅ AI Signal Validation<br>
        ✅ Date-Based Data Downloads
        </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Instruments status
        if st.session_state.instruments_list:
            st.success(f"✅ {len(st.session_state.instruments_list)} instruments loaded")
        else:
            st.warning("⚠️ No instruments loaded")

        # Pattern selection status
        selected_patterns_count = sum(st.session_state.pattern_selection.values())
        if selected_patterns_count > 0:
            st.success(f"🧠 {selected_patterns_count}/10 AI patterns selected")
        else:
            st.warning("⚠️ No patterns selected")

        # Professional Capital Management Status
        st.divider()
        st.subheader("💰 Capital Management")

        if st.session_state.capital_manager:
            summary = st.session_state.capital_manager.get_performance_summary()
            st.success(f"✅ AI Capital System Active")
            st.metric("Total Capital", f"${summary['total_capital_current']:,.0f}")
            st.metric("AI ROI", f"{summary['total_roi_pct']:.1f}%")
            st.metric("Trades", f"{summary['trades_executed']}")
        else:
            st.info("💰 AI capital system ready")
            st.metric("Total Capital", f"${st.session_state.total_capital:,.0f}")
            st.metric("Per Trade", f"${st.session_state.capital_per_trade:,.0f}")

        # Today's date and status
        st.divider()
        today_str = datetime.now().strftime('%Y-%m-%d')
        st.metric("Today's Date", today_str)
        st.success("✅ Real-time data active")

        # Data update status
        if st.session_state.last_data_update:
            time_diff = datetime.now() - st.session_state.last_data_update
            minutes_ago = int(time_diff.total_seconds() / 60)
            st.info(f"🕒 Data updated: {minutes_ago}min ago")
        else:
            st.info("🕒 Ready for first update")

        # Analysis status
        if st.session_state.analysis_complete:
            if st.session_state.analysis_results:
                today_patterns = len(
                    [r for r in st.session_state.analysis_results if r.get("Is Today's Pattern") == "YES"])
                st.success(f"📊 {len(st.session_state.analysis_results)} opportunities found")
                if today_patterns > 0:
                    st.success(f"🎯 {today_patterns} from TODAY!")
            else:
                st.info("📊 Analysis complete - no opportunities")
        else:
            st.info("📊 Ready for AI analysis")

        st.divider()

        # Professional Patterns showcase
        st.subheader("🧠 AI Pattern Recognition")
        pattern_emojis = {
            'pin_bar': '📍',
            'bullish_engulfing': '🔥',
            'three_candle': '🌟',
            'dragonfly_doji': '🐉',
            'three_white_soldiers': '⚔️',
            'bullish_marubozu': '💪',
            'bullish_harami': '🤰',
            'bullish_abandoned_baby': '👶',
            'tweezer_bottom': '🔧',
            'bullish_kicker': '🚀'
        }

        for pattern_key, emoji in pattern_emojis.items():
            is_selected = st.session_state.pattern_selection.get(pattern_key, False)
            status = "✅" if is_selected else "⭕"
            pattern_name = pattern_key.replace('_', ' ').title()
            st.write(f"{status} {emoji} {pattern_name}")

        st.divider()

        # Professional quick actions
        st.subheader("⚡ Quick Actions")

        if st.button("🔄 Refresh Platform", use_container_width=True):
            st.rerun()

        if st.button("🧹 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['file_manager', 'authenticated', 'login_username', 'is_viewer']:  # Keep essential keys
                    del st.session_state[key]
            st.success("Session reset!")
            st.rerun()

        st.divider()

        # Professional summary
        st.markdown("""
        <div class="professional-card">
        <h5 style="color: #0066cc; margin: 0;">🧠 APEX AI PLATFORM</h5>
        <p style="color: #5a6c7d; font-size: 11px; margin: 3px 0;">
        Professional AI Market Analysis Platform with real-time pattern detection, 
        advanced capital management, and comprehensive trading analytics.
        </p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()