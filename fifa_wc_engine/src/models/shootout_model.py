import numpy as np

class ShootoutModel:
    def __init__(self):
        """
        Baseline penalty conversion rate is ~75%.
        """
        self.baseline_conversion = 0.75
        
    def simulate_extra_time(self, match_engine, team_a, team_b):
        """
        Simulate 30 minutes (1/3 of a match).
        We simply divide the base lambdas by 3 and simulate.
        """
        lambda_a, lambda_b = match_engine.get_lambdas(team_a, team_b)
        lambda_a_et = lambda_a / 3.0
        lambda_b_et = lambda_b / 3.0
        
        # Simple poisson draw since Dixon-Coles adjustment for ET is negligible
        goals_a = np.random.poisson(lambda_a_et)
        goals_b = np.random.poisson(lambda_b_et)
        
        return goals_a, goals_b

    def simulate_penalties(self, team_a, team_b):
        """
        Simulate a penalty shootout.
        Returns the winner ('A' or 'B') and the score (goals_a, goals_b).
        """
        # In a real model, we would look up specific GK and Penalty taker stats.
        # Here we use a random coin flip slightly biased by overall quality (optional).
        # We will keep it simple: 5 rounds.
        
        goals_a = 0
        goals_b = 0
        rounds = 5
        
        for i in range(rounds):
            if np.random.rand() < self.baseline_conversion: goals_a += 1
            if np.random.rand() < self.baseline_conversion: goals_b += 1
            
            # Check if mathematically impossible to catch up
            rem_a = rounds - i - 1
            rem_b = rounds - i - 1
            if goals_a > goals_b + rem_b: return team_a, goals_a, goals_b
            if goals_b > goals_a + rem_a: return team_b, goals_a, goals_b
            
        # Sudden death
        while goals_a == goals_b:
            if np.random.rand() < self.baseline_conversion: goals_a += 1
            if np.random.rand() < self.baseline_conversion: goals_b += 1
            
        winner = team_a if goals_a > goals_b else team_b
        return winner, goals_a, goals_b

if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(__file__))
    from dixon_coles_poisson import DixonColesMatchEngine
    
    matrix_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'nation_strength_matrix.csv')
    if os.path.exists(matrix_path):
        engine = DixonColesMatchEngine(matrix_path)
        shootout = ShootoutModel()
        
        team1 = "Spain"
        team2 = "Uruguay"
        
        print(f"Simulating Extra Time: {team1} vs {team2}")
        ga, gb = shootout.simulate_extra_time(engine, team1, team2)
        print(f"Extra Time Score: {team1} {ga} - {gb} {team2}")
        
        if ga == gb:
            print("Going to Penalties...")
            winner, pa, pb = shootout.simulate_penalties(team1, team2)
            print(f"Penalty Result: {team1} {pa} - {pb} {team2}")
            print(f"Winner: {winner}")
