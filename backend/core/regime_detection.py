import numpy as np
import pandas as pd
from hmmlearn import hmm
import logging

logger = logging.getLogger(__name__)

class RegimeDetectionHMM:
    """
    Gaussian Hidden Markov Model (HMM) for detecting market regimes based on 
    observable returns and realized volatility.
    
    Identifies 3 market states:
    - State 0: Low Volatility (Ranging/Mean-Reverting)
    - State 1: High Volatility (Trending Up or Down)
    - State 2: Extreme Volatility (Crash/Panic)
    """
    def __init__(self, n_components=3, n_iter=1000, covariance_type="full", random_state=42):
        self.n_components = n_components
        self.n_iter = n_iter
        self.covariance_type = covariance_type
        self.random_state = random_state
        self.model = None
        self.is_fitted = False

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepares the observable emissions array for the HMM.
        Requires 'close' prices and ideally a 'garch_volatility' column.
        
        If garch_volatility is missing, it falls back to a rolling standard deviation.
        """
        # Calculate log returns
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Fallback for volatility if GARCH is not pre-calculated by Phase 1 engines
        if 'garch_volatility' not in df.columns:
            logger.warning("GARCH volatility missing. Falling back to rolling std_dev (win=20).")
            df['realized_volatility'] = df['log_returns'].rolling(window=20).std()
        else:
            df['realized_volatility'] = df['garch_volatility']

        # Drop NaNs introduced by shifts/rolling windows
        clean_df = df.dropna(subset=['log_returns', 'realized_volatility']).copy()
        
        # Format as 2D array [Returns, Volatility]
        X = np.column_stack([clean_df['log_returns'].values, clean_df['realized_volatility'].values])
        return X

    def fit(self, historical_data: pd.DataFrame):
        """
        Fits the Gaussian HMM to historical data to define the transition matrices
        and state clusters.
        """
        X = self.prepare_features(historical_data)
        
        logger.info(f"Fitting GaussianHMM({self.n_components}) on {len(X)} observations...")
        
        self.model = hmm.GaussianHMM(
            n_components=self.n_components, 
            covariance_type=self.covariance_type, 
            n_iter=self.n_iter,
            random_state=self.random_state
        )
        
        self.model.fit(X)
        self.is_fitted = True
        logger.info("HMM Model successfully fitted.")

    def predict_current_regime(self, recent_data: pd.DataFrame) -> dict:
        """
        Predicts the current hidden state based on recent observations.
        Acts as the Veto switch for the Execution Engine.
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted with historical data before predicting regimes.")

        X_recent = self.prepare_features(recent_data)
        
        # Predict the sequence of states
        hidden_states = self.model.predict(X_recent)
        
        # The current state is the very last prediction in the array
        current_state = hidden_states[-1]
        
        # Extract the probability of being in this state
        probabilities = self.model.predict_proba(X_recent)
        current_prob = probabilities[-1][current_state]

        # Map state to Execution Protocol logic
        # Note: HMM states are clustered randomly. We sort by variance to standardize.
        variances = np.array([np.diag(cov) for cov in self.model.covars_])
        volatility_sorted_indices = np.argsort(variances[:, 1]) # Sort by the second feature (Volatility)
        
        # Re-map the raw current_state to our strict 0, 1, 2 definitions
        mapped_state = list(volatility_sorted_indices).index(current_state)

        protocol_action = self._map_action_to_state(mapped_state)

        return {
            "mapped_state_id": mapped_state,
            "probability": current_prob,
            "action": protocol_action,
            "raw_hmm_state": current_state
        }

    def _map_action_to_state(self, mapped_state: int) -> str:
        """
        Executes the exact logic defined in whitepaper 03_hmm_regime_detection.md
        """
        if mapped_state == 0:
            return "AUTHORIZE_MEAN_REVERSION" # Ranging Environment
        elif mapped_state == 1:
            return "VETO_MEAN_REVERSION_AUTHORIZE_MOMENTUM" # Trending Environment
        elif mapped_state == 2:
            return "TRIGGER_SYSTEMIC_KILL_SWITCH" # Crash/Panic Environment
        else:
            return "UNKNOWN_STATE_VETO_ALL"
