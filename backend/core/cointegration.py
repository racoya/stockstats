import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import logging

logger = logging.getLogger(__name__)

class CointegrationEngine:
    """
    Statistical Arbitrage Engine.
    Uses Ordinary Least Squares (OLS) to calculate the Hedge Ratio between two assets,
    and the Augmented Dickey-Fuller (ADF) test to mathematically prove the resulting
    spread is stationary (mean-reverting).
    """
    def __init__(self, adf_pvalue_threshold=0.05):
        self.adf_pvalue_threshold = adf_pvalue_threshold

    def _calculate_hedge_ratio_ols(self, price_a: pd.Series, price_b: pd.Series) -> float:
        """
        Calculates the static Hedge Ratio (Beta) via OLS regression.
        Equation: PriceA = Alpha + Beta * PriceB + Error
        """
        # Add a constant to Asset B (the independent variable)
        X = sm.add_constant(price_b)
        
        # Fit OLS: y = Price_A, X = [const, Price_B]
        model = sm.OLS(price_a, X).fit()
        
        # model.params[0] is the Intercept (Alpha)
        # model.params[1] is the Slope (Beta / Hedge Ratio)
        hedge_ratio = model.params[1]
        
        return hedge_ratio

    def build_spread(self, price_a: pd.Series, price_b: pd.Series) -> tuple[pd.Series, float]:
        """
        Extracts the residual error (the Spread) using the OLS Hedge Ratio.
        """
        hedge_ratio = self._calculate_hedge_ratio_ols(price_a, price_b)
        spread = price_a - (hedge_ratio * price_b)
        
        return spread, hedge_ratio

    def is_cointegrated(self, spread: pd.Series) -> dict:
        """
        Executes the Augmented Dickey-Fuller test on the Spread array.
        Returns authorization boolean and statistical metrics.
        """
        logger.info("Executing ADF stationarity test on spread...")
        
        # Run ADF Test
        # adf_result contains: [adf_statistic, p_value, usedlag, nobs, critical_values, icbest]
        adf_result = adfuller(spread)
        
        adf_statistic = adf_result[0]
        p_value = adf_result[1]
        critical_values = adf_result[4]
        
        is_stationary = p_value <= self.adf_pvalue_threshold
        
        if is_stationary:
            logger.info(f"AUTHORIZED: Pair is cointegrated (p-value: {p_value:.4f})")
        else:
            logger.warning(f"VETO: Spread is a Random Walk (p-value: {p_value:.4f})")
            
        return {
            "is_cointegrated": is_stationary,
            "p_value": p_value,
            "adf_statistic": adf_statistic,
            "critical_values": critical_values
        }

    def generate_signal(self, current_spread_val: float, historical_spread: pd.Series, dynamic_std_dev: float = None) -> dict:
        """
        Calculates the real-time Z-Score of the spread.
        If dynamic_std_dev (from GARCH) is provided, it uses that for superior reactivity.
        Otherwise, falls back to the simple standard deviation of the historical spread.
        """
        spread_mean = historical_spread.mean()
        
        if dynamic_std_dev is not None:
            # Institutional: Use GARCH Volatility
            z_score = (current_spread_val - spread_mean) / dynamic_std_dev
        else:
            # Retail constraint: Use Simple Moving StdDev
            spread_std = historical_spread.std()
            z_score = (current_spread_val - spread_mean) / spread_std
            
        action = "HOLD"
        # Typical StatArb execution thresholds
        if z_score >= 2.0:
            action = "SHORT_SPREAD"  # Spread is too wide, expect it to contract
        elif z_score <= -2.0:
            action = "LONG_SPREAD"   # Spread is too narrow, expect it to widen
        elif abs(z_score) <= 0.1:
            action = "FLATTEN"       # Spread reverted to mean, close all legs
            
        return {
            "z_score": z_score,
            "action": action,
            "spread_value": current_spread_val,
            "spread_mean": spread_mean
        }
