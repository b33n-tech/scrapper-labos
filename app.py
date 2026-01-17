import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep

st.set_page_config(page_title="Scraper membres LARHRA", layout="wide")

st.title("Scraper des membres LARHRA")
st.write("Scrape les profils de https://larhra.fr/membres/page/1 à /page/29")

BASE_URL = "https://larhra.fr/membres/page/{}"

@st.cache_data(show_spinner=False)
def scrape_members(max_pages=29):
    results = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for page in range(1, max_pages + 1):
        url = BASE_URL.format(page)
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        cards = soup.select("a.card-member")
        for card in cards:
            profile_url = card.get("href")

            img = card.select_one("img.object-cover")
            img_url = img.get("src") if img else None

            texts = card.select("p.text--min")
            name = texts[0].get_text(strip=True) if len(texts) > 0 else None
            role = texts[1].get_text(strip=True) if len(texts) > 1 else None

            results.append({
                "nom": name,
                "role": role,
                "profil_url": profile_url,
                "photo_url": img_url
            })

        sleep(0.3)  # politesse serveur

    return pd.DataFrame(results)

if st.button("Lancer le scraping"):
    with st.spinner("Scraping en cours…"):
        df = scrape_members()

    st.success(f"{len(df)} profils récupérés")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Télécharger en CSV",
        csv,
        "larhra_membres.csv",
        "text/csv"
    )
