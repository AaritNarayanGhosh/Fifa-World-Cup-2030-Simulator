import pandas as pd
import numpy as np
import os
import sys

# Ensure imports work when run as script
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from recency_decay import RecencyDecay
from lqc_normalizer import LQCNormalizer
from database.db_manager import DBManager

class PlayerMetricsCalculator:
    def __init__(self):
        self.decay = RecencyDecay()
        self.lqc = LQCNormalizer()
        self.db = DBManager()
        
    def calculate_ratings(self, df=None):
        """
        Calculates Player Attacking Value (PAV) and Player Defensive Value (PDV).
        If df is None, pulls logs dynamically from the SQLite database.
        """
        if df is None:
            df = self.db.fetch_all_logs()
            # Map column names from lowercase SQLite schema to uppercase pandas expected schema
            column_mapping = {
                'player_id': 'Player_ID',
                'name': 'Name',
                'nationality': 'Nationality',
                'position': 'Position',
                'date': 'Date',
                'tier': 'Tier',
                'minutes': 'Minutes',
                'npxg_90': 'npxG_90',
                'xa_90': 'xA_90',
                'sca_90': 'SCA_90',
                'tackles_90': 'Tackles_90',
                'interceptions_90': 'Interceptions_90',
                'aerial_won_pct': 'AerialWon_pct',
                'psxg_ga_90': 'PSxG_GA_90'
            }
            df = df.rename(columns=column_mapping)
            
        if df.empty:
            print("Warning: Database/Logs DataFrame is empty.")
            return pd.DataFrame(columns=['Player_ID', 'Name', 'Nationality', 'Position', 'Minutes', 'PAV', 'PDV'])
            
        # 1. Apply decay and LQC
        df = self.decay.apply_decay(df)
        df = self.lqc.apply_lqc(df)
        
        # 2. Calculate match-level raw values
        df['Raw_PAV'] = df['npxG_90'] + 0.85 * df['xA_90'] + 0.15 * df['SCA_90']
        df['Raw_PDV'] = 0.4 * df['Tackles_90'] + 0.4 * df['Interceptions_90'] + 0.2 * df['AerialWon_pct']
        
        # 3. Multiply by Final Weight (w(t) * C_league)
        df['Weighted_PAV'] = df['Final_Match_Weight'] * df['Raw_PAV']
        df['Weighted_PDV'] = df['Final_Match_Weight'] * df['Raw_PDV']
        
        df.loc[df['Position'] == 'GK', 'Weighted_PDV'] = df['Final_Match_Weight'] * df['PSxG_GA_90']
        
        # 4. Group by Player and compute aggregated metrics
        agg_df = df.groupby(['Player_ID', 'Name', 'Nationality', 'Position']).agg({
            'Weighted_PAV': 'sum',
            'Weighted_PDV': 'sum',
            'Time_Weight': 'sum',
            'Minutes': 'sum'
        }).reset_index()
        
        # Calculate final PAV and PDV
        agg_df['PAV'] = agg_df['Weighted_PAV'] / (agg_df['Time_Weight'] + 1e-6)
        agg_df['PDV'] = agg_df['Weighted_PDV'] / (agg_df['Time_Weight'] + 1e-6)
        
        agg_df = agg_df[['Player_ID', 'Name', 'Nationality', 'Position', 'Minutes', 'PAV', 'PDV']]
        return agg_df

if __name__ == "__main__":
    calculator = PlayerMetricsCalculator()
    ratings_df = calculator.calculate_ratings()
    
    out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'aggregated_player_ratings.csv')
    
    ratings_df.to_csv(out_path, index=False)
    print(f"Aggregated {len(ratings_df)} player ratings from SQLite database.")
    print(ratings_df.head(10))
    print(f"Saved to {out_path}")
