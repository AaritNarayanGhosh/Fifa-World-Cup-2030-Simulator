import pandas as pd
import numpy as np

class RecencyDecay:
    def __init__(self, half_life_days=365):
        self.half_life_days = half_life_days
        self.gamma = np.log(2) / self.half_life_days
        
    def apply_decay(self, df, date_col='Date', current_date=None):
        """
        Calculates the exponential recency weight for each match log.
        """
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        if current_date is None:
            # If no current date is provided, assume the latest date in the dataset
            current_date = df[date_col].max()
        else:
            current_date = pd.to_datetime(current_date)
            
        # Time difference in days
        time_diff = (current_date - df[date_col]).dt.days
        
        # Avoid negative days if current_date is somehow before match date
        time_diff = np.maximum(time_diff, 0)
        
        # Calculate weight: w(t) = exp(-gamma * delta_t)
        df['Time_Weight'] = np.exp(-self.gamma * time_diff)
        
        return df

if __name__ == "__main__":
    # Simple test
    dates = pd.DataFrame({'Date': ['2026-06-01', '2025-06-01', '2024-06-01']})
    decay = RecencyDecay(half_life_days=365)
    weighted_df = decay.apply_decay(dates, current_date='2026-06-01')
    print("Recency Weights Validation:")
    print(weighted_df)
