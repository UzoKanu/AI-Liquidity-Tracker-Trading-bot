import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time

# MetaTrader 5 connection parameters
MT5_SERVER = 'Deriv-Demo'
MT5_LOGIN = 25681005
MT5_PASSWORD = 'Slizzer1$'

# Initialize MetaTrader 5 connection
if not mt5.initialize(server=MT5_SERVER, login=MT5_LOGIN, password=MT5_PASSWORD):
    print("MetaTrader5 initialization failed")
    mt5.shutdown()
else:
    print("Connected to MetaTrader5")

# Strategy configuration
SYMBOL = 'SOLUSD.0'  # Change to your platform's symbol for Solana
LOT_SIZE = 20.0    # Adjust based on your platform's lot size for SOL
RISK_REWARD_RATIO = 2
ATR_PERIOD = 14

# Check if the symbol is available and select it
def check_and_select_symbol(symbol):
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol: {symbol}. Error: {mt5.last_error()}")
        return False
    return True

# Get account balance
def get_account_info():
    account_info = mt5.account_info()
    if account_info:
        return account_info.balance
    else:
        print(f"Failed to get account info: {mt5.last_error()}")
        return None

# Calculate ATR to estimate volatility
def calculate_atr(symbol, period=ATR_PERIOD):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, period + 1)
    if rates is None or len(rates) < period:
        print(f"Failed to get rates for ATR calculation: {mt5.last_error()}")
        return None
    df = pd.DataFrame(rates)
    df['tr'] = np.maximum(df['high'] - df['low'],
                          np.maximum(np.abs(df['high'] - df['close'].shift()), np.abs(df['low'] - df['close'].shift())))
    atr = df['tr'].rolling(window=period).mean().iloc[-1]
    return atr

# Identify trade setups based on high-confidence conditions (trend, strong rejection, etc.)
def identify_trade_setup(symbol):
    # Example: Look for significant trend and strong price rejection
    rates_h1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 5)
    if rates_h1 is None or len(rates_h1) < 5:
        print(f"Failed to get recent rates: {mt5.last_error()}")
        return None

    df_h1 = pd.DataFrame(rates_h1)

    # Condition 1: Check for strong trend
    trend = df_h1['close'].iloc[-1] > df_h1['close'].mean()  # Price above moving average

    # Condition 2: Check for strong rejection in last candle (A+ setup)
    last_candle = df_h1.iloc[-1]
    upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
    lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
    body_size = abs(last_candle['open'] - last_candle['close'])

    # A+ trade condition: Strong wick compared to the body (rejection from key level)
    if trend and (upper_wick > body_size * 2 or lower_wick > body_size * 2):
        return 'BUY' if trend else 'SELL'

    return None

# Place trade with dynamic SL and TP (1:2 risk:reward ratio)
def place_order(symbol, trade_type, lot_size, price, sl, tp):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return

    # Ensure price, sl, and tp are correctly formatted
    price = round(price / symbol_info.point) * symbol_info.point
    sl = round(sl / symbol_info.point) * symbol_info.point
    tp = round(tp / symbol_info.point) * symbol_info.point

    order_request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': lot_size,
        'price': price,
        'sl': sl,
        'tp': tp,
        'deviation': 50,
        'type': mt5.ORDER_TYPE_BUY if trade_type == 'BUY' else mt5.ORDER_TYPE_SELL,
        'magic': 123456,
        'comment': 'Auto Trade',
        'type_filling': mt5.ORDER_FILLING_FOK,
        'type_time': mt5.ORDER_TIME_GTC
    }

    result = mt5.order_send(order_request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"Order successfully placed: {result}")
        return True
    else:
        print(f"Order failed: Error code: {result.retcode}")
        print(f"Order details: {result}")
        return False

# Main trading strategy
def trading_strategy(symbol):
    if not check_and_select_symbol(symbol):
        return

    # Get account balance and ATR
    atr = calculate_atr(symbol)
    if atr is None:
        return

    trade_signal = identify_trade_setup(symbol)
    if trade_signal is None:
        print("Scanning Solana.")
        return

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"Failed to get tick info for symbol: {symbol}")
        return

    price = tick.ask if trade_signal == 'BUY' else tick.bid
    stop_loss_pips = atr  # ATR as stop loss
    stop_loss = price - stop_loss_pips if trade_signal == 'BUY' else price + stop_loss_pips
    take_profit = price + (2 * stop_loss_pips) if trade_signal == 'BUY' else price - (2 * stop_loss_pips)

    # Place the order with fixed lot size
    order_placed = place_order(symbol, trade_signal, LOT_SIZE, price, stop_loss, take_profit)

    return order_placed

# Main loop to run the strategy every 3 hours
def run_strategy():
    try:
        while True:
            order_completed = False
            while not order_completed:
                order_completed = trading_strategy(SYMBOL)
                if order_completed:
                    print("Waiting for trade to complete before next setup...")
                    time.sleep(10800)  # 3 hours wait
    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        mt5.shutdown()
        print("Disconnected from MetaTrader 5.")

# Start the strategy
run_strategy()
