# trader.py

from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict
import json
import math

class Trader:
    """
    This Trader class implements a round 1 trading algorithm for the IMC Prosperity challenge.
    
    Strategy Overview:
      - SQUID_INK: Maintain a price history and compute a moving average (window=20) and standard deviation.
        When the normalized deviation (current price – average divided by standard deviation) is less than -1.5, buy;
        if it is greater than 1.5, sell.
      
      - KELP: Use a short-term moving average (window=10) and percentage deviation threshold of 1%. If the current price is significantly 
        below the moving average, buy; if it is above, sell.
      
      - RAINFOREST_RESIN: Price is very stable; no active trading is performed.
    
    Persistent state is managed via the traderData string.
    """
    
    def run(self, state: TradingState):
        # Print some debugging information:
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        
        # Recover persistent data (our price histories) from state.traderData if available, otherwise initialize.
        try:
            persistent: Dict[str, List[float]] = json.loads(state.traderData) if state.traderData else {}
        except Exception as e:
            print("Error decoding traderData, reinitializing.", e)
            persistent = {}
            
        # Make sure our price history for each product is present.
        for product in ["SQUID_INK", "KELP", "RAINFOREST_RESIN"]:
            if product not in persistent:
                persistent[product] = []
        
        # Update our price history per product using the current market price.
        # We derive a price from order depth: if both buy and sell orders exist, use the midprice.
        # If only one side is present, use the best available price.
        for product, order_depth in state.order_depths.items():
            # Only update if there is at least one order on one side.
            if order_depth.buy_orders or order_depth.sell_orders:
                if order_depth.buy_orders and order_depth.sell_orders:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_ask = min(order_depth.sell_orders.keys())
                    mid_price = (best_bid + best_ask) // 2  # integer midprice
                elif order_depth.buy_orders:
                    mid_price = max(order_depth.buy_orders.keys())
                else:
                    mid_price = min(order_depth.sell_orders.keys())
                persistent[product].append(mid_price)
                # Limit history size to, say, 50 ticks.
                if len(persistent[product]) > 50:
                    persistent[product] = persistent[product][-50:]
        
        # Prepare a result dictionary that maps each product to a list of orders.
        result: Dict[str, List[Order]] = {}
        
        # Define our strategy parameters.
        squid_window = 20
        squid_threshold = 1.5
        kelp_window = 10
        kelp_threshold = 0.01  # 1% deviation threshold
        trade_size = 1  # fixed trade size per order
        
        # Process each product that we have an OrderDepth for.
        for product, order_depth in state.order_depths.items():
            orders: List[Order] = []
            
            if product == "SQUID_INK":
                history = persistent[product]
                if len(history) >= squid_window:
                    window = history[-squid_window:]
                    avg_price = sum(window) / len(window)
                    variance = sum((p - avg_price) ** 2 for p in window) / len(window)
                    std_price = math.sqrt(variance)
                    current_price = history[-1]
                    normalized_dev = (current_price - avg_price) / std_price if std_price != 0 else 0
                    print(f"[SQUID_INK] Current: {current_price}, MA: {avg_price:.2f}, Std: {std_price:.2f}, NormDev: {normalized_dev:.2f}")
                    
                    # For mean reversion: if price is significantly below average, buy; if above, sell.
                    if normalized_dev < -squid_threshold:
                        # Attempt to buy: use best ask price from the sell orders.
                        if order_depth.sell_orders:
                            best_ask = min(order_depth.sell_orders.keys())
                            orders.append(Order(product, best_ask, trade_size))
                            print(f"Placing BUY order for {product} at price {best_ask}, qty {trade_size}")
                    elif normalized_dev > squid_threshold:
                        # Attempt to sell: use best bid price from the buy orders.
                        if order_depth.buy_orders:
                            best_bid = max(order_depth.buy_orders.keys())
                            orders.append(Order(product, best_bid, -trade_size))
                            print(f"Placing SELL order for {product} at price {best_bid}, qty {trade_size}")
            
            elif product == "KELP":
                history = persistent[product]
                if len(history) >= kelp_window:
                    window = history[-kelp_window:]
                    avg_price = sum(window) / len(window)
                    current_price = history[-1]
                    deviation = (current_price - avg_price) / avg_price if avg_price != 0 else 0
                    print(f"[KELP] Current: {current_price}, MA: {avg_price:.2f}, Deviation: {deviation:.2%}")
                    
                    if deviation < -kelp_threshold:
                        # Attempt to buy using best ask price.
                        if order_depth.sell_orders:
                            best_ask = min(order_depth.sell_orders.keys())
                            orders.append(Order(product, best_ask, trade_size))
                            print(f"Placing BUY order for {product} at price {best_ask}, qty {trade_size}")
                    elif deviation > kelp_threshold:
                        # Attempt to sell using best bid price.
                        if order_depth.buy_orders:
                            best_bid = max(order_depth.buy_orders.keys())
                            orders.append(Order(product, best_bid, -trade_size))
                            print(f"Placing SELL order for {product} at price {best_bid}, qty {trade_size}")
            
            # RAINFOREST_RESIN is stable. We do not actively trade it.
            result[product] = orders
        
        # In this simple strategy we do not place any conversion requests.
        conversions = 0
        # Serialize persistent data to string to pass it to the next iteration.
        traderData = json.dumps(persistent)
        
        return result, conversions, traderData
