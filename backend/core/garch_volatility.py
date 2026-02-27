import numpy as np
import pandas as pd
from arch import arch_model
import logging

logger = logging.getLogger(__name__)

class GARCHVolatilityModel:
    """
    Generalized Autoregressive Conditional Heteroskedasticity (GARCH(1,1)) model.
    Forecasts dynamic, time-varying volatility by exponentially weighting recent
    price shocks, avoiding the lag of simple moving standard deviation.
    """
    def __init__(self, p=1, q=1, mean='Constant', vol='GARCH', dist='Normal'):
        self.p = p
        self.q = q
        self.mean = mean
        self.vol = vol
        self.dist = dist
        self.model_result = None
        self.is_fitted = False

    def _calculate_returns(self, prices: pd.Series) -> pd.Series:
        """
        Calculates logarithmic returns from a price series.
        Multiplying by 100 for numerical stability during MLE optimization in arch.
        """
        returns = np.log(prices / prices.shift(1)).dropna() * 100.0
        return returns

    def fit(self, historical_prices: pd.Series):
        """
        Fits the GARCH(1,1) model to historical price data using Maximum Likelihood Estimation.
        """
        returns = self._calculate_returns(historical_prices)
        
        logger.info(f"Fitting {self.vol}({self.p},{self.q}) on {len(returns)} observations...")
        
        am = arch_model(
            returns, 
            mean=self.mean, 
            vol=self.vol, 
            p=self.p, 
            q=self.q, 
            dist=self.dist
        )
        
        # disp='off' suppresses the optimization iteration output
        self.model_result = am.fit(update_freq=0, disp='off')
        self.is_fitted = True
        logger.info("GARCH Model successfully fitted.")

    def forecast_current_volatility(self, horizon=1) -> float:
        """
        Forecasts the conditional volatility (standard deviation) for the next `horizon` periods.
        """
        if not self.is_fitted:
            raise ValueError("GARCH Model must be fitted before forecasting.")
            
        forecasts = self.model_result.forecast(horizon=horizon)
        
        # Extract the variance forecast for the next immediate period (t+1)
        # Note: arch returns variance, we need standard deviation
        next_variance = forecasts.variance.iloc[-1, 0]
        
        # Divide by 100 to reverse the scaling done during returns calculation
        conditional_std_dev = np.sqrt(next_variance) / 100.0
        
        return conditional_std_dev

    def generate_dynamic_bands(self, current_price: float, multiplier: float = 2.0) -> dict:
        """
        Generates instantaneous upper and lower trading bands based on the GARCH forecast.
        Replaces static Bollinger Bands.
        """
        cond_std = self.forecast_current_volatility()
        
        band_distance = current_price * (cond_std * multiplier)
        
        upper_band = current_price + band_distance
        lower_band = current_price - band_distance
        
        return {
            "current_price": current_price,
            "conditional_std_dev": cond_std,
            "multiplier": multiplier,
            "upper_band": upper_band,
            "lower_band": lower_band
        }
