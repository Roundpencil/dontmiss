import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import base64

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

        # Stratégie 1 (principale) : Recherche du lien "Voir toutes les séances (X)"
        nombre_seances = 0
        seances_link = soup.select_one('.end-section-link')
        if seances_link:
            texte_seances = seances_link.get_text(strip=True)
            match = re.search(r'Voir toutes les séances \((\d+)\)', texte_seances)
            if match:
                nombre_seances = int(match.group(1))

        # # Stratégie 2 (secours) : Recherche plus générale du nombre entre parenthèses
        # if nombre_seances == 0:
        #     seances_elements = soup.select('.end-section-link-container span')
        #     for element in seances_elements:
        #         texte = element.get_text(strip=True)
        #         match = re.search(r'\((\d+)\)', texte)
        #         if match:
        #             nombre_seances = int(match.group(1))
        #             break

        return date_sortie, nombre_seances

    except requests.exceptions.Timeout:
        print("Timeout lors de la requête, le site est peut-être lent ou bloque les requêtes.")
        return None, 0
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête: {e}")
        return None, 0
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return None, 0


# # Exemple d'utilisation
# if __name__ == "__main__":
#     url = "https://www.allocine.fr/film/fichefilm_gen_cfilm=317783.html"
#     date_sortie, nb_seances = extract_allocine_info(url)
#     print(f"Date de sortie: {date_sortie}")
#     print(f"Nombre de séances: {nb_seances}")

def recherche_allocine(terme_recherche):
    """
    Recherche un terme sur AlloCiné et extrait les résultats de films.

    Args:
        terme_recherche (str): Le terme à rechercher sur AlloCiné

    Returns:
        list: Liste de tuples (nom du film, realisateur, date_sortie, id_allocine) correspondant aux résultats
    """
    # Construction de l'URL de recherche
    url = f"https://www.allocine.fr/rechercher/?q={terme_recherche}"

    # En-têtes pour simuler un navigateur (éviter le blocage)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.allocine.fr/'
    }

    try:
        # Envoi de la requête
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parsing de la page avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Recherche des résultats de films dans la section "Films"
        resultats = []

        # On cible spécifiquement la section des films
        section_films = soup.find('section', class_='section movies-results')
        # print(section_films)

        if section_films:
            # Trouver tous les éléments de film dans cette section
            elements_films = section_films.find_all('div', class_='card entity-card entity-card-list cf')
            # print(len(elements_films))
            # print(elements_films[0])

            for film in elements_films:
                # 1. Extraction du titre du film
                titre_element = film.find('span', class_='meta-title-link')
                titre = titre_element.text.strip() if titre_element else None

                # 2. Extraction du réalisateur
                realisateur_element = film.find(class_='dark-grey-link')
                realisateur = realisateur_element.text.strip() if realisateur_element else None

                # 3. Extraction de la date de sortie
                date_element = film.find('span', class_='date')
                date_sortie = date_element.text.strip() if date_element else None

                # 4. Extraction de l'id
                movie_id = 0
                # Méthode 1 : Chercher les liens thumbnail qui contiennent généralement l'ID du film
                thumbnail_links = film.select('.thumbnail-container.thumbnail-link')

                for link in thumbnail_links:
                    # Obtenir la classe qui contient le lien encodé
                    class_value = link.get('class')[0]

                    # Si la classe commence par 'ACrL'
                    if class_value.startswith('ACrL'):
                        try:
                            # Décodage Base64
                            decoded = base64.b64decode(class_value[4:]).decode('utf-8')

                            # Extraction de l'ID à partir du chemin décodé
                            match = re.search(r'cfilm=(\d+)', decoded)
                            if match:
                                movie_id = match.group(1)
                        except:
                            pass
                # Méthode 2 : Extraction à partir des données JavaScript (jsEntities)
                # js_entities_pattern = re.compile(r'var jsEntities = \{\"([^"]+)\":')
                # match = js_entities_pattern.search(str(film))
                #
                # if match:
                #     encoded_id = match.group(1)
                #     try:
                #         # Décodage Base64 de l'ID du film
                #         decoded = base64.b64decode(encoded_id).decode('utf-8')
                #         # Format attendu après décodage: "Movie:28367"
                #         movie_id = decoded.split(':')[1]
                #     except:
                #         pass

                resultats.append((titre, realisateur, date_sortie, movie_id))

                # ##### tentatived'une focntion dédiée
                # resultats.append(extraire_infos_film(str(film)))



        return resultats

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return []
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return []


# # Exemple d'utilisation
# if __name__ == "__main__":
#     resultats = recherche_allocine("sirat")
#     for film, url in resultats:
#         print(f"Film: {film}")
#         print(f"URL: {url}")
#         print("-" * 30)
