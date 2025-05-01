# IMC Prosperity Trading Competition
**[IMC Prosperity Wiki](https://imc-prosperity.notion.site/Prosperity-3-Wiki-19ee8453a09380529731c4e6fb697ea4)**  

## Context

IMC Prosperity is an algorithm trading competition that lasts over 15 days, with over 12,000 teams globally. In each of the 5 rounds, new products were introduced that we had to trade with through a Python algorithm. With indicators such as provided historical data of these products, teams could identify trends to shape their strategies. At the end of each round, the algorithm would then be tested with (hidden) data that had 1 million ticks (time) of trades. The profit accumulated through these rounds was compared to other teams in the tournament.

There was also a manual trading position in the form of small challenges in each round; however, manual trading ended up a fraction of our total PNL.

## Round 1

Round 1 introduced 3 products to trade: rainforest resin, squid ink, and kelp. From the historical data of the products, rainforest resin was very stable, only deviating from the 10k price by a small amount. As such, we implemented a fair price strategy, buying when the resin was below the fair price and selling when above. Testing our implementation with 100k ticks led us to make around 200 seashells.

Unfortunately, midterm season was in full swing and we didn't have time to figure out squid ink and kelp, so we didn't trade those products. We also didn't perform any manual trades, and we lost out on potential profits for our overall score.

At the end of round 1, we had a total profit of 239 seashells.

## Round 2

Round 2 introduced new products:

- **Picnic Basket 1** contained:
  - 6 croissants, 3 jams, 1 djembe
- **Picnic Basket 2** contained:
  - 4 croissants, 2 jams

Each basket was a product itself, and the products inside the baskets could be traded individually as well.

After research, we converged on a popular trading hypothesis called arbitrage. In short, if the sum of the individual costs of the products inside a picnic basket had a large difference with the actual price of the picnic basket, we could buy or sell for profit. In addition, this strategy allowed us to short stocks and sell until we hit our max quota (-50 baskets). This actually took quite some time to implement, as we had to change the logic of many functions to allow us to short products.

Next, we went back to round 1 products: rainforest resin, squid ink, and kelp. Both products were very similar in volatility, and we didn't notice or anticipate any sharp changes in price trends. As such, we implemented a moving average, taking the mid-price within a certain time frame. We also tweaked the time frame for each product (kelp around 100 ticks, squid ink 50 ticks).

At the end of the round, we made 36k seashells from algo trading.
<img width="700" alt="image" src="https://github.com/user-attachments/assets/feca60c2-987d-44d9-aaa6-430fdefd63ab" />


## Round 3

Round 3 introduced multiple Volcanic vouchers, essentially options: purchasing a voucher gave us the right to purchase the volcanic rock product at the "strike price". Honestly, we didn't really understand how to trade options and a good strategy to do so; we tried a regression strategy of sorts but had large losses and scrapped that.

As such, we focused on refining our strategies from previous rounds, as the trend of our profits was still fairly volatile. After examining the data from round 2, we noticed that while picnic basket 1 was making large earnings (8k+), picnic basket 2 profit was near 0.

In addition, with our moving average strategy, our kelp results from the previous were in the negatives. Interestingly enough, the same mid-price strategy worked very well for squid ink in the previous round, but not for kelp. We tried tuning the frequency at which we calculated the mid-price, but we were never able to create PNL greater than 1000 seashells.

Lastly, we implemented a simple fair price strategy with Volcanic rock, buying and selling over a certain price. This was a last minute hail mary as we approached the deadline, and we got very lucky.

With these edits, we made over 275k seashells from algorithmic trading, placing us in the "elite contenders" category at #119 for algorithm trading.

<img width="700" alt="image" src="https://github.com/user-attachments/assets/92f038e5-d335-42dc-a31c-7e73125fee56" />

<img width="700" alt="image" src="https://github.com/user-attachments/assets/9ceadf27-e20e-4c40-8b47-29176810d676" />


## Reflection

For knowing nothing about trading prior to the competition, we were pretty happy to be placed in the top 0.5% (out of ~10,000 teams) of the algorithm trading competition. Even though we did get fortunate profits when shorting the volcanic rock and vouchers, we genuinely made very effective algorithms for picnic baskets, squid ink, and rainforest resin. We had a great experience and are eager to try again next year.
