from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict
import json
import math


def getFairResin(buyOrders,sellOrders):
    return 100000

def getFairPrice(buyOrders,sellOrders,product):
    if product == "RAINFOREST_RESIN":
        return getFairResin(buyOrders,sellOrders)
    elif product == "SQUID_INK":
        return getFairResin()
    else:
        return 10

class Trader:

    def getFairPrice(buyOrders,sellOrders,product):
        if product == "RAINFOREST_RESIN":
            return getFairResin(buyOrders,sellOrders)
        else:
            return 10

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        #Initiation
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}

        #Check Each Product
        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            buyOrders = order_depth.buy_orders.keys()
            sellOrders = order_depth.sell_orders.keys()

            #Calculate Acceptable Price
            fairPrice = getFairPrice(buyOrders,sellOrders,product)

            # Checking Sell Orders
            if len(order_depth.sell_orders) > 0:

                # Sort all the available sell orders by their price,
                # and select only the sell order with the lowest price
                lowestSell = min(sellOrders)
                lowestSellVolume = order_depth.sell_orders[lowestSell]

                # Check that lowestSell is lower than the fairPrice
                if lowestSell <= fairPrice:

                    # In case the lowest ask is lower than our fair value,
                    # This presents an opportunity for us to buy cheaply
                    print("BUY", str(-lowestSellVolume) + "x", lowestSell)
                    orders.append(Order(product, lowestSell, -lowestSellVolume))

            # Check Bid Orders and buy up cheap bids
            if len(order_depth.buy_orders) != 0:
                highestBid = max(order_depth.buy_orders.keys())
                highestBidVolume = order_depth.buy_orders[highestBid]

                # Check that 
                if highestBid > fairPrice:
                    print("SELL", str(highestBidVolume) + "x", highestBid)
                    orders.append(Order(product, highestBid, -highestBidVolume))

            # Add all the above the orders to the result dict
            result[product] = orders
            
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
    
        conversions = 1 
        return result, conversions, traderData