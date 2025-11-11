import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


def recherche_films_offi(texte_recherche: str):
    """
    Recherche des films sur le site de l'Officiel des Spectacles.

    Args:
        texte_recherche (str): texte saisi par l'utilisateur (ex: "l'étranger")

    Returns:
        list[tuple[str, str]]: liste de tuples (titre_du_film, id_du_film)
    """
    # Encoder correctement la recherche pour l’URL
    query = quote(texte_recherche)
    url = f"https://www.offi.fr/recherche-ac.html?acSearch={query}"

    # Récupération du HTML
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    films_section = None

    # Trouver le bloc de la section "Films"
    for bloc in soup.find_all("div", class_="single-event-page"):
        h2 = bloc.find("h2")
        if h2 and "Films" in h2.text:
            films_section = bloc
            break

    if not films_section:
        return []

    # Extraire tous les liens de la section "Films"
    results = []
    for a in films_section.find_all("a", href=True):
        href = a["href"]
        titre = a.get_text(strip=True)
        # On cherche les URLs du type /recherche-XXXXXX.html
        if href.startswith("/recherche-") and href.endswith(".html"):
            # Récupérer l'identifiant numérique
            film_id = href.split("-")[1].split(".")[0]
            results.append((titre, film_id))

    return results
