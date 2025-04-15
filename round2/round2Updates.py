from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict, Deque
from collections import deque
import statistics
import json
import math

class Trader:
    def __init__(self):
        # Initialize price history for each product
        self.price_history = {}
        self.history_length = 100
        
    def update_price_history(self, product, buy_orders, sell_orders):
        if buy_orders and sell_orders:
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
                
                if product not in self.price_history:
                    self.price_history[product] = deque(maxlen=self.history_length)
                
                self.price_history[product].append(mid_price)
                return mid_price
        return None

    def get_fair_price(self, product):
        if product == "RAINFOREST_RESIN":
            return 10000
        elif product == "KELP":
            self.history_length = 50
            if product in self.price_history and len(self.price_history[product]) > 0:
                return statistics.median(self.price_history[product])
            return 10000
        elif product == "SQUID_INK":
            self.history_length = 25000
            if product in self.price_history and len(self.price_history[product]) > 0:
                return statistics.median(self.price_history[product])
            return 10000
        else:
            return 10

    def find_midprice(self, state, product):
        order_depth = state.order_depths[product]
        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        mid_price = (best_ask + best_bid) / 2
        return mid_price

    def basket_arbitrage_trading(self, state):
        basket_orders = []
        
        # Get current mid prices
        croissant_mid = self.find_midprice(state, "CROISSANTS")
        jams_mid = self.find_midprice(state, "JAMS")
        basket_mid = self.find_midprice(state, "PICNIC_BASKET")
        
        # Calculate fair value (4 croissants + 2 jams)
        calculated_value = (4 * croissant_mid) + (2 * jams_mid)
        
        # Arbitrage threshold (adjust based on market conditions)
        threshold = 5
        
        # Check for arbitrage opportunity
        if basket_mid > calculated_value + threshold:
            # Sell basket and buy components
            basket_order_depth = state.order_depths["PICNIC_BASKET"]
            if basket_order_depth.buy_orders:
                best_basket_bid = max(basket_order_depth.buy_orders.keys())
                basket_volume = basket_order_depth.buy_orders[best_basket_bid]
                basket_orders.append(Order("PICNIC_BASKET", best_basket_bid, -basket_volume))
                
                # Buy components (4 croissants and 2 jams for each basket)
                croissant_order_depth = state.order_depths["CROISSANTS"]
                if croissant_order_depth.sell_orders:
                    best_croissant_ask = min(croissant_order_depth.sell_orders.keys())
                    croissant_volume = min(abs(croissant_order_depth.sell_orders[best_croissant_ask]), 
                                         abs(4 * basket_volume))
                    basket_orders.append(Order("CROISSANTS", best_croissant_ask, croissant_volume))
                
                jams_order_depth = state.order_depths["JAMS"]
                if jams_order_depth.sell_orders:
                    best_jams_ask = min(jams_order_depth.sell_orders.keys())
                    jams_volume = min(abs(jams_order_depth.sell_orders[best_jams_ask]), 
                                    abs(2 * basket_volume))
                    basket_orders.append(Order("JAMS", best_jams_ask, jams_volume))
        
        elif basket_mid < calculated_value - threshold:
            # Buy basket and sell components
            basket_order_depth = state.order_depths["PICNIC_BASKET"]
            if basket_order_depth.sell_orders:
                best_basket_ask = min(basket_order_depth.sell_orders.keys())
                basket_volume = abs(basket_order_depth.sell_orders[best_basket_ask])
                basket_orders.append(Order("PICNIC_BASKET", best_basket_ask, basket_volume))
                
                # Sell components
                croissant_order_depth = state.order_depths["CROISSANTS"]
                if croissant_order_depth.buy_orders:
                    best_croissant_bid = max(croissant_order_depth.buy_orders.keys())
                    croissant_volume = min(croissant_order_depth.buy_orders[best_croissant_bid], 
                                        4 * basket_volume)
                    basket_orders.append(Order("CROISSANTS", best_croissant_bid, -croissant_volume))
                
                jams_order_depth = state.order_depths["JAMS"]
                if jams_order_depth.buy_orders:
                    best_jams_bid = max(jams_order_depth.buy_orders.keys())
                    jams_volume = min(jams_order_depth.buy_orders[best_jams_bid], 
                                    2 * basket_volume)
                    basket_orders.append(Order("JAMS", best_jams_bid, -jams_volume))
        
        return basket_orders

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}

        # First handle basket arbitrage if these products exist
        basket_products = {"PICNIC_BASKET", "CROISSANTS", "JAMS"}
        if basket_products.issubset(state.order_depths.keys()):
            basket_orders = self.basket_arbitrage_trading(state)
            for order in basket_orders:
                product = order.symbol
                if product not in result:
                    result[product] = []
                result[product].append(order)

        # Then handle all other products normally
        for product in state.order_depths.keys():  
            if product in basket_products:
                continue  # Already handled by basket arbitrage
                
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            current_mid = self.update_price_history(
                product, 
                order_depth.buy_orders,
                order_depth.sell_orders
            )

            fair_price = self.get_fair_price(product)

            # Buy logic
            if order_depth.sell_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                
                if best_ask <= fair_price:
                    print(f"BUY {product} {-best_ask_volume}x {best_ask}")
                    orders.append(Order(product, best_ask, -best_ask_volume))

            # Sell logic
            if order_depth.buy_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                
                if best_bid >= fair_price:
                    print(f"SELL {product} {best_bid_volume}x {best_bid}")
                    orders.append(Order(product, best_bid, -best_bid_volume))

            if product not in result:
                result[product] = []
            result[product].extend(orders)
            
        trader_data = json.dumps({
            "price_history": {k: list(v) for k, v in self.price_history.items()}
        })
        
        conversions = 1 
        return result, conversions, trader_data