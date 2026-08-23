import pandas as pd
import numpy as np
import os

def generate_real_nations():
    # Approximate top nations per confederation with base Elo ratings
    # (Higher Elo = Better team)
    nations_data = [
        # UEFA (Europe)
        ("France", "UEFA", 2100), ("England", "UEFA", 2050), ("Belgium", "UEFA", 2000),
        ("Netherlands", "UEFA", 1980), ("Italy", "UEFA", 1950), ("Germany", "UEFA", 1940),
        ("Croatia", "UEFA", 1930), ("Switzerland", "UEFA", 1900), ("Denmark", "UEFA", 1880),
        ("Serbia", "UEFA", 1850), ("Poland", "UEFA", 1830), ("Scotland", "UEFA", 1800),
        ("Hungary", "UEFA", 1790), ("Austria", "UEFA", 1780), ("Sweden", "UEFA", 1770),
        ("Ukraine", "UEFA", 1760), ("Wales", "UEFA", 1750), ("Turkey", "UEFA", 1740),
        ("Czech Republic", "UEFA", 1730), ("Norway", "UEFA", 1720), ("Romania", "UEFA", 1700),
        ("Slovakia", "UEFA", 1690), ("Greece", "UEFA", 1680), ("Slovenia", "UEFA", 1670),
        ("Republic of Ireland", "UEFA", 1650), ("Finland", "UEFA", 1630), ("Bosnia", "UEFA", 1620),
        
        # CONMEBOL (South America)
        ("Brazil", "CONMEBOL", 2100), ("Colombia", "CONMEBOL", 1950),
        ("Ecuador", "CONMEBOL", 1850), ("Peru", "CONMEBOL", 1800),
        ("Chile", "CONMEBOL", 1780), ("Venezuela", "CONMEBOL", 1750),
        ("Bolivia", "CONMEBOL", 1650),
        
        # CAF (Africa)
        ("Senegal", "CAF", 1850), ("Egypt", "CAF", 1820), ("Nigeria", "CAF", 1800),
        ("Algeria", "CAF", 1790), ("Ivory Coast", "CAF", 1780), ("Tunisia", "CAF", 1770),
        ("Cameroon", "CAF", 1750), ("Mali", "CAF", 1740), ("Burkina Faso", "CAF", 1700),
        ("Ghana", "CAF", 1690), ("South Africa", "CAF", 1680), ("DR Congo", "CAF", 1670),
        ("Guinea", "CAF", 1650), ("Zambia", "CAF", 1620), ("Equatorial Guinea", "CAF", 1600),
        
        # AFC (Asia)
        ("Japan", "AFC", 1850), ("Iran", "AFC", 1820), ("South Korea", "AFC", 1800),
        ("Australia", "AFC", 1780), ("Saudi Arabia", "AFC", 1750), ("Qatar", "AFC", 1720),
        ("Iraq", "AFC", 1680), ("UAE", "AFC", 1650), ("Uzbekistan", "AFC", 1640),
        ("Oman", "AFC", 1620), ("China", "AFC", 1580), ("Syria", "AFC", 1550),
        
        # CONCACAF (North/Central America)
        ("USA", "CONCACAF", 1850), ("Mexico", "CONCACAF", 1820), ("Canada", "CONCACAF", 1780),
        ("Panama", "CONCACAF", 1720), ("Costa Rica", "CONCACAF", 1700), ("Jamaica", "CONCACAF", 1680),
        ("Honduras", "CONCACAF", 1620), ("El Salvador", "CONCACAF", 1580), ("Haiti", "CONCACAF", 1550),
        
        # OFC (Oceania)
        ("New Zealand", "OFC", 1600), ("Solomon Islands", "OFC", 1400),
        ("Fiji", "OFC", 1350), ("Tahiti", "OFC", 1300)
    ]
    
    # Add random variations to qualification rates and recent form to make it dynamic
    np.random.seed(42)
    records = []
    
    for nation, confed, elo in nations_data:
        # Better teams have higher baseline Q_rate and Recent_Form
        q_rate_baseline = min(1.0, (elo - 1300) / 700)
        form_baseline = min(1.0, (elo - 1300) / 700)
        
        records.append({
            'Nation': nation,
            'Confederation': confed,
            'Elo': elo + np.random.randint(-50, 50),
            'Q_rate': np.clip(np.random.normal(q_rate_baseline, 0.15), 0, 1),
            'Recent_Form': np.clip(np.random.normal(form_baseline, 0.15), 0, 1)
        })
        
    df = pd.DataFrame(records)
    
    # Normalize Elo per confederation
    df['Elo_norm'] = df.groupby('Confederation')['Elo'].transform(lambda x: (x - x.min()) / (x.max() - x.min() + 1e-5))
    
    out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'real_nations_db.csv')
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} real nations to {out_path}")

if __name__ == "__main__":
    generate_real_nations()
