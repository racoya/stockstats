import numpy as np
import pandas as pd
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class OrderBookToxicityDetector:
    """
    High-Frequency Trading Defense Mechanism.
    Analyzes Level 2 (L2) Order Book Snapshots to calculate the Order Book Imbalance (OBI).
    Detects predatory 'spoofing' algorithms and pauses the VWAP slicing execution algorithm
    if the market microstructure is toxic (highly adversarial).
    """
    def __init__(self, toxicity_threshold: float = +0.7, depth_levels: int = 5):
        """
        :param toxicity_threshold: 0.7 means 85% of book volume is on one side (Adverse Selection risk).
        :param depth_levels: How many price levels deep into L2 to analyze (e.g., top 5 Bids vs top 5 Asks).
        """
        self.toxicity_threshold = toxicity_threshold
        self.depth_levels = depth_levels

    def _extract_volumes(self, book_side: List[Tuple[float, float]], levels: int) -> float:
        """
        Extracts the total volume from a specific side of the order book up to `levels` depth.
        Assumes book_side is a list of [price, size] arrays/tuples.
        """
        if not book_side:
            return 0.0
            
        # Ensure we don't index out of bounds if the book is thin
        analyze_levels = min(len(book_side), levels)
        
        total_volume = 0.0
        for i in range(analyze_levels):
            # book_side[i][1] is the Size/Volume at that price level
            total_volume += float(book_side[i][1]) 
            
        return total_volume

    def calculate_obi(self, bids: List[Tuple[float, float]], asks: List[Tuple[float, float]]) -> float:
        """
        Calculates the Order Book Imbalance (OBI).
        Equation: (Bid_Volume - Ask_Volume) / (Bid_Volume + Ask_Volume)
        
        Range is [-1.0, 1.0]
        -1.0 = 100% of volume is Asks (Massive downward pressure / spoofing)
         1.0 = 100% of volume is Bids (Massive upward pressure / spoofing)
         0.0 = Perfectly balanced book
        """
        bid_vol = self._extract_volumes(bids, self.depth_levels)
        ask_vol = self._extract_volumes(asks, self.depth_levels)
        
        total_vol = bid_vol + ask_vol
        
        if total_vol == 0:
            return 0.0 # Prevent division by zero if book is totally empty (exchange halt)
            
        obi = (bid_vol - ask_vol) / total_vol
        return obi

    def evaluate_execution_safety(self, bids: List[Tuple[float, float]], asks: List[Tuple[float, float]], intended_side: str) -> dict:
        """
        The Master Veto Switch for the Execution Engine.
        Analyzes the current L2 snapshot and immediately warns if HFT spoofing is 
        stacked against our intended execution direction.
        
        :param intended_side: 'BUY' or 'SELL'.
        """
        obi = self.calculate_obi(bids, asks)
        
        is_safe = True
        reason = "optimal_liquidity"
        
        if intended_side.upper() == "BUY":
            # If we want to BUY, we get hurt if HFTs are spoofing massive ASKS above us
            # to drive the price down right before they pull them and buy into us.
            if obi <= -self.toxicity_threshold:
                is_safe = False
                reason = "predatory_hft_ask_spoofing"
                logger.warning(f"TOXICITY VETO (BUY): Massive Ask Imbalance (OBI: {obi:.3f}). HFT spoofing detected. Pausing slice.")
                
        elif intended_side.upper() == "SELL":
            # If we want to SELL, we get hurt if HFTs are spoofing massive BIDS below us
            # (Iceberging) to drive the price up before pulling.
            if obi >= self.toxicity_threshold:
                is_safe = False
                reason = "predatory_hft_bid_spoofing"
                logger.warning(f"TOXICITY VETO (SELL): Massive Bid Imbalance (OBI: {obi:.3f}). HFT spoofing detected. Pausing slice.")

        return {
            "is_safe": is_safe,
            "current_obi": obi,
            "toxicity_threshold": self.toxicity_threshold,
            "reason": reason
        }
