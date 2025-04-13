from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict, Deque
from collections import deque
import statistics
import json
import math

class Trader:
    def __init__(self):
        # Initialize price history for each product
        self.price_history = {}  # Stores historical mid-prices for products
        self.history_length = 100  # Maximum history length to keep

    def update_price_history(self, product, buy_orders, sell_orders):
        # If there are valid buy and sell orders...
        if buy_orders and sell_orders:
            new_bids = {}
            new_sells = {}

            # Filter buy orders by volume (only orders with volume >= 10)
            for bid in buy_orders.keys():
                if buy_orders[bid] >= 10:
                    new_bids[bid] = buy_orders[bid]
            
            # Filter sell orders similarly
            for ask in sell_orders.keys():
                if sell_orders[ask] >= 10:
                    new_sells[ask] = sell_orders[ask]

            # Only compute mid-price if there are qualifying orders on both sides
            if new_bids and new_sells:
                mid_bids = statistics.median(new_bids.keys())
                mid_asks = statistics.median(new_sells.keys())
                mid_price = (mid_bids + mid_asks) / 2

                if product not in self.price_history:
                    self.price_history[product] = deque(maxlen=self.history_length)
                
                self.price_history[product].append(mid_price)
                return mid_price
        return None

    # This function calculates midprice using the best bid and ask.
    def find_midprice(self, state, product):
        order_depth = state.order_depths[product]
        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        # Using integer division; adjust if decimal precision is needed.
        mid_price = (best_ask + best_bid) // 2
        return mid_price

    # NEW FUNCTION: Place a buy order for a given product.
    # In our system, using negative volume may be the convention to indicate a buy
    # (as seen elsewhere in your code). We take half the available volume as our trade size.
    def place_buy_order(self, product: str, price: float, available_volume: int) -> Order:
        volume = -max(1, int(available_volume * 0.5))
        print(f"Placing BUY order for {product}: {abs(volume)} units at {price}")
        return Order(product, price, volume)

    # NEW FUNCTION: Place a sell order for a given product.
    # (Following your existing convention, we also use a negative volume for a sell order.)
    def place_sell_order(self, product: str, price: float, available_volume: int) -> Order:
        volume = -max(1, int(available_volume * 0.5))
        print(f"Placing SELL order for {product}: {abs(volume)} units at {price}")
        return Order(product, price, volume)

    # This function implements the basket two arbitrage trading logic.
    def basket_two_arbitrage_trading(self, state):
        # Calculate mid prices for the underlying products
        croissant_mid_price = self.find_midprice(state, "CROISSANTS")
        jams_mid_price = self.find_midprice(state, "JAMS")
        # Calculate the market mid price for the basket product
        basket_mid_price = self.find_midprice(state, "PICNIC_BASKET2")
        # Theoretical (calculated) value of the basket given the underlying midprices
        calculated_value = (4 * croissant_mid_price) + (2 * jams_mid_price)

        orders = []
        # Grab the order depth for the basket product
        order_depth = state.order_depths["PICNIC_BASKET2"]

        # If the market basket price is greater than our calculated value,
        # then sell the basket (i.e. market is overvaluing the basket).
        if basket_mid_price > calculated_value:
            if order_depth.buy_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                sell_order = self.place_sell_order("PICNIC_BASKET2", best_bid, best_bid_volume)
                orders.append(sell_order)
        # If the market basket price is lower than our calculated value,
        # then buy the basket (i.e. market is undervaluing the basket).
        elif basket_mid_price < calculated_value:
            if order_depth.sell_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                buy_order = self.place_buy_order("PICNIC_BASKET2", best_ask, best_ask_volume)
                orders.append(buy_order)

        return orders

    def basket_one_arbitrage_trading(self, state):
        # Ensure that all required products exist before proceeding.
        required_products = ["CROISSANTS", "JAMS", "DJEMBE", "PICNIC_BASKET1"]
        if not all(prod in state.order_depths for prod in required_products):
            return []

        # Calculate mid prices for the underlying products
        croissant_mid_price = self.find_midprice(state, "CROISSANTS")
        jams_mid_price = self.find_midprice(state, "JAMS")
        djembe_mid_price = self.find_midprice(state, "DJEMBE")

        # Calculate the market mid price for the basket product
        basket_mid_price = self.find_midprice(state, "PICNIC_BASKET1")
        # Theoretical (calculated) value of the basket given the underlying midprices
        calculated_value = (6 * croissant_mid_price) + (3 * jams_mid_price) + djembe_mid_price

        orders = []
        # Grab the order depth for the basket product
        order_depth = state.order_depths["PICNIC_BASKET1"]

        # If the market basket price is greater than our calculated value, sell the basket.
        if basket_mid_price > calculated_value:
            if order_depth.buy_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                sell_order = self.place_sell_order("PICNIC_BASKET1", best_bid, best_bid_volume)
                orders.append(sell_order)
        # If the market basket price is lower than our calculated value, buy the basket.
        elif basket_mid_price < calculated_value:
            if order_depth.sell_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                buy_order = self.place_buy_order("PICNIC_BASKET1", best_ask, best_ask_volume)
                orders.append(buy_order)

        return orders

    def get_fair_price(self, product):
        if product == "RAINFOREST_RESIN":
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
        elif product == "":
            return self.arbitrage_trading(self, product)
        else:
            return 10

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}

        # Iterate through all products in the current market state
        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            # Update price history for the product using current buy/sell data
            current_mid = self.update_price_history(
                product,
                order_depth.buy_orders,
                order_depth.sell_orders
            )

            # Calculate fair price based on historical prices
            fair_price = self.get_fair_price(product)

            # BUY LOGIC: Look at sell orders
            if order_depth.sell_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                if best_ask <= fair_price:
                    order = self.place_buy_order(product, best_ask, best_ask_volume)
                    orders.append(order)

            # SELL LOGIC: Look at buy orders
            if order_depth.buy_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid >= fair_price:
                    order = self.place_sell_order(product, best_bid, best_bid_volume)
                    orders.append(order)

            result[product] = orders

        # Incorporate PICNIC_BASKET2 arbitrage orders
        basket2_orders = self.basket_two_arbitrage_trading(state)
        if "PICNIC_BASKET2" in result:
            result["PICNIC_BASKET2"].extend(basket2_orders)
        else:
            result["PICNIC_BASKET2"] = basket2_orders

        # Incorporate PICNIC_BASKET1 arbitrage orders if implemented
        basket1_orders = self.basket_one_arbitrage_trading(state)
        if "PICNIC_BASKET1" in result:
            result["PICNIC_BASKET1"].extend(basket1_orders)
        else:
            result["PICNIC_BASKET1"] = basket1_orders

        trader_data = json.dumps({
            "price_history": {k: list(v) for k, v in self.price_history.items()}
        })

        conversions = 1
        return result, conversions, trader_data
