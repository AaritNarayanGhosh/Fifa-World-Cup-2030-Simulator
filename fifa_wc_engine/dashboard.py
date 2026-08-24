import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="FIFA WC 2030 Simulation", page_icon="🏆", layout="wide")

# Paths
BASE_DIR = os.path.dirname(__file__)
RESULTS_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'monte_carlo_results.csv')
DB_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'fifa_simulation.db')
SQUADS_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'aggregated_player_ratings.csv')
GROUPS_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'group_stage_draw.csv')

def get_flag_url(nation):
    # A mapping of some common nations to their ISO 2-letter codes for flagcdn
    codes = {
        'Spain': 'es', 'Portugal': 'pt', 'France': 'fr', 'England': 'gb-eng', 'Belgium': 'be',
        'Netherlands': 'nl', 'Italy': 'it', 'Germany': 'de', 'Croatia': 'hr', 'Switzerland': 'ch',
        'Denmark': 'dk', 'Serbia': 'rs', 'Poland': 'pl', 'Scotland': 'gb-sct', 'Austria': 'at',
        'Ukraine': 'ua', 'Argentina': 'ar', 'Uruguay': 'uy', 'Paraguay': 'py', 'Brazil': 'br',
        'Colombia': 'co', 'Ecuador': 'ec', 'Morocco': 'ma', 'Senegal': 'sn', 'Egypt': 'eg',
        'Nigeria': 'ng', 'Algeria': 'dz', 'Ivory Coast': 'ci', 'Tunisia': 'tn', 'Cameroon': 'cm',
        'Mali': 'ml', 'Japan': 'jp', 'Iran': 'ir', 'South Korea': 'kr', 'Australia': 'au',
        'Saudi Arabia': 'sa', 'Qatar': 'qa', 'Iraq': 'iq', 'UAE': 'ae', 'USA': 'us',
        'Mexico': 'mx', 'Canada': 'ca', 'Panama': 'pa', 'Costa Rica': 'cr', 'Jamaica': 'jm',
        'New Zealand': 'nz', 'Sweden': 'se', 'Peru': 'pe'
    }
    code = codes.get(nation, 'un')
    return f"https://flagcdn.com/w40/{code}.png"

@st.cache_data
def load_data():
    results = pd.read_csv(RESULTS_PATH) if os.path.exists(RESULTS_PATH) else None
    squads = pd.read_csv(SQUADS_PATH) if os.path.exists(SQUADS_PATH) else None
    groups = pd.read_csv(GROUPS_PATH) if os.path.exists(GROUPS_PATH) else None
    return results, squads, groups

results_df, squads_df, groups_df = load_data()

st.title("FIFA World Cup 2030 AI Simulator")

import sys
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'src'))

from src.simulation.draw_generator import DrawGenerator
from src.simulation.monte_carlo_engine import VectorizedMonteCarloEngine

def run_simulation_in_process(num_simulations):
    # Paths
    teams_path = os.path.join(BASE_DIR, 'data', 'processed', 'nation_strength_matrix.csv')
    draw_path = os.path.join(BASE_DIR, 'data', 'processed', 'group_stage_draw.csv')
    output_path = os.path.join(BASE_DIR, 'data', 'processed', 'monte_carlo_results.csv')
    
    engine = VectorizedMonteCarloEngine(num_simulations=num_simulations)
    engine.load_data(teams_path, draw_path)
    results = engine.run_tournaments()
    
    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    results.to_csv(output_path, index=False)

def redraw_groups_in_process():
    input_path = os.path.join(BASE_DIR, 'data', 'processed', 'projected_48_teams.csv')
    output_path = os.path.join(BASE_DIR, 'data', 'processed', 'group_stage_draw.csv')
    
    generator = DrawGenerator(input_path)
    generator.save_draw(output_path)

# Sidebar - Live Tuner
with st.sidebar:
    st.header("⚙️ Simulation Tuner")
    st.markdown("Adjust parameters and re-run live.")
    
    sims = st.slider("Number of Simulations", 1000, 50000, 25000, step=1000)
    
    if st.button("Run Simulation Now"):
        with st.spinner(f"Running {sims} tournaments..."):
            try:
                run_simulation_in_process(sims)
                st.success(f"Completed {sims} simulations!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error running simulation: {e}")
                
    st.divider()
    st.header("🔀 FIFA Sandbox Mode")
    st.markdown("Since the official 2030 draw hasn't happened yet, generate an entirely new group draw!")
    
    if st.button("Redraw Groups & Simulate"):
        with st.spinner("Redrawing groups and running simulations..."):
            try:
                redraw_groups_in_process()
                run_simulation_in_process(sims)
                st.success("New groups drawn and simulated!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error redrawing groups: {e}")

if results_df is None:
    st.error("Results file not found. Please run the simulation first.")
else:
    # Top Section - Winner Odds
    st.subheader("Tournament Champions (Top 10 Odds)")
    top_10 = results_df.head(10).reset_index(drop=True)
    
    # Native Streamlit rendering for Top 10 (2 rows of 5)
    row1 = st.columns(5)
    for idx in range(5):
        if idx < len(top_10):
            row = top_10.iloc[idx]
            flag = get_flag_url(row['Nation'])
            with row1[idx]:
                st.markdown(f"""
                <div style='background-color:#1e1e1e; padding:15px; border-radius:10px; text-align:center; border: 1px solid #333; margin-bottom:15px;'>
                    <img src='{flag}' width='40' style='border-radius:4px; margin-bottom:10px;'><br>
                    <strong style='font-size:16px;'>{row['Nation']}</strong><br>
                    <span style='color:gold; font-size:22px; font-weight:bold;'>{row['Win_%']:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
                
    row2 = st.columns(5)
    for idx in range(5, 10):
        if idx < len(top_10):
            row = top_10.iloc[idx]
            flag = get_flag_url(row['Nation'])
            with row2[idx-5]:
                st.markdown(f"""
                <div style='background-color:#1e1e1e; padding:15px; border-radius:10px; text-align:center; border: 1px solid #333; margin-bottom:15px;'>
                    <img src='{flag}' width='40' style='border-radius:4px; margin-bottom:10px;'><br>
                    <strong style='font-size:16px;'>{row['Nation']}</strong><br>
                    <span style='color:gold; font-size:22px; font-weight:bold;'>{row['Win_%']:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()

    # Tabs for deep dives
    tab1, tab2 = st.tabs(["📊 Full Probabilities", "📅 Group Stage Visualizer"])
    
    with tab1:
        st.dataframe(
            results_df.style.format({
                'Win_%': '{:.2f}%', 'Final_%': '{:.2f}%', 'SF_%': '{:.2f}%',
                'QF_%': '{:.2f}%', 'R16_%': '{:.2f}%', 'R32_%': '{:.2f}%'
            }).background_gradient(cmap='Greens', subset=['Win_%']),
            height=600, use_container_width=True
        )
            
    with tab2:
        if groups_df is not None:
            # Render groups as cards
            st.markdown("### Official 2030 Group Stage Draw")
            group_letters = sorted(groups_df['Group'].unique())
            cols = st.columns(4)
            for i, grp in enumerate(group_letters):
                grp_data = groups_df[groups_df['Group'] == grp]
                with cols[i % 4]:
                    st.markdown(f"**{grp}**")
                    for _, row in grp_data.iterrows():
                        flag = get_flag_url(row['Nation'])
                        st.markdown(f"<img src='{flag}' width='20' style='margin-right:8px; border-radius:2px;'> {row['Nation']}", unsafe_allow_html=True)
                    st.write("")
