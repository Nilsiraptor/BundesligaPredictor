from classes import Team, defaultdict

import pandas as pd
from tqdm import tqdm

# Load dataset
df = pd.read_csv("data/combined.csv")

# Prepare dataset
df["Heimtore"] = df["Ergebnis"].str.split(":").str[0].astype(int)
df["Gasttore"] = df["Ergebnis"].str.split(":").str[1].astype(int)

l_home = df["Heimtore"].mean()
l_away = df["Gasttore"].mean()

l_historic = l_home, l_away

# Sort dataset by date
df["Datum"] = pd.to_datetime(df["Datum"].str.split().str[1], dayfirst=True, format="mixed")
df = df.sort_values(by=["Datum", "Uhrzeit"])

# Create list of teams
teams = defaultdict(Team)

# Go through all matches
for index, row in tqdm(df.iterrows(), total=len(df)):
    home_name = row["Heim"]
    away_name = row["Gast"]

    home_team = teams[home_name]
    away_team = teams[away_name]

    result = row["Heimtore"], row["Gasttore"]

    home_team.update(away_team, result)

team_list = [team for team in teams.values()]

team_list.sort(key=lambda x: x.score, reverse=True)

df = pd.DataFrame(team_list)

df.to_csv("model.csv", index=False)
