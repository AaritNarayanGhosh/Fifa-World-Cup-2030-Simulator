import pandas as pd
import numpy as np
import os
import random

class DrawGenerator:
    def __init__(self, qualified_teams_path):
        if not os.path.exists(qualified_teams_path):
            raise FileNotFoundError(f"Could not find {qualified_teams_path}. Run qualification.py first.")
        self.teams_df = pd.read_csv(qualified_teams_path)
        
    def _assign_pots(self):
        """
        Assigns the 48 teams into 4 pots of 12 teams each.
        In reality, pots are determined by FIFA World Ranking.
        Here we will sort by a mock 'Seeding_Score' (randomized for now, 
        but prioritizing Hosts to Pot 1).
        """
        # Assign mock seeding score if we don't have Elo
        if 'Elo' not in self.teams_df.columns:
            self.teams_df['Seeding_Score'] = np.random.uniform(1000, 2000, size=len(self.teams_df))
            
        # Give hosts an artificial boost to ensure they are in Pot 1
        self.teams_df.loc[self.teams_df['Method'] == 'Host', 'Seeding_Score'] = 3000
        
        # Sort teams
        sorted_teams = self.teams_df.sort_values(by='Seeding_Score', ascending=False).reset_index(drop=True)
        
        # Assign pots
        pots = {
            1: sorted_teams.iloc[0:12].to_dict('records'),
            2: sorted_teams.iloc[12:24].to_dict('records'),
            3: sorted_teams.iloc[24:36].to_dict('records'),
            4: sorted_teams.iloc[36:48].to_dict('records')
        }
        return pots
        
    def generate_draw(self):
        """
        Generates 12 groups of 4 teams.
        Simplified draw without strict confederation constraints for Sprint 1.
        """
        pots = self._assign_pots()
        
        # Shuffle pots
        for p in pots:
            random.shuffle(pots[p])
            
        groups = {f"Group {chr(65+i)}": [] for i in range(12)} # Group A to Group L
        group_names = list(groups.keys())
        
        for pot_num in range(1, 5):
            for i, group_name in enumerate(group_names):
                team = pots[pot_num][i]
                groups[group_name].append({
                    'Nation': team['Nation'],
                    'Confederation': team['Confederation'],
                    'Pot': pot_num
                })
                
        return groups
        
    def save_draw(self, output_path):
        groups = self.generate_draw()
        
        # Flatten for DataFrame
        flat_data = []
        for group_name, teams in groups.items():
            for team in teams:
                flat_data.append({
                    'Group': group_name,
                    'Nation': team['Nation'],
                    'Confederation': team['Confederation'],
                    'Pot': team['Pot']
                })
                
        df = pd.DataFrame(flat_data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        return groups

if __name__ == "__main__":
    input_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'projected_48_teams.csv')
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'group_stage_draw.csv')
    
    generator = DrawGenerator(input_path)
    groups = generator.save_draw(output_path)
    
    print("==================================================")
    print("2030 FIFA World Cup - Group Stage Draw")
    print("==================================================")
    for group_name, teams in groups.items():
        print(f"\n{group_name}:")
        for team in teams:
            print(f"  - {team['Nation']} (Pot {team['Pot']}, {team['Confederation']})")
    print(f"\nSaved draw to {output_path}")
