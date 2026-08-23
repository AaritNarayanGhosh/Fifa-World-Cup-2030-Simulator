import sqlite3
import os
import pandas as pd

class DBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'fifa_simulation.db')
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.setup_tables()
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def setup_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Nations Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS nations (
                nation TEXT PRIMARY KEY,
                confederation TEXT,
                method TEXT
            )
            """)
            
            # 2. Match Logs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS match_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                name TEXT,
                nationality TEXT,
                position TEXT,
                date TEXT,
                tier TEXT,
                minutes INTEGER,
                npxg_90 REAL,
                xa_90 REAL,
                sca_90 REAL,
                tackles_90 REAL,
                interceptions_90 REAL,
                aerial_won_pct REAL,
                psxg_ga_90 REAL
            )
            """)
            conn.commit()

    def seed_nations(self, projected_nations_df):
        with self.get_connection() as conn:
            projected_nations_df.to_sql('nations', conn, if_exists='replace', index=False)
            
    def insert_match_logs(self, df):
        """
        Inserts new match logs into the database.
        """
        df_db = df.copy()
        # Normalize original column names to lowercase
        df_db.columns = [c.lower() for c in df_db.columns]
        
        # Explicit mapping
        column_mapping = {
            'player_id': 'player_id',
            'name': 'name',
            'nationality': 'nationality',
            'position': 'position',
            'date': 'date',
            'tier': 'tier',
            'minutes': 'minutes',
            'npxg_90': 'npxg_90',
            'xa_90': 'xa_90',
            'sca_90': 'sca_90',
            'tackles_90': 'tackles_90',
            'interceptions_90': 'interceptions_90',
            'aerialwon_pct': 'aerial_won_pct',
            'psxg_ga_90': 'psxg_ga_90'
        }
        
        # Filter and rename
        df_db = df_db[[col for col in column_mapping.keys() if col in df_db.columns]]
        df_db = df_db.rename(columns=column_mapping)
        
        with self.get_connection() as conn:
            df_db.to_sql('match_logs', conn, if_exists='append', index=False)

    def fetch_all_logs(self):
        with self.get_connection() as conn:
            return pd.read_sql("SELECT * FROM match_logs", conn)

if __name__ == "__main__":
    db = DBManager()
    print(f"SQLite Database initialized at {db.db_path}")
