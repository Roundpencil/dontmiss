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


def extract_allocine_info(url):
    """
    Extrait la date de sortie et le nombre de séances d'une page de film Allociné

    Args:
        url (str): URL d'une page film Allociné (format: https://www.allocine.fr/film/fichefilm_gen_cfilm=XXXXX.html)

    Returns:
        tuple: (date_sortie (datetime.date), nombre_seances (int))
    """
    # Ajout d'un User-Agent pour éviter d'être bloqué
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9'
    }

    try:
        # Augmenter le timeout pour éviter les erreurs
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraction de la date de sortie
        date_sortie = None
        date_elem = soup.select_one('div.meta-body-info span.date')
        if date_elem:
            date_text = date_elem.text.strip()
            # Extraction du format "XX mois YYYY"
            match = re.search(r'(\d+\s+\w+\s+\d{4})', date_text)
            if match:
                date_str = match.group(1)
                # Conversion de la date en format datetime
                try:
                    # Conversion du mois en français vers un nombre
                    for i, mois in enumerate(['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                                              'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']):
                        date_str = date_str.replace(mois, str(i + 1))

                    # Reformatage et parsing
                    jour, mois, annee = date_str.split()
                    date_sortie = datetime(int(annee), int(mois), int(jour)).date()
                except Exception as e:
                    print(f"Erreur lors de la conversion de la date: {e}")

        # Extraction du nombre de séances
        # nb_seances = 0
        # seances_elem = soup.select_one('a.button.button-md.button-primary-full')
        # print(seances_elem)
        # if seances_elem and "séance" in seances_elem.text.lower():
        #     seances_text = seances_elem.text.strip()
        #     # Extraction du nombre (peut être formaté comme "XXX séances")
        #     match = re.search(r'(\d+)', seances_text)
        #     if match:
        #         nb_seances = int(match.group(1))
        # Stratégie 1 (principale) : Recherche du lien "Voir toutes les séances (X)"
        nombre_seances = 0
        seances_link = soup.select_one('.end-section-link')
        if seances_link:
            texte_seances = seances_link.get_text(strip=True)
            match = re.search(r'Voir toutes les séances \((\d+)\)', texte_seances)
            if match:
                nombre_seances = int(match.group(1))

        return date_sortie, nombre_seances

    except requests.exceptions.Timeout:
        print("Timeout lors de la requête, le site est peut-être lent ou bloque les requêtes.")
        return (None, 0)
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête: {e}")
        return (None, 0)
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return (None, 0)


# # Exemple d'utilisation
# if __name__ == "__main__":
#     url = "https://www.allocine.fr/film/fichefilm_gen_cfilm=317783.html"
#     date_sortie, nb_seances = extract_allocine_info(url)
#     print(f"Date de sortie: {date_sortie}")
#     print(f"Nombre de séances: {nb_seances}")