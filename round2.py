from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict, Deque
from collections import deque
import statistics
import json
import math

class Trader:
    def __init__(self):
        self.price_history = {}
        # Track history length per product
        self.product_history_lengths = {
            "RAINFOREST_RESIN": 100,
            "KELP": 100,
            "SQUID_INK": 100,
            "DEFAULT": 100
        }
        
    def update_price_history(self, product, buy_orders, sell_orders):
        if buy_orders and sell_orders:
            # Get history length for this product
            history_length = self.product_history_lengths.get(
                product, 
                self.product_history_lengths["DEFAULT"]
            )
            
            # Update deque if needed
            if product in self.price_history:
                # Create new deque if length changed
                if self.price_history[product].maxlen != history_length:
                    self.price_history[product] = deque(
                        self.price_history[product], 
                        maxlen=history_length
                    )
            else:
                # Initialize new deque with correct length
                self.price_history[product] = deque(maxlen=history_length)

            # Rest of your existing update logic...
            new_bids = {}
            new_sells = {}

            for bid in buy_orders.keys():
                if buy_orders[bid] >= 10:
                    new_bids[bid] = buy_orders[bid]
            
            for ask in sell_orders.keys():
                if sell_orders[ask] >= 10:
                    new_sells[ask] = sell_orders[ask]

            if new_bids and new_sells:
                mid_bids = statistics.median(new_bids.keys())
                mid_asks = statistics.median(new_sells.keys())
                mid_price = (mid_bids + mid_asks) / 2
                
                self.price_history[product].append(mid_price)
                return mid_price
        return None

    def get_fair_price(self, product):
        # Get history length for this product
        history_length = self.product_history_lengths.get(
            product, 
            self.product_history_lengths["DEFAULT"]
        )
        
        # Update if needed (this is just for safety)
        if product in self.price_history and self.price_history[product].maxlen != history_length:
            self.price_history[product] = deque(
                self.price_history[product], 
                maxlen=history_length
            )
            
        if product in self.price_history and len(self.price_history[product]) > 0:
            return statistics.median(self.price_history[product])
        else:
            # Return product-specific default if needed
            return 10  # Or add default prices to product_history_lengths

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