import json
import statistics
from collections import deque
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:
    def __init__(self):
        # Price history for each product, stored as a deque to keep recent mid prices.
        self.price_history = {}
        self.history_length = 100  # Default length; note that get_fair_price may adjust this per product.

    def update_price_history(self, product: str, buy_orders: Dict[int, int], sell_orders: Dict[int, int]):
        """
        Update the price history for a product from the current order book.
        Only includes orders with significant volume (>= 10) to filter out noise. - commented out for now
        The mid price is computed as the average of the medians of qualifying bids and asks.
        """
        if buy_orders and sell_orders:
            new_bids = {}
            new_sells = {}
            # Filter bids with volume at least 10.
            for bid in buy_orders:
                # if buy_orders[bid] >= 10:
                    new_bids[bid] = buy_orders[bid]
            # Filter asks with volume at least 10 (using absolute value).
            for ask in sell_orders:
                # if abs(sell_orders[ask]) >= 10:
                    new_sells[ask] = sell_orders[ask]
            if new_bids and new_sells:
                mid_bids = statistics.median(new_bids.keys())
                mid_asks = statistics.median(new_sells.keys())
                mid_price = (mid_bids + mid_asks) / 2.0
                if product not in self.price_history:
                    self.price_history[product] = deque(maxlen=self.history_length)
                self.price_history[product].append(mid_price)
                return mid_price
        return None

    def get_fair_price(self, product: str) -> float:
        """
        Returns a fair price for the product.
        For RAINFOREST_RESIN a fixed price is used.
        For KELP and SQUID_INK, the history length is adjusted and a median price returned.
        Otherwise, a default fair price of 10 is applied.
        """
        if product == "RAINFOREST_RESIN":
            return 10000
        elif product == "KELP":
            self.history_length = 50
            if product in self.price_history and len(self.price_history[product]) > 0:
                if len(self.price_history[product]) > 200:
                    return statistics.median(self.price_history[product][-200:])
            return 10000
        elif product == "SQUID_INK":
            self.history_length = 25000
            if product in self.price_history and len(self.price_history[product]) > 0:
                if len(self.price_history[product]) > 200:
                    return statistics.median(self.price_history[product][-200:]) / 2 + statistics.median(self.price_history[product][-100:]) / 2
            return 10000
        else:
            return 10

    def find_midprice(self, state: TradingState, product: str) -> float:
        """
        Quickly compute the current mid price from the best bid and ask in the order book.
        """
        order_depth = state.order_depths[product]
        if order_depth.buy_orders and order_depth.sell_orders:
            best_bid = max(order_depth.buy_orders.keys())
            best_ask = min(order_depth.sell_orders.keys())
            mid_price = (best_bid + best_ask) / 2.0
            return mid_price
        return 0

    def arbitrage_basket1(self, state: TradingState) -> List[Order]:
        """
        Implements basket arbitrage for PICNIC_BASKET1:
          Components: 6 × CROISSANTS, 3 × JAMS, 1 × DJEMBES.
        Determines if the basket is mispriced versus its components and sends orders accordingly.
        """
        orders = []
        # Retrieve current mid prices for each component.
        croissant_mid = self.find_midprice(state, "CROISSANTS")
        jams_mid = self.find_midprice(state, "JAMS")
        djembes_mid = self.find_midprice(state, "DJEMBES")
        basket_mid = self.find_midprice(state, "PICNIC_BASKET1")
        # Calculate the theoretical basket value.
        calculated_value = (6 * croissant_mid) + (3 * jams_mid) + (1 * djembes_mid)
        threshold = 5

        if basket_mid > calculated_value + threshold:
            # Basket is overpriced: sell basket and buy the components.
            basket_depth = state.order_depths["PICNIC_BASKET1"]
            if basket_depth.buy_orders:
                best_basket_bid = max(basket_depth.buy_orders.keys())
                basket_volume = basket_depth.buy_orders[best_basket_bid]
                orders.append(Order("PICNIC_BASKET1", best_basket_bid, -basket_volume))
                # Buy CROISSANTS.
                croissant_depth = state.order_depths["CROISSANTS"]
                if croissant_depth.sell_orders:
                    best_croissant_ask = min(croissant_depth.sell_orders.keys())
                    required_croissants = 6 * basket_volume
                    available_croissants = abs(croissant_depth.sell_orders[best_croissant_ask])
                    croissant_volume = min(available_croissants, required_croissants)
                    orders.append(Order("CROISSANTS", best_croissant_ask, croissant_volume))
                # Buy JAMS.
                jams_depth = state.order_depths["JAMS"]
                if jams_depth.sell_orders:
                    best_jams_ask = min(jams_depth.sell_orders.keys())
                    required_jams = 3 * basket_volume
                    available_jams = abs(jams_depth.sell_orders[best_jams_ask])
                    jams_volume = min(available_jams, required_jams)
                    orders.append(Order("JAMS", best_jams_ask, jams_volume))
                # Buy DJEMBES.
                djembes_depth = state.order_depths["DJEMBES"]
                if djembes_depth.sell_orders:
                    best_djembes_ask = min(djembes_depth.sell_orders.keys())
                    required_djembes = 1 * basket_volume
                    available_djembes = abs(djembes_depth.sell_orders[best_djembes_ask])
                    djembes_volume = min(available_djembes, required_djembes)
                    orders.append(Order("DJEMBES", best_djembes_ask, djembes_volume))
        elif basket_mid < calculated_value - threshold:
            # Basket is underpriced: buy basket and sell the components.
            basket_depth = state.order_depths["PICNIC_BASKET1"]
            if basket_depth.sell_orders:
                best_basket_ask = min(basket_depth.sell_orders.keys())
                basket_volume = abs(basket_depth.sell_orders[best_basket_ask])
                orders.append(Order("PICNIC_BASKET1", best_basket_ask, basket_volume))
                # Sell CROISSANTS.
                croissant_depth = state.order_depths["CROISSANTS"]
                if croissant_depth.buy_orders:
                    best_croissant_bid = max(croissant_depth.buy_orders.keys())
                    required_croissants = 6 * basket_volume
                    available_croissants = croissant_depth.buy_orders[best_croissant_bid]
                    croissant_volume = min(available_croissants, required_croissants)
                    orders.append(Order("CROISSANTS", best_croissant_bid, -croissant_volume))
                # Sell JAMS.
                jams_depth = state.order_depths["JAMS"]
                if jams_depth.buy_orders:
                    best_jams_bid = max(jams_depth.buy_orders.keys())
                    required_jams = 3 * basket_volume
                    available_jams = jams_depth.buy_orders[best_jams_bid]
                    jams_volume = min(available_jams, required_jams)
                    orders.append(Order("JAMS", best_jams_bid, -jams_volume))
                # Sell DJEMBES.
                djembes_depth = state.order_depths["DJEMBES"]
                if djembes_depth.buy_orders:
                    best_djembes_bid = max(djembes_depth.buy_orders.keys())
                    required_djembes = 1 * basket_volume
                    available_djembes = djembes_depth.buy_orders[best_djembes_bid]
                    djembes_volume = min(available_djembes, required_djembes)
                    orders.append(Order("DJEMBES", best_djembes_bid, -djembes_volume))
        return orders

    def arbitrage_basket2(self, state: TradingState) -> List[Order]:
        """
        Implements basket arbitrage for PICNIC_BASKET2:
          Components: 4 × CROISSANTS and 2 × JAMS.
        Determines mispricing and sends orders accordingly.
        """
        orders = []
        croissant_mid = self.find_midprice(state, "CROISSANTS")
        jams_mid = self.find_midprice(state, "JAMS")
        basket_mid = self.find_midprice(state, "PICNIC_BASKET2")
        calculated_value = (4 * croissant_mid) + (2 * jams_mid)
        threshold = 0
        #testing threshold value

        if basket_mid > calculated_value + threshold:
            # Basket is overpriced: sell basket and buy components.
            basket_depth = state.order_depths["PICNIC_BASKET2"]
            if basket_depth.buy_orders:
                best_basket_bid = max(basket_depth.buy_orders.keys())
                basket_volume = basket_depth.buy_orders[best_basket_bid]
                orders.append(Order("PICNIC_BASKET2", best_basket_bid, -basket_volume))
                # Buy CROISSANTS.
                croissant_depth = state.order_depths["CROISSANTS"]
                if croissant_depth.sell_orders:
                    best_croissant_ask = min(croissant_depth.sell_orders.keys())
                    required_croissants = 4 * basket_volume
                    available_croissants = abs(croissant_depth.sell_orders[best_croissant_ask])
                    croissant_volume = min(available_croissants, required_croissants)
                    orders.append(Order("CROISSANTS", best_croissant_ask, croissant_volume))
                # Buy JAMS.
                jams_depth = state.order_depths["JAMS"]
                if jams_depth.sell_orders:
                    best_jams_ask = min(jams_depth.sell_orders.keys())
                    required_jams = 2 * basket_volume
                    available_jams = abs(jams_depth.sell_orders[best_jams_ask])
                    jams_volume = min(available_jams, required_jams)
                    orders.append(Order("JAMS", best_jams_ask, jams_volume))
        elif basket_mid < calculated_value - threshold:
            # Basket is underpriced: buy basket and sell components.
            basket_depth = state.order_depths["PICNIC_BASKET2"]
            if basket_depth.sell_orders:
                best_basket_ask = min(basket_depth.sell_orders.keys())
                basket_volume = abs(basket_depth.sell_orders[best_basket_ask])
                orders.append(Order("PICNIC_BASKET2", best_basket_ask, basket_volume))
                # Sell CROISSANTS.
                croissant_depth = state.order_depths["CROISSANTS"]
                if croissant_depth.buy_orders:
                    best_croissant_bid = max(croissant_depth.buy_orders.keys())
                    required_croissants = 4 * basket_volume
                    available_croissants = croissant_depth.buy_orders[best_croissant_bid]
                    croissant_volume = min(available_croissants, required_croissants)
                    orders.append(Order("CROISSANTS", best_croissant_bid, -croissant_volume))
                # Sell JAMS.
                jams_depth = state.order_depths["JAMS"]
                if jams_depth.buy_orders:
                    best_jams_bid = max(jams_depth.buy_orders.keys())
                    required_jams = 2 * basket_volume
                    available_jams = jams_depth.buy_orders[best_jams_bid]
                    jams_volume = min(available_jams, required_jams)
                    orders.append(Order("JAMS", best_jams_bid, -jams_volume))
        return orders

    def basket_arbitrage_trading(self, state: TradingState) -> List[Order]:
        """
        Checks and executes basket arbitrage for both PICNIC_BASKET1 and PICNIC_BASKET2,
        if all their required components are available.
        """
        orders = []
        # For PICNIC_BASKET1: requires CROISSANTS, JAMS, and DJEMBES.
        if {"PICNIC_BASKET1", "CROISSANTS", "JAMS", "DJEMBES"}.issubset(state.order_depths.keys()):
            orders.extend(self.arbitrage_basket1(state))
        # For PICNIC_BASKET2: requires CROISSANTS and JAMS.
        if {"PICNIC_BASKET2", "CROISSANTS", "JAMS"}.issubset(state.order_depths.keys()):
            orders.extend(self.arbitrage_basket2(state))
        return orders

    def regular_trading(self, state: TradingState, product: str) -> List[Order]:
        """
        Executes fair-price–based trading for non-basket products.
        Updates price history and compares the best bid/ask against the fair price.
        """
        orders = []
        order_depth = state.order_depths[product]
        # Update historical mid prices.
        self.update_price_history(product, order_depth.buy_orders, order_depth.sell_orders)
        fair_price = self.get_fair_price(product)
        # If the best ask is below or equal to the fair price, buy.
        if order_depth.sell_orders:
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_volume = order_depth.sell_orders[best_ask]
            if best_ask <= fair_price:
                print(f"BUY {product} {-best_ask_volume}x at {best_ask}")
                orders.append(Order(product, best_ask, -best_ask_volume))
        # If the best bid is above or equal to the fair price, sell.
        if order_depth.buy_orders:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_volume = order_depth.buy_orders[best_bid]
            if best_bid >= fair_price:
                print(f"SELL {product} {best_bid_volume}x at {best_bid}")
                orders.append(Order(product, best_bid, -best_bid_volume))
        return orders

    def run(self, state: TradingState) -> (Dict[str, List[Order]], int, str):
        """
        Main trading logic:
         1. Executes basket arbitrage for both PICNIC_BASKET1 and PICNIC_BASKET2.
         2. For all other products, applies standard fair-price trading.
         3. Serializes the price history into traderData for state persistence.
        """
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}

        # Execute basket arbitrage.
        basket_orders = self.basket_arbitrage_trading(state)
        for order in basket_orders:
            prod = order.symbol
            if prod not in result:
                result[prod] = []
            result[prod].append(order)

        # Process remaining (non-basket) products.
        basket_products = {"PICNIC_BASKET1", "PICNIC_BASKET2"}
        for product in state.order_depths.keys():
            if product in basket_products:
                continue
            orders = self.regular_trading(state, product)
            if orders:
                result[product] = orders

        # Persist the price history in traderData for the next iteration.
        trader_data = json.dumps({
            "price_history": {k: list(v) for k, v in self.price_history.items()}
        })
        conversions = 1  # Set conversion count according to your strategy.
        return result, conversions, trader_data