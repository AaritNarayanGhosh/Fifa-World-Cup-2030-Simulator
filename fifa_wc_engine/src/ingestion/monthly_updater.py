import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Path setup
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager
from ingestion.kaggle_downloader import KaggleDownloader

class MonthlyUpdater:
    def __init__(self):
        self.db = DBManager()
        self.downloader = KaggleDownloader()
        
    def check_for_delta(self):
        """
        Determines the last date of logs stored in SQLite database.
        """
        logs = self.db.fetch_all_logs()
        if logs.empty:
            # If database is empty, seed it with the baseline 5-year logs
            baseline_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'synthetic_player_logs.csv')
            if os.path.exists(baseline_path):
                print("Seeding SQLite database with baseline 5-year match logs...")
                baseline_df = pd.read_csv(baseline_path)
                self.db.insert_match_logs(baseline_df)
                return pd.to_datetime(baseline_df['Date']).max()
            return pd.to_datetime('2026-06-01')
            
        return pd.to_datetime(logs['date']).max()

    def run_monthly_update(self, target_dataset="stefanoleone992/fifa-22-complete-player-dataset"):
        last_update_date = self.check_for_delta()
        next_update_date = last_update_date + pd.DateOffset(months=1)
        
        print(f"Last database update was: {last_update_date.strftime('%Y-%m-%d')}")
        print(f"Preparing update for: {next_update_date.strftime('%Y-%m-%d')}")
        
        # 1. Attempt Kaggle Download
        raw_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'kaggle')
        success = self.downloader.download_dataset(target_dataset, raw_dir)
        
        if success:
            print("Successfully downloaded latest Kaggle dataset. Parsing data...")
            # Here we would parse the real kaggle csv and map it.
            # (Simplified for demonstration to extract delta)
        else:
            print("\n[WARNING] Kaggle download skipped/failed (likely due to dataset terms acceptance).")
            print("Falling back to generating realistic monthly delta update dynamically to keep simulation alive...")
            
        # 2. Generate Delta logs for this month
        # We query the database to see which players exist
        logs = self.db.fetch_all_logs()
        unique_players = logs[['player_id', 'name', 'nationality', 'position', 'tier']].drop_duplicates().to_dict('records')
        
        delta_records = []
        np.random.seed(int(next_update_date.timestamp()) % 100000)
        
        for player in unique_players:
            # Simulate 2 matches for each player for this new month
            for match_id in range(2):
                match_date = next_update_date - pd.DateOffset(days=np.random.randint(1, 28))
                
                pos = player['position']
                tier = player['tier']
                stat_mult = 1.2 if tier == 'Tier_1' else (1.0 if tier == 'Tier_2' else 0.8)
                
                log = {
                    'Player_ID': player['player_id'],
                    'Name': player['name'],
                    'Nationality': player['nationality'],
                    'Position': pos,
                    'Date': match_date.strftime('%Y-%m-%d'),
                    'Tier': tier,
                    'Minutes': np.random.randint(60, 90),
                    
                    'npxG_90': np.clip(np.random.normal((0.25 if pos in ['FW', 'AM'] else 0.05) * stat_mult, 0.1), 0, 1.5),
                    'xA_90': np.clip(np.random.normal((0.20 if pos in ['AM', 'CM', 'FB'] else 0.05) * stat_mult, 0.1), 0, 1.0),
                    'SCA_90': np.clip(np.random.normal((3.5 if pos in ['AM', 'FW'] else 1.0) * stat_mult, 1.0), 0, 8.0),
                    
                    'Tackles_90': np.clip(np.random.normal((3.0 if pos in ['DM', 'FB', 'CB'] else 0.5) * stat_mult, 0.8), 0, 6.0),
                    'Interceptions_90': np.clip(np.random.normal((2.0 if pos in ['DM', 'CB'] else 0.3) * stat_mult, 0.5), 0, 5.0),
                    'AerialWon_pct': np.clip(np.random.normal((0.65 if pos == 'CB' else 0.4) * stat_mult, 0.1), 0, 1.0),
                    'PSxG_GA_90': np.clip(np.random.normal(0.05 * stat_mult, 0.2), -1.0, 1.5) if pos == 'GK' else 0.0
                }
                delta_records.append(log)
                
        delta_df = pd.DataFrame(delta_records)
        self.db.insert_match_logs(delta_df)
        print(f"Successfully added {len(delta_df)} new match logs for date {next_update_date.strftime('%Y-%m-%d')} to local SQLite database.")

if __name__ == "__main__":
    updater = MonthlyUpdater()
    updater.run_monthly_update()
