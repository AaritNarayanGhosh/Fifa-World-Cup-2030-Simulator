import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self, start_date="2021-01-01", end_date="2026-06-01"):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        
    def generate_synthetic_player_logs(self, num_players=1000, logs_per_player=50):
        """
        Generates synthetic match logs for players across different leagues.
        This simulates the output of a merged FBref + Transfermarkt ingestion pipeline.
        """
        np.random.seed(42)
        positions = ['FW', 'AM', 'CM', 'DM', 'FB', 'CB', 'GK']
        tiers = {
            'Tier_1': ['EPL', 'La_Liga', 'UCL'],
            'Tier_2': ['Serie_A', 'Bundesliga', 'Ligue_1'],
            'Tier_3': ['Eredivisie', 'Liga_Portugal', 'Brasileirao', 'MLS'],
            'Tier_4': ['Saudi_Pro_League', 'Liga_MX', 'Championship'],
            'Tier_5': ['Other']
        }
        
        flat_leagues = [(tier, league) for tier, leagues in tiers.items() for league in leagues]
        
        data = []
        for i in range(num_players):
            player_id = f"P_{i:04d}"
            pos = np.random.choice(positions)
            tier, primary_league = flat_leagues[np.random.choice(len(flat_leagues))]
            
            # Generate random match dates within the 5-year window
            dates = [self.start_date + timedelta(days=np.random.randint(0, 1900)) for _ in range(logs_per_player)]
            
            for date in dates:
                log = {
                    'Player_ID': player_id,
                    'Position': pos,
                    'Date': date,
                    'League': primary_league,
                    'Tier': tier,
                    'Minutes': np.random.randint(15, 90),
                    
                    # Attacking
                    'npxG_90': np.clip(np.random.normal(0.2 if pos in ['FW', 'AM'] else 0.05, 0.2), 0, 1.5),
                    'xA_90': np.clip(np.random.normal(0.15 if pos in ['AM', 'CM', 'FB'] else 0.05, 0.1), 0, 1.0),
                    'SCA_90': np.clip(np.random.normal(3.0 if pos in ['AM', 'FW'] else 1.0, 1.5), 0, 8.0),
                    
                    # Defensive
                    'Tackles_90': np.clip(np.random.normal(2.5 if pos in ['DM', 'FB', 'CB'] else 0.5, 1.0), 0, 6.0),
                    'Interceptions_90': np.clip(np.random.normal(1.5 if pos in ['DM', 'CB'] else 0.3, 0.8), 0, 5.0),
                    'AerialWon_pct': np.clip(np.random.normal(0.6 if pos == 'CB' else 0.4, 0.15), 0, 1.0),
                    
                    # Goalkeeping
                    'PSxG_GA_90': np.clip(np.random.normal(0.0 if pos == 'GK' else 0.0, 0.5), -2.0, 2.0) if pos == 'GK' else 0.0
                }
                data.append(log)
                
        df = pd.DataFrame(data)
        df = df.sort_values(by=['Player_ID', 'Date'])
        return df

if __name__ == "__main__":
    loader = DataLoader()
    print("Generating synthetic player match logs (This may take a few seconds)...")
    df = loader.generate_synthetic_player_logs(num_players=2000, logs_per_player=40)
    
    out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'synthetic_player_logs.csv')
    
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} logs to {out_path}")
    print(df.head())
