"""
Interface graphique pour l'application de suivi des séances de films.
Utilise Tkinter et son module ttk pour une interface moderne et performante.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from typing import List

from modele_dontmiss import Film, GestionnaireFilms, StatutFilm


# # Définition de classes factices pour permettre au code de s'exécuter
# class StatutFilm:
#     AFFICHE = "affiché"
#
#
# class Film:
#     pass
#
#
# class GestionnaireFilms:
#     def charger(self): self.films = {}
#
#     def lister_films(self, statut): return []
#
#     def obtenir_film(self, id): return None
#
#     def supprimer_film(self, id): pass
#
#     def sauvegarder(self): pass
#
#     @staticmethod
#     def trouver_mercredi_semaine(ref_date=date.today()):
#         jours_a_soustraire = (ref_date.weekday() - 2) % 7
#         return ref_date - timedelta(days=jours_a_soustraire)


class ApplicationSuiviFilms:
    """
    Classe principale de l'application. Gère l'interface et les interactions
    avec le gestionnaire de données.
    """

    def __init__(self, fenetre_principale: tk.Tk, gestionnaire: GestionnaireFilms):
        """
        Initialise l'application.

        Args:
            fenetre_principale: La fenêtre racine de Tkinter.
            gestionnaire: L'instance du gestionnaire de films.
        """
        self.root = fenetre_principale
        self.gestionnaire = gestionnaire
        self.semaines_colonnes: List[date] = []

        # --- Configuration de la fenêtre ---
        self.root.title("Suivi des Séances Cinéma")
        self.root.geometry("1200x600")
        self.root.minsize(900, 400)
        self.root.protocol("WM_DELETE_WINDOW", self.action_fermer_application)

        # --- Construction de l'interface ---
        self._creer_widgets()
        self.charger_et_rafraichir_vue()

    def _creer_widgets(self) -> None:
        """Construit les composants graphiques de l'application."""

        # === 1. Cadre supérieur pour les boutons d'action ===
        frame_boutons = ttk.Frame(self.root, padding="10")
        frame_boutons.pack(side=tk.TOP, fill=tk.X)

        btn_ajouter = ttk.Button(frame_boutons, text="➕ Ajouter un film", command=self.action_ajouter_film)
        btn_ajouter.pack(side=tk.LEFT, padx=(0, 5))

        btn_rafraichir = ttk.Button(frame_boutons, text="🔄 Rafraîchir les séances",
                                    command=self.action_rafraichir_seances)
        btn_rafraichir.pack(side=tk.LEFT, padx=5)

        # === 2. Séparateur visuel ===
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=10, pady=5)

        # === 3. Cadre pour le tableau (Treeview) ===
        frame_tableau = ttk.Frame(self.root, padding="10")
        frame_tableau.pack(fill=tk.BOTH, expand=True)

        # Le Treeview est le widget idéal pour afficher des données tabulaires
        self.tree = ttk.Treeview(frame_tableau, show="headings", selectmode="none")

        # Configuration des barres de défilement
        scrollbar_v = ttk.Scrollbar(frame_tableau, orient="vertical", command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(frame_tableau, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        # Positionnement dans la grille pour une bonne gestion du redimensionnement
        frame_tableau.grid_rowconfigure(0, weight=1)
        frame_tableau.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")

        # Associer l'événement de clic pour la suppression
        self.tree.bind("<ButtonRelease-1>", self._gerer_clic_action)

    def _configurer_colonnes_tableau(self):
        """Définit les colonnes du tableau en fonction des 5 dernières semaines."""
        self.semaines_colonnes = self._calculer_5_dernieres_semaines()

        colonnes_ids = ["titre", "date_sortie"] + [s.isoformat() for s in self.semaines_colonnes] + ["actions"]
        self.tree["columns"] = colonnes_ids

        # Configuration des en-têtes
        self.tree.heading("titre", text="Titre")
        self.tree.heading("date_sortie", text="Date de Sortie")
        for semaine in self.semaines_colonnes:
            self.tree.heading(semaine.isoformat(), text=semaine.strftime('%d/%m'))
        self.tree.heading("actions", text="Actions")

        # Configuration de la largeur et de l'alignement des colonnes
        self.tree.column("titre", width=300, minwidth=200)
        self.tree.column("date_sortie", width=100, minwidth=90, anchor=tk.CENTER)
        for semaine in self.semaines_colonnes:
            self.tree.column(semaine.isoformat(), width=80, minwidth=70, anchor=tk.CENTER)
        self.tree.column("actions", width=80, minwidth=80, anchor=tk.CENTER)

    def charger_et_rafraichir_vue(self) -> None:
        """
        Charge les données depuis le gestionnaire et met à jour l'affichage du tableau.
        C'est la fonction principale pour rafraîchir la GUI.
        """
        # Efface les anciennes données du tableau
        self.tree.delete(*self.tree.get_children())

        # (Re)configure les colonnes au cas où la semaine aurait changé
        self._configurer_colonnes_tableau()

        # Récupère les films à afficher (statut "affiché")
        films_affiches = self.gestionnaire.lister_films(statut=StatutFilm.AFFICHE)

        # Trie les films par date de sortie (les plus récents en premier)
        films_tries = sorted(films_affiches, key=lambda f: f.date_sortie, reverse=True)

        # Remplit le tableau avec les nouvelles données
        for film in films_tries:
            valeurs = [film.titre, film.date_sortie.strftime('%d/%m/%Y')]
            for semaine in self.semaines_colonnes:
                nb_seances = film.seances_par_semaine.get(semaine.isoformat(), "—")
                valeurs.append(nb_seances)

            valeurs.append("🗑️ Supprimer")  # Texte affiché dans la colonne action

            # Insère la ligne en associant l'ID du film via les 'tags'
            # C'est une méthode performante pour lier des métadonnées à une ligne.
            self.tree.insert("", tk.END, values=valeurs, tags=(film.allocine_id,))

    def _gerer_clic_action(self, event) -> None:
        """Gère un clic dans le tableau, spécifiquement pour la colonne 'Actions'."""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        colonne_id = self.tree.identify_column(event.x)
        if colonne_id == "#" + str(len(self.tree["columns"])):  # Est-ce la dernière colonne ?
            ligne_id = self.tree.identify_row(event.y)
            if ligne_id:
                # Récupère l'ID du film stocké dans les tags de la ligne
                film_id = int(self.tree.item(ligne_id, "tags")[0])
                self.action_supprimer_film(film_id)

    @staticmethod
    def _calculer_5_dernieres_semaines() -> List[date]:
        """Calcule les dates des 5 derniers mercredis."""
        mercredi_ref = GestionnaireFilms.trouver_mercredi_semaine()
        return [mercredi_ref - timedelta(weeks=i) for i in range(5)]

    # --- Fonctions Placeholders (logique métier à implémenter) ---

    def action_ajouter_film(self) -> None:
        """[PLACEHOLDER] Ouvre une fenêtre pour ajouter un film."""
        messagebox.showinfo("Fonctionnalité à venir",
                            "Ici s'ouvrira une fenêtre de dialogue pour ajouter un nouveau film par son ID Allociné.")
        # Logique future :
        # new_film_id = DemanderIdFilmDialog(self.root)
        # if new_film_id:
        #     # scraper les infos, créer l'objet Film, l'ajouter au gestionnaire
        #     self.gestionnaire.sauvegarder()
        #     self.charger_et_rafraichir_vue()

    def action_rafraichir_seances(self) -> None:
        """[PLACEHOLDER] Lance la mise à jour des séances pour tous les films."""
        messagebox.showinfo("Fonctionnalité à venir",
                            "Ici sera lancée la mise à jour (scraping) des séances pour tous les films suivis.")
        # Logique future :
        # self.root.config(cursor="watch") # Curseur d'attente
        # for film in self.gestionnaire.lister_films():
        #     # appeler la fonction de scraping
        #     # mettre à jour l'objet film
        # self.gestionnaire.sauvegarder()
        # self.charger_et_rafraichir_vue()
        # self.root.config(cursor="")

    def action_supprimer_film(self, film_id: int) -> None:
        """[PLACEHOLDER] Supprime un film après confirmation."""
        film = self.gestionnaire.obtenir_film(film_id)
        if not film:
            messagebox.showerror("Erreur", f"Film avec l'ID {film_id} non trouvé.")
            return

        confirmation = messagebox.askyesno(
            "Confirmation de suppression",
            f"Voulez-vous vraiment supprimer le film :\n\n'{film.titre}' ?"
        )
        if confirmation:
            # Logique future :
            # self.gestionnaire.supprimer_film(film_id)
            # self.gestionnaire.sauvegarder()
            self.charger_et_rafraichir_vue()  # Rafraîchit l'affichage
            print(f"INFO: Le film '{film.titre}' (ID: {film_id}) serait supprimé ici.")

    def action_fermer_application(self) -> None:
        """[PLACEHOLDER] Actions à exécuter à la fermeture de l'application."""
        print("Fermeture de l'application. Sauvegarde des données...")
        # Logique future :
        # self.gestionnaire.sauvegarder()
        self.root.destroy()


# --- Point d'entrée de l'application ---
if __name__ == "__main__":
    # Initialisation du gestionnaire de données
    gestionnaire_films = GestionnaireFilms("films_suivis.json")
    try:
        gestionnaire_films.charger()
    except Exception as e:
        print(f"Avertissement : Impossible de charger le fichier de données : {e}. Démarrage avec une base vide.")

    # Création de données de démo si la base est vide
    if not gestionnaire_films.lister_films():
        print("Base de données vide. Création de données de démonstration.")
        film1 = Film(allocine_id=278224, titre="Dune : Deuxième Partie", realisateur="Denis Villeneuve",
                     date_sortie=date(2024, 2, 28))
        mercredi_ref = GestionnaireFilms.trouver_mercredi_semaine()
        film1.ajouter_seances(mercredi_ref, 5500)
        film1.ajouter_seances(mercredi_ref - timedelta(weeks=1), 4200)
        gestionnaire_films.ajouter_film(film1)

        film2 = Film(allocine_id=254220, titre="Oppenheimer", realisateur="Christopher Nolan",
                     date_sortie=date(2023, 7, 19))
        film2.ajouter_seances(mercredi_ref - timedelta(weeks=2), 1500)
        gestionnaire_films.ajouter_film(film2)

    # Création de la fenêtre principale et lancement de l'application
    fenetre = tk.Tk()
    app = ApplicationSuiviFilms(fenetre, gestionnaire_films)
    fenetre.mainloop()