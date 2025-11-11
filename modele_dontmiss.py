"""
Modèle de données pour le suivi des séances de films, optimisé pour la
performance, la robustesse et la maintenabilité.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import json
from pathlib import Path


class StatutFilm(Enum):
    """Énumération des statuts possibles pour un film."""
    AFFICHE = "affiché"
    MASQUE = "masqué"
    EN_PAUSE = "mis en pause"


@dataclass
class Film:
    """
    Représente un film et ses données de suivi. L'utilisation d'une dataclass
    génère automatiquement les méthodes __init__, __repr__, __eq__, etc. [2, 5, 8]

    Attributes:
        allocine_id: Identifiant unique AlloCiné (entier).
        titre: Titre du film.
        realisateur: Nom du ou des réalisateurs.
        date_sortie: Date de sortie nationale du film.
        seances_par_semaine: Dictionnaire des relevés.
                               Clé: date du mercredi (format 'YYYY-MM-DD').
                               Valeur: nombre de séances.
        statut: Statut actuel du film dans l'application.
        derniere_verification: Timestamp de la dernière mise à jour des séances.
    """
    allocine_id: int
    titre: str
    realisateur: str
    date_sortie: date
    seances_par_semaine: Dict[str, int] = field(default_factory=dict)
    statut: StatutFilm = StatutFilm.AFFICHE
    derniere_verification: Optional[datetime] = None

    @property
    def url_allocine(self) -> str:
        """Génère dynamiquement l'URL de la fiche AlloCiné du film."""
        return f"https://www.allocine.fr/film/fichefilm_gen_cfilm={self.allocine_id}.html"

    def ajouter_seances(self, date_mercredi: date, nombre_seances: int) -> None:
        """
        Ajoute ou met à jour un relevé de séances pour une semaine donnée.
        La date fournie doit obligatoirement être un mercredi.

        Args:
            date_mercredi: Date du premier jour de la semaine cinéma (un mercredi).
            nombre_seances: Nombre total de séances relevées pour cette semaine.

        Raises:
            ValueError: Si la date fournie n'est pas un mercredi.
        """
        if date_mercredi.weekday() != 2:  # L'index pour mercredi est 2
            raise ValueError(f"La date {date_mercredi} doit être un mercredi.")

        date_cle = date_mercredi.isoformat()
        self.seances_par_semaine[date_cle] = nombre_seances
        self.derniere_verification = datetime.now()

    def changer_statut(self, nouveau_statut: StatutFilm) -> None:
        """Modifie le statut du film."""
        self.statut = nouveau_statut

    def to_dict(self) -> Dict:
        """Convertit l'objet Film en dictionnaire pour la sérialisation JSON."""
        return {
            'allocine_id': self.allocine_id,
            'titre': self.titre,
            'realisateur': self.realisateur,
            'date_sortie': self.date_sortie.isoformat(),
            'seances_par_semaine': self.seances_par_semaine,
            'statut': self.statut.value,
            'derniere_verification': self.derniere_verification.isoformat() if self.derniere_verification else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Film':
        """Crée une instance de Film à partir d'un dictionnaire (désérialisation)."""
        return cls(
            allocine_id=data['allocine_id'],
            titre=data['titre'],
            realisateur=data['realisateur'],
            date_sortie=date.fromisoformat(data['date_sortie']),
            seances_par_semaine=data.get('seances_par_semaine', {}),
            statut=StatutFilm(data.get('statut', StatutFilm.AFFICHE.value)),
            derniere_verification=datetime.fromisoformat(data['derniere_verification']) if data.get(
                'derniere_verification') else None,
        )


class GestionnaireFilms:
    """
    Gère la collection de films suivis, incluant l'ajout, la suppression,
    la recherche et la persistance des données dans un fichier JSON.
    """

    def __init__(self, fichier_sauvegarde: str = "donnees_films.json"):
        """
        Initialise le gestionnaire de films.

        Args:
            fichier_sauvegarde: Chemin du fichier JSON pour la persistance.
        """
        self.fichier_sauvegarde = Path(fichier_sauvegarde)
        # Utilisation d'un dictionnaire pour un accès quasi-instantané (complexité O(1)) [1, 3, 4]
        self.films: Dict[int, Film] = {}

    def ajouter_film(self, film: Film) -> None:
        """Ajoute un film à la collection."""
        if film.allocine_id in self.films:
            raise ValueError(f"Le film avec l'ID {film.allocine_id} ('{film.titre}') existe déjà.")
        self.films[film.allocine_id] = film

    def obtenir_film(self, allocine_id: int) -> Optional[Film]:
        """Récupère un film par son ID AlloCiné."""
        return self.films.get(allocine_id)

    def supprimer_film(self, allocine_id: int) -> bool:
        """Supprime un film de la collection. Renvoie True si la suppression a eu lieu."""
        if allocine_id in self.films:
            del self.films[allocine_id]
            return True
        return False

    def lister_films(self, statut: Optional[StatutFilm] = None) -> List[Film]:
        """Retourne la liste de tous les films, avec un filtre optionnel par statut."""
        films_values = self.films.values()
        if statut:
            return [film for film in films_values if film.statut == statut]
        return list(films_values)

    def sauvegarder(self) -> None:
        """Sauvegarde la collection de films dans le fichier JSON."""
        data_a_sauvegarder = [film.to_dict() for film in self.films.values()]
        with self.fichier_sauvegarde.open('w', encoding='utf-8') as f:
            json.dump(data_a_sauvegarder, f, ensure_ascii=False, indent=2)

    def charger(self) -> None:
        """Charge la collection de films depuis le fichier JSON."""
        if not self.fichier_sauvegarde.exists():
            return  # Pas de fichier, on commence avec une collection vide.

        try:
            with self.fichier_sauvegarde.open('r', encoding='utf-8') as f:
                donnees_chargees = json.load(f)

            self.films.clear()
            for film_data in donnees_chargees:
                film = Film.from_dict(film_data)
                self.films[film.allocine_id] = film
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise RuntimeError(f"Erreur lors du chargement ou du parsage du fichier '{self.fichier_sauvegarde}': {e}")

    @staticmethod
    def trouver_mercredi_semaine(ref_date: date = date.today()) -> date:
        """Calcule la date du mercredi de la semaine contenant la date de référence."""
        # weekday() -> Lundi=0, ..., Dimanche=6. Mercredi=2.
        jours_a_soustraire = (ref_date.weekday() - 2) % 7
        return ref_date - timedelta(days=jours_a_soustraire)


# --- Exemple d'utilisation concrète ---
if __name__ == "__main__":
    # 1. Initialisation du gestionnaire
    gestionnaire = GestionnaireFilms("mes_films.json")

    # Optionnel: Nettoyer le fichier de sauvegarde pour un test à blanc
    if gestionnaire.fichier_sauvegarde.exists():
        gestionnaire.fichier_sauvegarde.unlink()

    # 2. Création et ajout de films
    film_1 = Film(
        allocine_id=278224,
        titre="Dune : Deuxième Partie",
        realisateur="Denis Villeneuve",
        date_sortie=date(2024, 2, 28)
    )
    film_2 = Film(
        allocine_id=254220,
        titre="Oppenheimer",
        realisateur="Christopher Nolan",
        date_sortie=date(2023, 7, 19)
    )
    gestionnaire.ajouter_film(film_1)
    gestionnaire.ajouter_film(film_2)

    # 3. Ajout de relevés de séances
    mercredi_s1 = GestionnaireFilms.trouver_mercredi_semaine(date(2024, 3, 1))
    mercredi_s2 = mercredi_s1 + timedelta(weeks=1)

    film_1.ajouter_seances(mercredi_s1, 5500)
    film_1.ajouter_seances(mercredi_s2, 4200)
    film_2.ajouter_seances(mercredi_s1, 1500)

    # 4. Modification du statut d'un film
    film_2.changer_statut(StatutFilm.EN_PAUSE)

    print("--- État avant sauvegarde ---")
    for f in gestionnaire.lister_films():
        print(f"ID: {f.allocine_id}, Titre: {f.titre}, Statut: {f.statut.value}, URL: {f.url_allocine}")
        print(f"  Séances: {f.seances_par_semaine}")
        print(
            f"  Dernière vérif: {f.derniere_verification.strftime('%Y-%m-%d %H:%M') if f.derniere_verification else 'N/A'}\n")

    # 5. Sauvegarde des données
    gestionnaire.sauvegarder()
    print(f"\n>>> Données sauvegardées dans '{gestionnaire.fichier_sauvegarde}'.\n")

    # 6. Chargement dans une nouvelle instance pour vérifier la persistance
    print("--- Chargement dans un nouveau gestionnaire ---")
    nouveau_gestionnaire = GestionnaireFilms("mes_films.json")
    nouveau_gestionnaire.charger()

    for f in nouveau_gestionnaire.lister_films():
        print(f"Film chargé: {f.titre} ({f.realisateur}) - {len(f.seances_par_semaine)} relevé(s)")
