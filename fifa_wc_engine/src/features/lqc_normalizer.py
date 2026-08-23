import pandas as pd

class LQCNormalizer:
    def __init__(self):
        """
        Baseline Calibration for League Quality Coefficient (LQC):
          - Tier 1: 1.00
          - Tier 2: 0.88
          - Tier 3: 0.70
          - Tier 4: 0.55
          - Tier 5: 0.40
        """
        self.tier_weights = {
            'Tier_1': 1.00,
            'Tier_2': 0.88,
            'Tier_3': 0.70,
            'Tier_4': 0.55,
            'Tier_5': 0.40
        }
        
    def apply_lqc(self, df, tier_col='Tier'):
        """
        Maps the tier of each match to its respective LQC multiplier.
        """
        df = df.copy()
        df['LQC_Multiplier'] = df[tier_col].map(self.tier_weights).fillna(0.40)
        
        # Calculate the final combined match weight (Time_Weight * LQC)
        if 'Time_Weight' in df.columns:
            df['Final_Match_Weight'] = df['Time_Weight'] * df['LQC_Multiplier']
        else:
            df['Final_Match_Weight'] = df['LQC_Multiplier']
            
        return df

if __name__ == "__main__":
    df = pd.DataFrame({'Tier': ['Tier_1', 'Tier_3', 'Tier_5', 'Unknown']})
    lqc = LQCNormalizer()
    print("LQC Mapping:")
    print(lqc.apply_lqc(df))
