import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
from datetime import datetime
import locale # Pour gérer les noms de mois en français


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

def count_sessions_by_date_from_url(url):
    """
    Télécharge le contenu HTML d'une URL, extrait la date de sortie du film
    et compte le nombre de séances de cinéma pour chaque date.

    Args:
        url (str): L'URL de la page web à analyser.

    Returns:
        tuple: Un tuple contenant :
            - str: La date de sortie du film au format 'YYYY-MM-DD' (ou None si non trouvée/parsable).
            - dict: Un dictionnaire où les clés sont des dates au format 'YYYY-MM-DD' et
                    les valeurs sont le nombre de séances pour cette date.
        Retourne (None, {}) en cas d'erreur de téléchargement ou d'analyse majeure.
    """
    sessions_by_date = {}
    release_date_str_formatted = None # Date de sortie au format YYYY-MM-DD

    html_content = ""
    try:
        # 1. Télécharger le contenu HTML de l'URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP 4xx/5xx
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de l'URL {url}: {e}")
        return None, {} # Retourne un tuple (None, {}) en cas d'erreur de connexion ou HTTP

    # 2. Analyser le contenu HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # --- Extraction de la date de sortie ---
    # La date de sortie est dans un paragraphe <p> sous le texte "Date de sortie (ou ressortie) :"
    release_label_tag = soup.find('b', string=re.compile(r'Date de sortie \(ou ressortie\) :'))
    if release_label_tag:
        # La date est le "next_sibling" (le nœud texte suivant directement)
        raw_date_text = release_label_tag.next_sibling
        if raw_date_text:
            raw_date_text = raw_date_text.strip()
            # Tenter de parser la date (ex: "10 septembre 2025") en YYYY-MM-DD
            try:
                # Sauvegarder la locale actuelle
                current_locale = locale.getlocale(locale.LC_TIME)
                # Définir la locale en français pour que strptime comprenne "septembre"
                # La valeur exacte dépend de votre système : 'fr_FR.utf8', 'fr_FR', 'fra', etc.
                try:
                    locale.setlocale(locale.LC_TIME, 'fr_FR.utf8')
                except locale.Error:
                    try:
                        locale.setlocale(locale.LC_TIME, 'fr_FR')
                    except locale.Error:
                        locale.setlocale(locale.LC_TIME, 'fra') # Pour certains systèmes Windows

                parsed_date = datetime.strptime(raw_date_text, "%d %B %Y")
                release_date_str_formatted = parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                print(f"Avertissement : Impossible de parser la date de sortie '{raw_date_text}'.")
                release_date_str_formatted = raw_date_text # Retourner la date brute si le parsing échoue
            finally:
                # Restaurer la locale précédente
                locale.setlocale(locale.LC_TIME, current_locale)
        else:
            print("Avertissement : Le texte de la date de sortie est vide.")
    else:
        print("Avertissement : Balise 'Date de sortie (ou ressortie) :' non trouvée.")

    # --- Extraction des séances par date (le reste du code est inchangé) ---
    tab_seances_div = soup.find('div', id='tab_seances')
    if not tab_seances_div:
        print(f"Avertissement : Aucun conteneur de données de séance ('tab_seances') trouvé sur {url}.")
        return release_date_str_formatted, {}

    date_tabs = tab_seances_div.select('.nav-tabs .nav-item a')
    if not date_tabs:
        print(f"Avertissement : Aucun onglet de date trouvé dans 'tab_seances' sur {url}.")
        return release_date_str_formatted, {}

    for tab_link in date_tabs:
        href = tab_link.get('href')
        if href and href.startswith('#t_sceances_'):
            date_str = href.replace('#t_sceances_', '')
            tab_pane_id = href[1:]
            tab_pane_content = tab_seances_div.find('div', id=tab_pane_id)
            if tab_pane_content:
                session_elements = tab_pane_content.find_all('span', class_='event-times')
                sessions_count = len(session_elements)
                sessions_by_date[date_str] = sessions_count
            else:
                sessions_by_date[date_str] = 0

    return release_date_str_formatted, sessions_by_date
#
# # --- Exemple d'utilisation ---
# target_url = "https://www.offi.fr/cinema/evenement/sirat-102675.html"
#
# release_date, session_counts = count_sessions_by_date_from_url(target_url)
#
# print(f"Date de sortie du film : {release_date}")
# print(f"Nombre de séances par date : {session_counts}")