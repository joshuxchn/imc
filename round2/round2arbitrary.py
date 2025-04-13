from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict, Deque
from collections import deque
import statistics
import json
import math

class Trader:
    def __init__(self):
        # Initialize price history for each product
        self.price_history = {}  # Changed to snake_case
        self.history_length = 100  # Changed to snake_case
        
    def update_price_history(self, product, buy_orders, sell_orders):  # Changed to snake_case
        if buy_orders and sell_orders:
            new_bids = {}  # Changed to snake_case
            new_sells = {}  # Changed to snake_case

            for bid in buy_orders.keys():
                if buy_orders[bid] >= 10:
                    new_bids[bid] = buy_orders[bid]  # Changed from .add() to dict assignment
            
            for ask in sell_orders.keys():  # Changed variable name from 'sell' to 'ask'
                if sell_orders[ask] >= 10:
                    new_sells[ask] = sell_orders[ask]  # Changed from .add() to dict assignment

            if new_bids and new_sells:  # Only calculate if we have qualifying orders
                mid_bids = statistics.median(new_bids.keys())  # Changed to snake_case
                mid_asks = statistics.median(new_sells.keys())  # Changed to snake_case
                mid_price = (mid_bids + mid_asks) / 2
                
                if product not in self.price_history:
                    self.price_history[product] = deque(maxlen=self.history_length)
                
                self.price_history[product].append(mid_price)
                return mid_price
        return None

    def get_fair_price(self, product):  # Changed to snake_case
        if product == "RAINFOREST_RESIN":
            # self.history_length = 1000
            # if product in self.price_history and len(self.price_history[product]) > 900:
            #     return statistics.median(self.price_history[product])
            return 10000
        elif product == "KELP":
            self.history_length = 50
            if product in self.price_history and len(self.price_history[product]) > 0:
                return statistics.median(self.price_history[product])
            return 10000  # Default if no history
        elif product == "SQUID_INK":
            self.history_length = 25000
            if product in self.price_history and len(self.price_history[product]) > 0:
                return statistics.median(self.price_history[product])
            return 10000  # Default if no history
        else:
            return 10

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}

        # Corrected to use order_depths instead of orderDepths
        for product in state.order_depths.keys():  
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            # Update price history with current market data
            current_mid = self.update_price_history(
                product, 
                order_depth.buy_orders,  # Corrected to snake_case
                order_depth.sell_orders  # Corrected to snake_case
            )

            # Calculate fair price based on history
            fair_price = self.get_fair_price(product)

            # Buy logic
            if order_depth.sell_orders:  # Corrected to snake_case
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                
                if best_ask <= fair_price:
                    print(f"BUY {product} {-best_ask_volume}x {best_ask}")
                    orders.append(Order(product, best_ask, -best_ask_volume))

            # Sell logic
            if order_depth.buy_orders:  # Corrected to snake_case
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                
                if best_bid >= fair_price:
                    print(f"SELL {product} {best_bid_volume}x {best_bid}")
                    orders.append(Order(product, best_bid, -best_bid_volume))

            result[product] = orders
            
        # Serialize trader data for next iteration
        trader_data = json.dumps({  # Changed to snake_case
            "price_history": {k: list(v) for k, v in self.price_history.items()}
        })
        
        conversions = 1 
        return result, conversions, trader_data