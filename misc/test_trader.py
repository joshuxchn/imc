# test_trader.py

from datamodel import Listing, OrderDepth, Trade, TradingState, Observation
from round1 import Trader  # Adjust the import if your class has a different name
import json

# Create a sample listing dictionary
listings = {
    "SQUID_INK": Listing(symbol="SQUID_INK", product="SQUID_INK", denomination="SEASHELLS"),
    "KELP": Listing(symbol="KELP", product="KELP", denomination="SEASHELLS"),
    "RAINFOREST_RESIN": Listing(symbol="RAINFOREST_RESIN", product="RAINFOREST_RESIN", denomination="SEASHELLS")
}

# Create a sample order_depths with dummy data
order_depths = {
    "SQUID_INK": OrderDepth(),
    "KELP": OrderDepth(),
    "RAINFOREST_RESIN": OrderDepth()
}
# Populate a sample order depth (for testing purposes, you could use different prices/volumes)
order_depths["SQUID_INK"].buy_orders = {1968: 10}
order_depths["SQUID_INK"].sell_orders = {1972: -10}
order_depths["KELP"].buy_orders = {2030: 5}
order_depths["KELP"].sell_orders = {2032: -5}
order_depths["RAINFOREST_RESIN"].buy_orders = {10000: 10}
order_depths["RAINFOREST_RESIN"].sell_orders = {10002: -10}

# Set own_trades and market_trades to empty lists for now
own_trades = {"SQUID_INK": [], "KELP": [], "RAINFOREST_RESIN": []}
market_trades = {"SQUID_INK": [], "KELP": [], "RAINFOREST_RESIN": []}

# Set a sample position (e.g., initial zero position)
position = {"SQUID_INK": 0, "KELP": 0, "RAINFOREST_RESIN": 0}

# Create an Observation object (using empty dictionaries for this test)
observations = Observation(plainValueObservations={}, conversionObservations={})

# Initialize traderData as an empty string (or some initial state if needed)
initial_traderData = ""

# Create a sample TradingState object.
state = TradingState(
    traderData=initial_traderData,
    timestamp=1000,
    listings=listings,
    order_depths=order_depths,
    own_trades=own_trades,
    market_trades=market_trades,
    position=position,
    observations=observations
)

# Instantiate your Trader.
trader = Trader()

# Now run your algorithm.
result, conversions, new_traderData = trader.run(state)

# Print the output so you can inspect them.
print("Orders to place:")
for product, orders in result.items():
    print(f"{product}:")
    for order in orders:
        print("  ", order)
print("Conversions:", conversions)
print("New traderData:", new_traderData)
