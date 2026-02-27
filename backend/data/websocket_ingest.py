import asyncio
import ccxt.pro as ccxtpro
import logging
from collections import deque
import pandas as pd

# Import the defense modules (assume they are in the python path or relative)
from core.hampel_filter import HampelFilter
from core.l2_toxicity import OrderBookToxicityDetector

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ExchangeWebsocketStreamer:
    """
    Asynchronous Data Ingestion Engine using CCXT Pro.
    Connects to exchange WebSockets to stream L1 (Trades) and L2 (Orderbook) data.
    All data is immediately sterilized through the Hampel Filter and Toxicity detectors
    before being passed down to the mathematical pricing engine.
    """
    def __init__(self, exchange_id: str = 'binance', symbols: list = None):
        self.exchange_id = exchange_id
        self.symbols = symbols if symbols else ['BTC/USDT', 'ETH/USDT']
        
        # Initialize CCXT Async Exchange instance
        exchange_class = getattr(ccxtpro, self.exchange_id)
        self.exchange = exchange_class({'enableRateLimit': True})
        
        # Defense Mechanisms
        self.hampel_filter = HampelFilter(window_size=21, sigma_multiplier=3.0)
        self.toxicity_detector = OrderBookToxicityDetector(toxicity_threshold=0.7, depth_levels=5)
        
        # In-Memory Rolling Windows (Fast storage before DB write)
        self.recent_trades = {sym: deque(maxlen=100) for sym in self.symbols}
        self.current_orderbook = {sym: {'bids': [], 'asks': []} for sym in self.symbols}

    async def stream_trades(self, symbol: str):
        """
        Subscribes to live public trades (Tick Data).
        Applies Hampel Filter sterilization before appending to the rolling window.
        """
        logger.info(f"Subscribing to Trades stream for {symbol} on {self.exchange_id}")
        while True:
            try:
                trades = await self.exchange.watch_trades(symbol)
                for trade in trades:
                    price = float(trade['price'])
                    
                    # Convert deque to pandas Series for the Hampel Filter
                    historical_window = pd.Series([t['price'] for t in self.recent_trades[symbol]])
                    
                    # Sterilize the tick
                    scrub_result = self.hampel_filter.check_live_tick(price, historical_window)
                    
                    if not scrub_result['is_valid']:
                        # Rogue tick detected! Replace the price with the median scrubbed price
                        logger.warning(f"Trade payload sterilized: Original {price} -> Scrubbed {scrub_result['scrubbed_price']}")
                        trade['price'] = scrub_result['scrubbed_price']
                        trade['is_scrubbed'] = True
                    else:
                        trade['is_scrubbed'] = False

                    # Append to fast-access memory for the math models
                    self.recent_trades[symbol].append(trade)
                    
                    # In a production environment, this is where we would trigger an async 
                    # event to Kafka or a callback to the GARCH model.
                    
            except ccxtpro.NetworkError as e:
                logger.error(f"Network error streaming trades for {symbol}: {str(e)}")
                await asyncio.sleep(1) # Backoff
            except Exception as e:
                logger.error(f"Critical error streaming trades for {symbol}: {str(e)}")
                break

    async def stream_orderbook(self, symbol: str):
        """
        Subscribes to live L2 Order Book snapshots.
        Applies Order Book Imbalance (OBI) tracking to constantly monitor for HFT Toxicity.
        """
        logger.info(f"Subscribing to OrderBook stream for {symbol} on {self.exchange_id}")
        while True:
            try:
                orderbook = await self.exchange.watch_order_book(symbol)
                
                # Update local state
                self.current_orderbook[symbol]['bids'] = orderbook['bids']
                self.current_orderbook[symbol]['asks'] = orderbook['asks']
                
                # Calculate Toxicity Metrics continuously
                obi = self.toxicity_detector.calculate_obi(
                    bids=orderbook['bids'], 
                    asks=orderbook['asks']
                )
                
                # If OBI is extremely toxic, we could emit a system-wide flag here to 
                # pause the VWAP Execution engine.
                if abs(obi) > 0.8:
                    logger.warning(f"[{symbol}] Extreme Order Book Toxicity Detected! OBI: {obi:.3f}")

            except ccxtpro.NetworkError as e:
                logger.error(f"Network error streaming orderbook for {symbol}: {str(e)}")
                await asyncio.sleep(1) # Backoff
            except Exception as e:
                logger.error(f"Critical error streaming orderbook for {symbol}: {str(e)}")
                break

    async def start(self):
        """
        Initializes the concurrent WebSocket streams.
        """
        tasks = []
        for symbol in self.symbols:
            tasks.append(self.stream_trades(symbol))
            tasks.append(self.stream_orderbook(symbol))
            
        await asyncio.gather(*tasks)

    async def close(self):
        """Cleanly close the exchange connection."""
        await self.exchange.close()

# Used for local testing
if __name__ == "__main__":
    streamer = ExchangeWebsocketStreamer(exchange_id='binance', symbols=['BTC/USDT'])
    try:
        asyncio.run(streamer.start())
    except KeyboardInterrupt:
        asyncio.run(streamer.close())
        logger.info("Websocket stream closed cleanly.")
