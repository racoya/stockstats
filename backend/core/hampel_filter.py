import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class HampelFilter:
    """
    Data Sterilization Engine.
    Uses the Hampel Filter (Median Absolute Deviation - MAD) to autonomously detect
    and scrub structurally impossible 'rogue ticks' or flash crashes from live exchange feeds
    before they poison the downstream quantitative models (GARCH/Cointegration).
    """
    def __init__(self, window_size: int = 21, sigma_multiplier: float = 3.0):
        """
        :param window_size: The rolling lookback window for the median calculation. Must be odd.
        :param sigma_multiplier: The stringency of the filter. 3.0 is standard (~99.7% of Gaussian data).
        """
        if window_size % 2 == 0:
            window_size += 1 # Ensure odd window size for strict median
        self.window_size = window_size
        self.sigma_multiplier = sigma_multiplier

    def apply(self, price_series: pd.Series) -> pd.Series:
        """
        Applies the Hampel Filter to historical arrays for backtesting and model fitting.
        Replaces detected outliers with the rolling median.
        """
        # Ensure we have a pandas Series
        if not isinstance(price_series, pd.Series):
            price_series = pd.Series(price_series)

        # 1. Calculate Rolling Median
        rolling_median = price_series.rolling(window=self.window_size, center=False).median()

        # 2. Calculate Rolling Median Absolute Deviation (MAD)
        # Using the standard scaling factor 1.4826 to makeMAD a consistent estimator of standard deviation
        mad_scaling_factor = 1.4826
        rolling_mad = (price_series - rolling_median).abs().rolling(window=self.window_size, center=False).median() * mad_scaling_factor

        # 3. Define the Outlier Thresholds
        upper_bound = rolling_median + (self.sigma_multiplier * rolling_mad)
        lower_bound = rolling_median - (self.sigma_multiplier * rolling_mad)

        # 4. Identify Outliers
        outliers_boolean = (price_series > upper_bound) | (price_series < lower_bound)
        
        # Log the scrubbing event for audit
        num_outliers = outliers_boolean.sum()
        if num_outliers > 0:
            logger.warning(f"Hampel Filter detected and scrubbed {num_outliers} rogue ticks out of {len(price_series)} observations.")

        # 5. Scrub the Data: Replace outliers with the rolling median
        scrubbed_series = price_series.copy()
        scrubbed_series[outliers_boolean] = rolling_median[outliers_boolean]

        return scrubbed_series

    def check_live_tick(self, latest_tick_price: float, historical_window: pd.Series) -> dict:
        """
        Analyzes a single live tick against the immediately preceding historical window.
        Used continuously inside the WebSocket stream before writing to the database.
        
        :param latest_tick_price: The incoming WebSocket tick
        :param historical_window: The last `self.window_size` prices required to calculate median
        """
        if len(historical_window) < self.window_size:
             # Not enough data to confidently filter, allow it through
             return {"is_valid": True, "scrubbed_price": latest_tick_price, "reason": "insufficent_data"}
             
        current_median = historical_window.median()
        absolute_deviations = (historical_window - current_median).abs()
        current_mad = absolute_deviations.median() * 1.4826

        # Avoid Division by Zero if the market is totally flat (e.g., stablecoin peg)
        if current_mad == 0:
             return {"is_valid": True, "scrubbed_price": latest_tick_price, "reason": "zero_mad"}

        # Calculate Z-Score equivalent using MAD
        mad_z_score = abs(latest_tick_price - current_median) / current_mad

        if mad_z_score > self.sigma_multiplier:
            logger.error(f"LIVE SENSOR TRIPPED: Rogue tick detected ({latest_tick_price}). Scrubbing to median ({current_median}).")
            return {
                "is_valid": False, 
                "scrubbed_price": current_median, # Return the median to substitute
                "reason": "mad_boundary_exceeded"
            }
            
        return {"is_valid": True, "scrubbed_price": latest_tick_price, "reason": "clean"}
