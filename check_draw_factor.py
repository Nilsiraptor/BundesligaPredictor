import pandas as pd
import numpy as np
from scipy.special import factorial
import matplotlib.pyplot as plt
from tqdm import tqdm
from classes import Team

# --- Configuration ---
TRAIN_UP_TO = "2023-07-01"
DRAW_FACTORS = [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.6, 1.7, 1.8, 2.0]
DRAW_FACTORS, dx = list(np.linspace(1.0, 1.5, 10001, True, True))

# --- Helper Functions ---

def poisson(k, l):
    """Calculates Poisson probability."""
    return l**k / factorial(k, exact=True) * np.exp(-l)

def calculate_actual_points(pred_h, pred_a, actual_h, actual_a):
    """Calculates points received for a tip against the actual result."""
    if pred_h == actual_h and pred_a == actual_a:
        return 4
    elif (pred_h - pred_a) == (actual_h - actual_a):
        return 3
    elif (pred_h > pred_a and actual_h > actual_a) or (pred_h < pred_a and actual_h < actual_a):
        return 2
    else:
        return 0

def get_points_matrix(pred_h, pred_a, max_goals=6):
    """Creates a matrix of points for a given prediction against all possible outcomes."""
    M = np.zeros((max_goals+1, max_goals+1))
    for h in range(max_goals+1):
        for a in range(max_goals+1):
            M[h, a] = calculate_actual_points(pred_h, pred_a, h, a)
    return M

def run_optimization():
    # 1. Load and Prepare Data
    print("Loading data...")
    df = pd.read_csv("data/combined.csv")

    # Parse dates
    df["Datum_Clean"] = df["Datum"].str.split().str[1]
    df["Datum_dt"] = pd.to_datetime(df["Datum_Clean"], dayfirst=True, format="mixed")

    # Parse results
    df["Heimtore"] = df["Ergebnis"].str.split(":").str[0].astype(int)
    df["Gasttore"] = df["Ergebnis"].str.split(":").str[1].astype(int)

    # Sort by date
    df = df.sort_values(by=["Datum_dt", "Uhrzeit"])

    # Split Data
    train_mask = df["Datum_dt"] < TRAIN_UP_TO
    train_df = df[train_mask]
    test_df = df[~train_mask]

    print(f"Training set: {len(train_df)} matches | Test set: {len(test_df)} matches")

    # 2. Train Model (Use ALL matches to track team strengths)
    print("Training model...")
    teams = {}

    def get_team(name):
        if name not in teams:
            teams[name] = Team(name)
        return teams[name]

    for _, row in train_df.iterrows():
        h_team = get_team(row["Heim"])
        a_team = get_team(row["Gast"])
        result = (row["Heimtore"], row["Gasttore"])
        h_team.update(a_team, result)

    # 3. Test and Optimize
    print(f"Testing factors: {DRAW_FACTORS}")

    # Precompute points matrices
    TIP_RANGE = 5
    CALC_RANGE = 7
    points_matrices = {}
    for i in range(TIP_RANGE):
        for j in range(TIP_RANGE):
            points_matrices[(i,j)] = get_points_matrix(i, j, max_goals=CALC_RANGE)

    total_points = {f: 0 for f in DRAW_FACTORS}
    matches_counted = 0

    total = len(test_df)
    for idx, row in tqdm(test_df.iterrows(), total=total):
        h_team = get_team(row["Heim"])
        a_team = get_team(row["Gast"])
        actual_result = (row["Heimtore"], row["Gasttore"])

        # Only calculate points if 1. Bundesliga
        is_target_league = (row["Liga"] == "1. Bundesliga")

        if is_target_league:
            matches_counted += 1
            # Calculate match expectations
            exp_h, exp_a = h_team.match(a_team)

            # Calculate probability matrix P
            range_calc = np.arange(CALC_RANGE + 1)
            prob_h = poisson(range_calc, exp_h)
            prob_a = poisson(range_calc, exp_a)
            P_matrix = np.outer(prob_h, prob_a)

            # Calculate Base Expected Points
            base_exp_points = {}
            for tip_h in range(TIP_RANGE):
                for tip_a in range(TIP_RANGE):
                    mat = points_matrices[(tip_h, tip_a)]
                    e_pts = np.sum(P_matrix * mat)
                    base_exp_points[(tip_h, tip_a)] = e_pts

            # Evaluate each draw factor
            for f in DRAW_FACTORS:
                best_tip = None
                max_val = -1.0

                for tip, val in base_exp_points.items():
                    final_val = val
                    if tip[0] == tip[1]:
                        final_val *= f

                    if final_val > max_val:
                        max_val = final_val
                        best_tip = tip

                pts = calculate_actual_points(best_tip[0], best_tip[1], actual_result[0], actual_result[1])
                total_points[f] += pts

        # Update model for ALL matches (to keep team ratings valid)
        h_team.update(a_team, actual_result)

    # 4. Results & Plotting
    print(f"\n--- Results (Based on {matches_counted} matches from 1. Bundesliga) ---")

    x = list(total_points.keys())
    y = list(total_points.values())

    edges = [x[0]] + x
    edges = [e + dx/2 for e in edges]

    best_p = -1
    best_f = None

    for f, p in total_points.items():
        print(f"Factor {f}: {p} points")
        if p > best_p:
            best_p = p
            best_f = f

    print(f"\nOptimal Draw Factor (1. BL): {best_f} (Points: {best_p})")

    # Plot
    plt.figure(figsize=(10, 6))
    # plt.plot(x, y, marker='o', linestyle='-', color='forestgreen', linewidth=2, markersize=8)
    plt.stairs(y, edges, color="forestgreen", linewidth=2, baseline=None)

    # Labels
    plt.title(f'Total Points vs Draw Factor\n(1. Bundesliga Only)', fontsize=14)
    plt.xlabel('Draw Factor', fontsize=12)
    plt.ylabel('Total Points', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Highlight Peak
    plt.annotate(f'Optimal: {best_f} ({best_p} pts)',
                 xy=(best_f, best_p),
                 xytext=(best_f, best_p + (max(y)-min(y))*0.05),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_optimization()
