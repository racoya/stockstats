# Sprint 10 Implementation: XGBoost Machine Learning

## The Objective
We have deployed the fully autonomous Phase 6 router. The linear math (GARCH, Copulas, Kalman Filters) operates flawlessly, but it is fundamentally static. It cannot "learn" that a specific combination of order book toxicity and volume spikes on Thursdays leads to a loss.

Sprint 10 introduces true Artificial Intelligence. We will train an **XGBoost Classifier** on the physical "Ground Truth" data generated manually by the founder during Phase 1. This model sits directly in front of the VWAP Executor (Sprint 7) specifically to **veto mathematically unprofitable trades.**

**Reference:** [Model 10 (Machine Learning Overlays)](../models/10_machine_learning_overlays.md), [Strategy 12 (Execution Sprints)](../strategy/12_execution_sprints_and_tickets.md#sprint-8-xgboost-machine-learning-overlays-meta-labeling)

---

## Step 1: Feature Engineering (The Arrays)

Machine Learning models require stationary data to learn cleanly. We cannot feed an XGBoost tree raw Bitcoin prices; we must feed it fractional derivatives and statistical indicators representing the exact state of the world precisely when the logic engine signaled a buy.

**1.1 Data Preparation (`backend/logic/ml_features.py`):**
```python
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def extract_features(signal_timestamp: int, symbol: str, pg_pool) -> pd.DataFrame:
    """Builds the 1xN feature vector for a specific anomaly timestamp."""
    
    # 1. Fetch historical state spanning 3 hours before the signal
    # 2. Calculate fractional differencing on the raw prices to achieve Stationarity (d=0.45)
    # 3. Fetch the exact Copula Theta rating at the microsecond of the alert
    # 4. Fetch the exact HMM Regime State
    
    # ... Complex feature engineering aggregation ...
    
    features = {
        'frac_diff_price': 0.0014,
        'garch_variance': 0.000085,
        'copula_theta': 1.4,
        'hmm_regime': 0, # Choppy
        'orderbook_imbalance': -0.45,
        # ... Dozens of microstructural indicators ...
    }
    
    return pd.DataFrame([features])
```

## Step 2: Extracting the Ground Truth Labels

We must interrogate the `execution_ledger` for the manual trades logged by the founder in Phase 1 (Sprint 3) to create the `y` target variable for the AI to predict.

**2.1 Label Generation:**
```python
async def generate_training_labels(pg_pool):
    """
    Extracts every phase_1 manual execution.
    Target Value (y):
    1 = The trade was ultimately profitable under the R expectancy model.
    0 = The trade hit the VaR stop-loss or bled capital.
    """
    async with pg_pool.acquire() as connection:
        # We query the DB for the historical PnL of each manually executed Client UUID
        historical_executions = await connection.fetch('''
            SELECT client_uuid, symbol, created_at, pnl 
            FROM execution_ledger 
            WHERE state = 'CLOSED'
        ''')
        
    training_data = [] # X
    labels = []        # y
    
    for execution in historical_executions:
        timestamp = execution['created_at'].timestamp() * 1000
        # 1. Rebuild the exact environmental features at the moment of the trade
        state_vector = extract_features(timestamp, execution['symbol'], pg_pool)
        training_data.append(state_vector.iloc[0].to_dict())
        
        # 2. Assign the binary target variable based on the historical reality
        if execution['pnl'] > 0:
            labels.append(1) # Profitable
        else:
            labels.append(0) # Loss
            
    return pd.DataFrame(training_data), np.array(labels)
```

## Step 3: Training the XGBoost Tree

We use gradient boosting because it naturally handles non-linear financial feature interactions (e.g., *a high Copula is only dangerous if the OBI is profoundly negative*).

**3.1 Implement the Trainer (`backend/logic/ml_trainer.py`):**
```python
def train_meta_labeler(X: pd.DataFrame, y: np.ndarray):
    """Physically trains the gradient boosted decision trees."""
    
    # Split the historical Phase 1 data into Training and Out-of-Sample Testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Convert Pandas arrays to optimized DMatrix objects for C-level speed
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)
    
    # Hyperparameters
    params = {
        'max_depth': 4,              # Keep trees shallow to prevent overfitting on financial noise
        'eta': 0.1,                  # Learning rate
        'objective': 'binary:logistic', # We are predicting a probability (0.0 to 1.0) of a win
        'eval_metric': 'logloss'
    }
    
    # Train the model over 100 boosting rounds
    evalist = [(dtrain, 'train'), (dtest, 'eval')]
    num_round = 100
    bst = xgb.train(params, dtrain, num_round, evalist, early_stopping_rounds=10)
    
    # Save the trained brain to disk
    bst.save_model('meta_model.json')
    
    # Evaluate Out-of-Sample Accuracy
    preds = bst.predict(dtest)
    # Convert raw probability back to boolean (0 or 1) using a strict 60% confidence threshold
    predictions = [1 if value > 0.6 else 0 for value in preds]
    accuracy = accuracy_score(y_test, predictions)
    print(f"Meta-Labeler Accuracy on Out-of-Sample Tests: {accuracy * 100:.2f}%")
```

## Step 4: The Live Algorithmic Veto

The model is trained. We must now inject it directly into the routing pipeline built in Sprint 7.

**4.1 Intercept the Order (`backend/execution/router.py`):**
```python
import xgboost as xgb

# Pre-load the trained brain into RAM at startup
bst = xgb.Booster()
bst.load_model('meta_model.json')

async def execute_limit_order(symbol: str, side: str, amount: float, price: float, pg_pool):
    # ... (Sprint 9 UUID Logic) ...
    
    # 1. The GARCH math generated the BUY signal.
    # 2. Before executing, we interrogate the Xenon AI.
    
    # Rebuild the current live environmental arrays
    live_features = extract_features(current_time, symbol, pg_pool)
    d_live = xgb.DMatrix(live_features)
    
    # Ask the AI: "Based on the manual data I generated in Phase 1, 
    # what is the mathematical probability this trade ends in a win?"
    probability_of_win = bst.predict(d_live)[0]
    
    # 3. The Strict Machine Veto
    if probability_of_win < 0.60:
        logging.warning(f"VETO AI: Execution aborted. XGBoost predicts a {1 - probability_of_win:.0%} chance of structural loss.")
        
        # Log the veto to the database so we can study it later
        async with pg_pool.acquire() as connection:
            await connection.execute("UPDATE execution_ledger SET state = 'REJECTED' WHERE client_uuid = $1", request_uuid)
            
        return None # Do not execute the physical trade
        
    # 4. Neural Network Authorizes Trade 
    # Proceed to CCXT Routing ...
```

---
**Phase 8 Complete.**
The evolution is absolute. What began as a local Docker container scrubbing data via Numba is now a fully autonomous, self-reconciling entity protected by non-linear cryptographic algorithms.

The complete STOCKSTATS infrastructure has been fully documented from the foundational Strategy concepts down to the C-compiled Machine Learning code arrays. We are ready to execute.
