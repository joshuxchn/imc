from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import json
import math

class Trader:
    def run(self, state: TradingState) -> tuple[Dict[str, List[Order]], int, str]:
        """
        This reconfigured algorithm is designed to address previous losses.
        
        Key modifications:
         • SQUID_INK:
             - Uses a dual moving average approach: a short-term MA (last 5 ticks) and a long-term MA (last 20 ticks).
             - It triggers a trade only if the difference between the two averages exceeds a dynamic threshold 
               (the greater of a fixed minimum or a fraction of the long-term volatility).
             - A cooldown period (e.g., 100 ticks) is enforced so that trades are not executed too frequently.
         • KELP:
             - Uses a 10-tick moving average; a trade is triggered only if the current price is at least 1% away from the MA.
         • RAINFOREST_RESIN:
             - Remains untraded because of its stable nature.
         
        The algorithm uses traderData to persist price histories and the timestamp of the last trade for each product.
        It returns a tuple containing the orders dict, a conversion request value (here 0), and updated traderData.
        """
        # ----------------------
        # Step 1: Initialize result container
        result: Dict[str, List[Order]] = {}

        # ----------------------
        # Step 2: Load persistent state from traderData.
        # We expect traderData to be a JSON string that holds a dictionary for each product.
        # Each product’s data contains:
        #   "history": a list of past mid-prices, and 
        #   "last_trade_tick": the last tick (state.timestamp) when we executed a trade.
        try:
            persistent = json.loads(state.traderData) if state.traderData else {}
        except Exception as e:
            print("Failed to decode traderData; reinitializing history. Error:", e)
            persistent = {}

        # Ensure that for every product in the current market, we have a persistent record.
        for product in state.order_depths.keys():
            if product not in persistent:
                persistent[product] = {}
            if "history" not in persistent[product]:
                persistent[product]["history"] = []
            if "last_trade_tick" not in persistent[product]:
                persistent[product]["last_trade_tick"] = -float('inf')  # initialize to very old tick

        # The current tick is taken from state.timestamp.
        current_tick = state.timestamp

        # ----------------------
        # Step 3: Update Price Histories
        # For each product, we extract a current mid-price from the available order depth
        # and append it to that product's history.
        for product, order_depth in state.order_depths.items():
            if order_depth.buy_orders and order_depth.sell_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_bid + best_ask) // 2
            elif order_depth.buy_orders:
                mid_price = max(order_depth.buy_orders.keys())
            elif order_depth.sell_orders:
                mid_price = min(order_depth.sell_orders.keys())
            else:
                mid_price = 0  # fallback if no data present

            persistent[product]["history"].append(mid_price)
            # Limit the stored history to the last 50 ticks to avoid excessive memory usage.
            if len(persistent[product]["history"]) > 50:
                persistent[product]["history"] = persistent[product]["history"][-50:]

        # ----------------------
        # Step 4: Process Trading Strategies for Each Product
        for product in state.order_depths.keys():
            orders: List[Order] = []
            order_depth: OrderDepth = state.order_depths[product]
            history = persistent[product]["history"]
            last_trade_tick = persistent[product]["last_trade_tick"]

            # Enforce a cooldown period so that we only trade if it’s been enough ticks since the last trade.
            cooldown = 100  # e.g., at least 100 ticks must pass between trades.
            if current_tick - last_trade_tick < cooldown:
                result[product] = orders
                continue

            if product == "SQUID_INK":
                # We trade SQUID_INK only if we have at least 20 price observations.
                if len(history) >= 20:
                    # Compute moving averages:
                    short_window = history[-5:]      # short-term: last 5 ticks
                    long_window = history[-20:]      # long-term: last 20 ticks
                    short_ma = sum(short_window) / len(short_window)
                    long_ma = sum(long_window) / len(long_window)

                    # Calculate volatility for the long window (standard deviation).
                    variance = sum((p - long_ma) ** 2 for p in long_window) / len(long_window)
                    std_long = math.sqrt(variance)

                    # Define a dynamic threshold: we want the MA difference to be at least 0.5 or 0.5 * volatility.
                    threshold = max(0.5, 0.5 * std_long)

                    # Check for a sell signal: If the short-term average is significantly above the long-term average,
                    # expect a reversion downward.
                    if short_ma - long_ma > threshold:
                        if order_depth.buy_orders:
                            best_bid = max(order_depth.buy_orders.keys())
                            # Sell order: negative quantity indicates a sell.
                            orders.append(Order(product, best_bid, -1))
                            persistent[product]["last_trade_tick"] = current_tick
                            print(f"[SQUID_INK] SELL signal: short MA {short_ma:.2f} > long MA {long_ma:.2f} by {short_ma - long_ma:.2f}")
                    # Check for a buy signal: If the long-term average is significantly above the short-term average,
                    # expect a reversion upward.
                    elif long_ma - short_ma > threshold:
                        if order_depth.sell_orders:
                            best_ask = min(order_depth.sell_orders.keys())
                            orders.append(Order(product, best_ask, 1))
                            persistent[product]["last_trade_tick"] = current_tick
                            print(f"[SQUID_INK] BUY signal: long MA {long_ma:.2f} > short MA {short_ma:.2f} by {long_ma - short_ma:.2f}")

            elif product == "KELP":
                # For KELP, we require at least 10 ticks to compute a reliable 10-tick moving average.
                if len(history) >= 10:
                    window = history[-10:]
                    avg_price = sum(window) / len(window)
                    current_price = window[-1]
                    # Compute percentage deviation.
                    deviation = (current_price - avg_price) / avg_price if avg_price != 0 else 0

                    # Use a threshold of 1% deviation to trigger trades.
                    if deviation < -0.01:
                        if order_depth.sell_orders:
                            best_ask = min(order_depth.sell_orders.keys())
                            orders.append(Order(product, best_ask, 1))
                            persistent[product]["last_trade_tick"] = current_tick
                            print(f"[KELP] BUY signal: current {current_price} is {deviation:.2%} below avg {avg_price:.2f}")
                    elif deviation > 0.01:
                        if order_depth.buy_orders:
                            best_bid = max(order_depth.buy_orders.keys())
                            orders.append(Order(product, best_bid, -1))
                            persistent[product]["last_trade_tick"] = current_tick
                            print(f"[KELP] SELL signal: current {current_price} is {deviation:.2%} above avg {avg_price:.2f}")
            else:
                # For RAINFOREST_RESIN, we choose to remain passive.
                orders = []

            result[product] = orders

        # ----------------------
        # Step 5: Serialize the updated persistent state to pass forward.
        traderData = json.dumps(persistent)
        # No conversion requests in this algorithm.
        conversions = 0

        return result, conversions, traderData
