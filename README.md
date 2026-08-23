# FIFA World Cup 2030 AI Simulator

An interactive machine learning and statistical simulation engine predicting the outcome of the 2030 FIFA World Cup. The model uses a Dixon-Coles Bivariate Poisson engine alongside dynamic player metrics aggregated from rolling club and country match logs.

🏆 **Live Demo:** [Deploy your Streamlit Cloud Link Here!]

## Key Features
* **Dixon-Coles Match Engine:** Custom-built Poisson model capturing low-scoring draws and clean sheet probability.
* **Vectorized Monte Carlo:** Runs 25,000 full tournament simulations in under 0.6 seconds using pure 3D NumPy array indexing.
* **Dynamic SQLite Database:** Automatically aggregates 5 years of historical match logs to calculate attacking and defensive parameters per country.
* **FIFA Sandbox Mode:** Interactively redraw groups and seedings based on official pots and re-simulate the entire tournament instantly.
* **Automated Monthly Ingestion:** GitHub Actions automatically wakes up on the 1st of every month, downloads new player logs from Kaggle, updates the local database, and updates the tournament odds.

## Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/fifa-wc-2030-simulator.git
   cd fifa-wc-2030-simulator
   ```

2. Install dependencies:
   ```bash
   pip install -r fifa_wc_engine/requirements.txt
   ```

3. Run the dashboard locally:
   ```bash
   streamlit run fifa_wc_engine/dashboard.py
   ```
