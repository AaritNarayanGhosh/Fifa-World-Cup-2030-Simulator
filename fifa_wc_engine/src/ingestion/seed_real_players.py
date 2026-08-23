import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def get_nation_tier(nation):
    # Rough estimation of squad quality for generating player stats
    tier1 = ['France', 'Brazil', 'England', 'Argentina', 'Spain', 'Portugal', 'Germany']
    tier2 = ['Italy', 'Netherlands', 'Belgium', 'Uruguay', 'Croatia']
    tier3 = ['Morocco', 'Senegal', 'Japan', 'USA', 'Switzerland', 'Denmark', 'Colombia']
    tier4 = ['Ecuador', 'Mexico', 'South Korea', 'Serbia', 'Poland', 'Ukraine']
    
    if nation in tier1: return 1
    if nation in tier2: return 2
    if nation in tier3: return 3
    if nation in tier4: return 4
    return 5

def generate_real_rosters(nations_df):
    np.random.seed(42)
    positions = ['GK', 'GK', 'GK', 'CB', 'CB', 'CB', 'CB', 'CB', 'FB', 'FB', 'FB', 'FB',
                 'DM', 'DM', 'DM', 'CM', 'CM', 'CM', 'AM', 'AM', 'AM', 
                 'FW', 'FW', 'FW', 'FW', 'FW'] # 26-man roster
                 
    superstars = {
        'France': [('Kylian Mbappé', 'FW'), ('Antoine Griezmann', 'AM')],
        'Argentina': [('Lionel Messi', 'FW'), ('Emiliano Martínez', 'GK')],
        'England': [('Jude Bellingham', 'AM'), ('Harry Kane', 'FW')],
        'Brazil': [('Vinícius Júnior', 'FW'), ('Alisson', 'GK')],
        'Portugal': [('Cristiano Ronaldo', 'FW'), ('Bruno Fernandes', 'AM')],
        'Spain': [('Rodri', 'DM'), ('Lamine Yamal', 'FW')],
        'Norway': [('Erling Haaland', 'FW')]
    }
    
    data = []
    player_id_counter = 0
    start_date = pd.to_datetime('2021-01-01')
    
    for nation in nations_df['Nation']:
        tier = get_nation_tier(nation)
        
        # Determine base stat multiplier (Tier 1 gets highest stats)
        stat_mult = 1.2 if tier == 1 else (1.1 if tier == 2 else (1.0 if tier == 3 else (0.85 if tier == 4 else 0.75)))
        
        # Populate roster
        roster = positions.copy()
        
        # Inject superstars if any
        if nation in superstars:
            for name, pos in superstars[nation]:
                if pos in roster:
                    roster.remove(pos)
                    # Add superstar with heavily boosted stats
                    _create_player_logs(data, player_id_counter, name, pos, nation, stat_mult * 1.5, start_date)
                    player_id_counter += 1
                    
        # Fill rest of roster
        for pos in roster:
            name = f"{nation} Player {player_id_counter}"
            _create_player_logs(data, player_id_counter, name, pos, nation, stat_mult, start_date)
            player_id_counter += 1
            
    df = pd.DataFrame(data)
    return df

def _create_player_logs(data, pid, name, pos, nation, stat_mult, start_date):
    logs_per_player = 40
    # Tier 1 & 2 nations typically play in Tier 1 & 2 leagues
    league_tier = 'Tier_1' if stat_mult >= 1.1 else ('Tier_2' if stat_mult >= 1.0 else 'Tier_3')
    
    dates = [start_date + timedelta(days=np.random.randint(0, 1900)) for _ in range(logs_per_player)]
    
    for date in dates:
        log = {
            'Player_ID': pid,
            'Name': name,
            'Nationality': nation,
            'Position': pos,
            'Date': date,
            'Tier': league_tier,
            'Minutes': np.random.randint(45, 90),
            
            # Attacking
            'npxG_90': np.clip(np.random.normal((0.25 if pos in ['FW', 'AM'] else 0.05) * stat_mult, 0.1), 0, 1.5),
            'xA_90': np.clip(np.random.normal((0.20 if pos in ['AM', 'CM', 'FB'] else 0.05) * stat_mult, 0.1), 0, 1.0),
            'SCA_90': np.clip(np.random.normal((3.5 if pos in ['AM', 'FW'] else 1.0) * stat_mult, 1.0), 0, 8.0),
            
            # Defensive
            'Tackles_90': np.clip(np.random.normal((3.0 if pos in ['DM', 'FB', 'CB'] else 0.5) * stat_mult, 0.8), 0, 6.0),
            'Interceptions_90': np.clip(np.random.normal((2.0 if pos in ['DM', 'CB'] else 0.3) * stat_mult, 0.5), 0, 5.0),
            'AerialWon_pct': np.clip(np.random.normal((0.65 if pos == 'CB' else 0.4) * stat_mult, 0.1), 0, 1.0),
            
            # Goalkeeping
            'PSxG_GA_90': np.clip(np.random.normal(0.05 * stat_mult, 0.2), -1.0, 1.5) if pos == 'GK' else 0.0
        }
        data.append(log)

if __name__ == "__main__":
    teams_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'projected_48_teams.csv')
    if not os.path.exists(teams_path):
        print("Run qualification.py first.")
    else:
        teams_df = pd.read_csv(teams_path)
        print("Generating realistic 26-man rosters based on real nationalities...")
        
        df = generate_real_rosters(teams_df)
        
        out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'synthetic_player_logs.csv') # Overwriting the old synthetic logs
        
        df.to_csv(out_path, index=False)
        print(f"Generated {len(df)} match logs for 1,248 players.")
        print(f"Superstars included: {df[df['Name'] == 'Kylian Mbappé']['Name'].iloc[0]}")
