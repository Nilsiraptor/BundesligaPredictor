import os

import pandas as pd
from tqdm import tqdm

data_frames = []

files = [[(folder, file) for file in os.listdir(os.path.join("data", folder)) if os.path.isfile(os.path.join("data", folder, file))] for folder in os.listdir("data") if os.path.isdir(os.path.join("data", folder))]

files = sum(files, [])

for folder, file in tqdm(files):
    df = pd.read_csv(os.path.join("data", folder, file))

    columns = list(df.columns)

    df["Saison"] = folder.split("_")[1]

    if folder.split("_")[0].endswith("2"):
        league = "2. Bundesliga"
    else:
        league = "1. Bundesliga"

    df["Liga"] = league

    df["Spieltag"] = int(file.split("_")[1][:2])

    new_order = ["Liga", "Saison", "Spieltag"] + columns
    df = df[new_order]

    data_frames.append(df)

df = pd.concat(data_frames)

mask = ~df["Ergebnis"].str.contains("-")
df = df[mask]

df.to_csv("data/combined.csv", index=False)

print(df.head())
print(df.tail())

print(df.shape)
