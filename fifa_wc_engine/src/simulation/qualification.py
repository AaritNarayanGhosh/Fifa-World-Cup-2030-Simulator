import pandas as pd
import numpy as np
import os

class QualificationProjector:
    def __init__(self, nation_data_path=None):
        """
        Hardcoded 48-team field based on historical qualification and current Elo.
        """
        self.nations = [
            # UEFA (16)
            {"Nation": "Spain", "Confederation": "UEFA", "Method": "Host"},
            {"Nation": "Portugal", "Confederation": "UEFA", "Method": "Host"},
            {"Nation": "France", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "England", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Belgium", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Netherlands", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Italy", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Germany", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Croatia", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Switzerland", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Denmark", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Serbia", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Poland", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Scotland", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Austria", "Confederation": "UEFA", "Method": "Direct"},
            {"Nation": "Ukraine", "Confederation": "UEFA", "Method": "Direct"},
            
            # CONMEBOL (6)
            {"Nation": "Argentina", "Confederation": "CONMEBOL", "Method": "Host"},
            {"Nation": "Uruguay", "Confederation": "CONMEBOL", "Method": "Host"},
            {"Nation": "Paraguay", "Confederation": "CONMEBOL", "Method": "Host"},
            {"Nation": "Brazil", "Confederation": "CONMEBOL", "Method": "Direct"},
            {"Nation": "Colombia", "Confederation": "CONMEBOL", "Method": "Direct"},
            {"Nation": "Ecuador", "Confederation": "CONMEBOL", "Method": "Direct"},
            
            # CAF (9)
            {"Nation": "Morocco", "Confederation": "CAF", "Method": "Host"},
            {"Nation": "Senegal", "Confederation": "CAF", "Method": "Direct"},
            {"Nation": "Egypt", "Confederation": "CAF", "Method": "Direct"},
            {"Nation": "Nigeria", "Confederation": "CAF", "Method": "Direct"},
            {"Nation": "Algeria", "Confederation": "CAF", "Method": "Direct"},
            {"Nation": "Ivory Coast", "Confederation": "CAF", "Method": "Direct"},
            {"Nation": "Tunisia", "Confederation": "CAF", "Method": "Direct"},
            {"Nation": "Cameroon", "Confederation": "CAF", "Method": "Direct"},
            {"Nation": "Mali", "Confederation": "CAF", "Method": "Direct"},
            
            # AFC (8)
            {"Nation": "Japan", "Confederation": "AFC", "Method": "Direct"},
            {"Nation": "Iran", "Confederation": "AFC", "Method": "Direct"},
            {"Nation": "South Korea", "Confederation": "AFC", "Method": "Direct"},
            {"Nation": "Australia", "Confederation": "AFC", "Method": "Direct"},
            {"Nation": "Saudi Arabia", "Confederation": "AFC", "Method": "Direct"},
            {"Nation": "Qatar", "Confederation": "AFC", "Method": "Direct"},
            {"Nation": "Iraq", "Confederation": "AFC", "Method": "Direct"},
            {"Nation": "UAE", "Confederation": "AFC", "Method": "Direct"},
            
            # CONCACAF (6)
            {"Nation": "USA", "Confederation": "CONCACAF", "Method": "Direct"},
            {"Nation": "Mexico", "Confederation": "CONCACAF", "Method": "Direct"},
            {"Nation": "Canada", "Confederation": "CONCACAF", "Method": "Direct"},
            {"Nation": "Panama", "Confederation": "CONCACAF", "Method": "Direct"},
            {"Nation": "Costa Rica", "Confederation": "CONCACAF", "Method": "Direct"},
            {"Nation": "Jamaica", "Confederation": "CONCACAF", "Method": "Direct"},
            
            # OFC (1)
            {"Nation": "New Zealand", "Confederation": "OFC", "Method": "Direct"},
            
            # Playoff (2)
            {"Nation": "Sweden", "Confederation": "UEFA", "Method": "Playoff"},
            {"Nation": "Peru", "Confederation": "CONMEBOL", "Method": "Playoff"},
        ]

    def project_field(self):
        # We no longer calculate dynamic pools, just return the predefined dataframe.
        return pd.DataFrame(self.nations)

if __name__ == "__main__":
    projector = QualificationProjector()
    field = projector.project_field()
    print("Projected 48-Team Field for 2030 FIFA World Cup (Hardcoded)")
    print(field['Confederation'].value_counts())
    
    out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
    os.makedirs(out_dir, exist_ok=True)
    field.to_csv(os.path.join(out_dir, 'projected_48_teams.csv'), index=False)
    print("Saved to data/processed/projected_48_teams.csv")
