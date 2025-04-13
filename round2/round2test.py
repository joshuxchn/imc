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


    # logic for basket trading

    def find_midprice(state, product):
        order_depth = state.order_depths[product]
        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        mid_price = (best_ask + best_bid) // 2
        return mid_price
        

    def basket_two_arbitrage_trading(self, state):
        # Use correct product naming (adjust "CROISSANT" to "CROISSANTS" if needed)
        croissant_mid_price = self.find_midprice(state, "CROISSANT")
        jams_mid_price = self.find_midprice(state, "JAMS")
        basket_mid_price = self.find_midprice(state, "PICNIC_BASKET2")
        # Calculate the theoretical basket value from underlying products
        calculated_value = (4 * croissant_mid_price) + (2 * jams_mid_price)

        orders = []
        order_depth = state.order_depths["PICNIC_BASKET2"]

        # If market basket price is greater than theoretical value, sell the basket.
        if basket_mid_price > calculated_value:
            if order_depth.buy_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                sell_order = self.place_sell_order("PICNIC_BASKET2", best_bid, best_bid_volume)
                orders.append(sell_order)

        # If market basket price is lower than theoretical value, buy the basket.
        elif basket_mid_price < calculated_value:
            if order_depth.sell_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                buy_order = self.place_buy_order("PICNIC_BASKET2", best_ask, best_ask_volume)
                orders.append(buy_order)

        return orders

    def get_fair_price(self, product):  # Changed to snake_case
        if product == "RAINFOREST_RESIN":
            return 10000
        elif product == "KELP":
            self.history_length = 50
            if product in self.price_history and len(self.price_history[product]) > 0:
                return statistics.median(self.price_history[product])
        elif product == "SQUID_INK":
            self.history_length = 25000
            if product in self.price_history and len(self.price_history[product]) > 0:
                return statistics.median(self.price_history[product])
        else:
            return 10

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}

        # Process each product individually.
        for product in state.order_depths.keys():
            order_depth = state.order_depths[product]
            orders: List[Order] = []

            # Update price history for the product using current orders (if applicable)
            current_mid = self.update_price_history(
                product,
                order_depth.buy_orders,
                order_depth.sell_orders
            )

            # Determine fair price based on historical prices
            fair_price = self.get_fair_price(product)

            # BUY LOGIC: Look at sell orders if price is below fair price.
            if order_depth.sell_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                if best_ask <= fair_price:
                    order = self.place_buy_order(product, best_ask, best_ask_volume)
                    orders.append(order)

            # SELL LOGIC: Look at buy orders if price is above fair price.
            if order_depth.buy_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid >= fair_price:
                    order = self.place_sell_order(product, best_bid, best_bid_volume)
                    orders.append(order)

            result[product] = orders

        # Incorporate basket_two_arbitrage orders for PICNIC_BASKET2 based on its custom logic.
        basket2_orders = self.basket_two_arbitrage_trading(state)
        if "PICNIC_BASKET2" in result:
            result["PICNIC_BASKET2"].extend(basket2_orders)
        else:
            result["PICNIC_BASKET2"] = basket2_orders

        return result
