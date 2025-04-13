from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict
from collections import deque
import statistics
import json

class Trader:
    def __init__(self):
        # Dictionary to store price history for each product.
        # We store a deque (fixed-length list) for each product.
        self.price_history = {}
        # Maximum length of the price history to store.
        self.history_length = 100

    def update_price_history(self, product: str, buy_orders: Dict[float, int], sell_orders: Dict[float, int]):
        """
        Updates the price history for a product based on the current order depth.
        Only orders with volume >= 10 are included.
        The midprice is computed as the median of the bid prices and ask prices, then averaged.
        """
        # Create filtered dictionaries that only keep orders with volume at least 10.
        new_bids = {price: vol for price, vol in buy_orders.items() if vol >= 10}
        new_asks = {price: vol for price, vol in sell_orders.items() if vol >= 10}
        
        if new_bids and new_asks:
            # Compute the medians of the bid and ask prices.
            mid_bid = statistics.median(new_bids.keys())
            mid_ask = statistics.median(new_asks.keys())
            # Calculate the midprice as the average
            mid_price = (mid_bid + mid_ask) / 2.0

            # If no history exists for this product, create one as a deque with fixed maximum length.
            if product not in self.price_history:
                self.price_history[product] = deque(maxlen=self.history_length)
            self.price_history[product].append(mid_price)
            return mid_price
        return None

    def find_midprice(self, state: TradingState, product: str):
        """
        Computes a midprice for the given product using the best bid and best ask.
        Returns None if the product is missing or there is no valid bid/ask data.
        """
        if product not in state.order_depths:
            # Return None if this product isn’t found in the current market data.
            return None
        
        order_depth: OrderDepth = state.order_depths[product]
        if not order_depth.buy_orders or not order_depth.sell_orders:
            return None

        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        # Use integer division for midprice; adjust as needed.
        mid_price = (best_bid + best_ask) // 2
        return mid_price

    def basket_two_arbitrage_trading(self, state: TradingState) -> List[Order]:
        """
        Implements the arbitrage strategy for basket two.
        The basket comprises a fixed number of two underlying products (for example, 4 x "CROISSANT" and 2 x "JAMS").
        The idea is to compare the current basket midprice with the calculated value based on underlying midprices.
        Orders are placed only if the basket is mispriced relative to the combined value.
        """
        # Before attempting to calculate, ensure that all required products are available.
        required_products = ["CROISSANT", "JAMS", "PICNIC_BASKET2"]
        for prod in required_products:
            if prod not in state.order_depths:
                # If any required product is missing, skip arbitrage trading.
                return []

        # Retrieve midprices for the underlying components.
        croissant_mid = self.find_midprice(state, "CROISSANT")
        jams_mid = self.find_midprice(state, "JAMS")
        basket_mid = self.find_midprice(state, "PICNIC_BASKET2")
        if croissant_mid is None or jams_mid is None or basket_mid is None:
            return []
        
        # The calculated basket value based on underlying products:
        # e.g., basket_value = 4 * (croissant price) + 2 * (jams price)
        calculated_value = (4 * croissant_mid) + (2 * jams_mid)

        orders = []
        order_depth = state.order_depths["PICNIC_BASKET2"]

        # If the basket is trading above its calculated value, we assume it is overpriced:
        # Sell the basket (at the best bid) to take advantage of the premium.
        if basket_mid > calculated_value and order_depth.buy_orders:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_volume = order_depth.buy_orders[best_bid]
            # Example: Sell half the available volume (at least 1 unit)
            quantity_to_sell = -max(1, int(best_bid_volume * 0.5))
            print(f"[Arbitrage] SELL PICNIC_BASKET2: {abs(quantity_to_sell)}x at {best_bid}")
            orders.append(Order("PICNIC_BASKET2", best_bid, quantity_to_sell))
        
        # If the basket is trading below its calculated value, we assume it is underpriced:
        # Buy the basket (at the best ask) to exploit the discount.
        elif basket_mid < calculated_value and order_depth.sell_orders:
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_volume = order_depth.sell_orders[best_ask]
            # Example: Buy half the available volume (at least 1 unit)
            quantity_to_buy = max(1, int(best_ask_volume * 0.5))
            print(f"[Arbitrage] BUY PICNIC_BASKET2: {quantity_to_buy}x at {best_ask}")
            orders.append(Order("PICNIC_BASKET2", best_ask, -quantity_to_buy))
        
        return orders

    def get_fair_price(self, product: str):
        """
        Returns a fair price for the product based on its price history.
        For some products (like RAINFOREST_RESIN, KELP, SQUID_INK),
        the fair price is based on the median of recent midprices.
        Otherwise, a default value is returned.
        """
        if product == "RAINFOREST_RESIN":
            return 10000
        elif product == "KELP":
            self.history_length = 50  # Adjust history length if needed
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

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        The main entry point for trading.
        Processes any arbitrage opportunities for basket two first, then applies standard trading logic.
        Outputs a dictionary mapping product names to a list of orders.
        Also returns a string (traderData) that stores state information (such as price history)
        for use in the next round.
        """
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}

        # First, attempt the basket two arbitrage strategy.
        basket_orders = self.basket_two_arbitrage_trading(state)
        if basket_orders:
            result["PICNIC_BASKET2"] = basket_orders

        # Next, process all the other products via standard logic.
        for product, order_depth in state.order_depths.items():
            # Skip PICNIC_BASKET2 because it’s handled above.
            if product == "PICNIC_BASKET2":
                continue

            orders: List[Order] = []
            current_mid = self.update_price_history(product, order_depth.buy_orders, order_depth.sell_orders)
            fair_price = self.get_fair_price(product)

            # If there are sell orders and the best ask is less than or equal to our fair price, then BUY.
            if order_depth.sell_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                if best_ask <= fair_price:
                    print(f"[Standard] BUY {product}: {-best_ask_volume}x at {best_ask}")
                    orders.append(Order(product, best_ask, -best_ask_volume))
            
            # If there are buy orders and the best bid is greater than or equal to our fair price, then SELL.
            if order_depth.buy_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid >= fair_price:
                    print(f"[Standard] SELL {product}: {best_bid_volume}x at {best_bid}")
                    orders.append(Order(product, best_bid, -best_bid_volume))
            
            result[product] = orders

        # Save the trader's state (price history, etc.) for the next round.
        trader_data = json.dumps({
            "price_history": {k: list(v) for k, v in self.price_history.items()}
        })
        conversions = 1  # This value can be used to indicate any necessary conversion factors.

        return result, conversions, trader_data
