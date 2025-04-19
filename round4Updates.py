import json
import statistics
from collections import deque
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:
    def __init__(self):
        
        # Create Price History Dictionary
        self.priceHistory = {}
        
        # Fix History Length
        self.historyLength = 100
        
    def updatePriceHistory(self, product, buyOrders, sellOrders):
        
        # Check not Empty
        if buyOrders and sellOrders:
            
            # Get Median
            midBids = statistics.median(buyOrders.keys())
            midAsks = statistics.median(sellOrders.keys())
            
            # Apply Mid Price Arithmetic
            midPrice = (midBids + midAsks) / 2.0
            
            # Avoid Updating Product
            if product not in self.priceHistory:
                self.priceHistory[product] = deque(maxlen=self.historyLength)
            
            # Update Price (Will also delete least recent price if full)
            self.priceHistory[product].append(midPrice)
            return midPrice
        return None
    
    def getFairPrice(self, state, product):
        
        # Case on Products to price
        if product == "RAINFOREST_RESIN":
            
            # Estimating rainforest_resin price
            return 10000
        
        elif product == "KELP":

            #if product in self.price_history and len(self.price_history[product]) > 0:
            #    if len(self.price_history[product]) > 200:
            #        return statistics.median(self.price_history[product][-200:])
            return 10000
        
        elif product == "SQUID_INK":
            
            #if product in self.price_history and len(self.price_history[product]) > 0:
            #    if len(self.price_history[product]) > 200:
            #        return statistics.median(self.price_history[product][-200:]) / 2 + statistics.median(self.price_history[product][-100:]) / 2
            return 10000
        
        elif product == "CROISSANTS":
    
            #if product in self.price_history and len(self.price_history[product]) > 0:
            #    if len(self.price_history[product]) > 200:
            #        return statistics.median(self.price_history[product][-200:])
            return 10000
        
        elif product == "DJEMBES":
            
            #if product in self.price_history and len(self.price_history[product]) > 0:
            #    if len(self.price_history[product]) > 200:
            #        return statistics.median(self.price_history[product][-200:]) / 2 + statistics.median(self.price_history[product][-100:]) / 2
            return 10000
        
        elif product == "JAMS":
        
            #if product in self.price_history and len(self.price_history[product]) > 0:
            #    if len(self.price_history[product]) > 200:
            #        return statistics.median(self.price_history[product][-200:])
            return 10000
        
        elif product == "PICNIC_BASKET1":
            
            #if product in self.price_history and len(self.price_history[product]) > 0:
            #    if len(self.price_history[product]) > 200:
            #        return statistics.median(self.price_history[product][-200:]) / 2 + statistics.median(self.price_history[product][-100:]) / 2
            return 10000

        elif product == "PICNIC_BASKET2":
            
            #if product in self.price_history and len(self.price_history[product]) > 0:
            #    if len(self.price_history[product]) > 200:
            #        return statistics.median(self.price_history[product][-200:]) / 2 + statistics.median(self.price_history[product][-100:]) / 2
            return 10000
        
        else:
            
            #Short
            return 10
        
    def findMidPrice(self,state,product,expected):
        
        # Get Orders
        orderDepth = state.order_depths[product]
        
        # If there are orders we proceed
        if orderDepth.buy_orders and orderDepth.sell_orders:
            
            # Get best bid and ask price
            bestBid = max(orderDepth.buy_orders.keys())
            bestAsk = min(orderDepth.sell_orders.keys())
            
            # Apply midPrice Arithmetic
            midPrice = (bestBid + bestAsk) / 2.0
            return midPrice
        
        # Else we just return the expected price
        return expected
        
    def arbitrageBasket1(self,state):
        
        # New Orders
        orders = []
        
        # Retrieve current mid prices for each component.
        croissant_mid = self.findMidPrice(state, "CROISSANTS",4200)
        jams_mid = self.findMidPrice(state, "JAMS", 6630)
        djembes_mid = self.findMidPrice(state, "DJEMBES",13400)
        basket_mid = self.findMidPrice(state, "PICNIC_BASKET1",58650)
        
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
        
        # Update with new Orders
        return orders
    
    def arbitrageBasket2(self,state):
        
        # New Orders Array
        orders = []
        
        # Get Mid Prices
        croissant_mid = self.findMidPrice(state, "CROISSANTS", 4290)
        jams_mid = self.findMidPrice(state, "JAMS", 6550)
        basket_mid = self.findMidPrice(state, "PICNIC_BASKET2", 30300)
        calculated_value = (4 * croissant_mid) + (2 * jams_mid)
        
        #testing threshold value
        threshold = 0

        if basket_mid > calculated_value + threshold:
            
            # Basket is overpriced: sell basket and buy components.
            basket_depth = state.order_depths["PICNIC_BASKET2"]
            if basket_depth.buy_orders:
                
                # Sell Picnic Baskets
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
                
                # Buy Picnic Baskets
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
        
        # Update with new Orders
        return orders
    
    def fairPriceTrading(self,state,product):
        
        # Setup
        orders = []
        order_depth = state.order_depths[product]

        # Update price history
        self.updatePriceHistory(product, order_depth.buy_orders, order_depth.sell_orders)
        fair_price = self.getFairPrice(state,product)
        
        # Decide whether to Buy
        if order_depth.sell_orders:
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_volume = order_depth.sell_orders[best_ask]
            if best_ask <= fair_price:
                print(f"BUY {product} {-best_ask_volume}x at {best_ask}")
                orders.append(Order(product, best_ask, -best_ask_volume))

        # Decide whether to Sell
        if order_depth.buy_orders:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_volume = order_depth.buy_orders[best_bid]
            if best_bid >= fair_price:
                print(f"SELL {product} {best_bid_volume}x at {best_bid}")
                orders.append(Order(product, best_bid, -best_bid_volume))
        return orders
    
    def basketArbitrageTrading(self,state):
        
        # New Orders Array
        orders = []
        
        # For PICNIC_BASKET1: requires CROISSANTS, JAMS, and DJEMBES.
        if {"PICNIC_BASKET1", "CROISSANTS", "JAMS", "DJEMBES"}.issubset(state.order_depths.keys()):
            orders.extend(self.arbitrageBasket1(state))
            
        # For PICNIC_BASKET2: requires CROISSANTS and JAMS.
        if {"PICNIC_BASKET2", "CROISSANTS", "JAMS"}.issubset(state.order_depths.keys()):
            orders.extend(self.arbitrageBasket2(state))
            
        # Return New Array of Orders
        return orders
        
    def run(self, state):
        # Setup
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        
        # Execute basket arbitrage first (since it doesn't need product iteration)
        basket_orders = self.basketArbitrageTrading(state)
        for order in basket_orders:
            prod = order.symbol
            if prod not in result:
                result[prod] = []
            result[prod].append(order)

        # Process all products
        basket_products = {"PICNIC_BASKET1", "PICNIC_BASKET2"}
        blackScholesProducts = {"MAGNIFICENT_MACARONS"}
        
        for product in state.order_depths.keys():
            if product in basket_products:
                # Skip basket products as we already handled them
                continue
        for product in state.order_depths.keys():
            if product in basket_products:
                continue
            orders = self.fairPriceTrading(state, product)
            if orders:
                result[product] = orders

        # Persist the price history in traderData for the next iteration.
        trader_data = json.dumps({
            "price_history": {k: list(v) for k, v in self.priceHistory.items()}
        })
        conversions = 1  # Set conversion count according to your strategy.
        return result, conversions, trader_data
        
    
        
    
    