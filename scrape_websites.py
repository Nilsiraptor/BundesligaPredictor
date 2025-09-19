import os
import io
import json
import time

from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

for file_name in tqdm(os.listdir("websites")):

    if not os.path.isfile(os.path.join("websites", file_name)):
        continue

    with open("./websites/" + file_name, "r", encoding="utf-8") as file:
        text = file.read()

    site = BeautifulSoup(text, "html.parser")

    tables = site.find_all("table")

    i = 1

    for table in tables:

        os.makedirs(f"data/{file_name.rsplit(".", 1)[0]}", exist_ok=True)

        text = table.find_parent().find_all()[0].text

        if text.endswith("Spieltag"):
            table_str = io.StringIO(str(table))
            df = pd.read_html(table_str)[0]

            df = df.drop(["Heimmannschaft.1", "Heim.1", "Gastmannschaft", "Gastmannschaft.1", "Gast", "Gast.1"], axis=1)

            df = df.rename(columns={"Heimmannschaft": "Heim", "Heim": "Ergebnis", "Ergebnis": "Gast"})

            mask = (df["Uhrzeit"] != df["Ergebnis"])
            df = df[mask]

            df = df.ffill()

            df = df.reset_index(drop=True)

            df["Heim"] = df["Heim"].str.replace(r"\s?\(.*\)\s?", "", regex=True)
            df["Gast"] = df["Gast"].str.replace(r"\s?\(.*\)\s?", "", regex=True)

            df.to_csv(f"data/{file_name.rsplit(".", 1)[0]}/Spieltag_{i:02}.csv", index=False)
            i += 1
