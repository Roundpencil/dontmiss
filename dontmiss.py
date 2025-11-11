from modele_dontmiss import GestionnaireFilms
import tkinter as tk
from GUI_Dontmiss import ApplicationSuiviFilms

# Initialisation du gestionnaire de données
gestionnaire_films = GestionnaireFilms("films_suivis.json")
try:
    gestionnaire_films.charger()
except Exception as e:
    print(f"Avertissement : Impossible de charger le fichier de données : {e}. Démarrage avec une base vide.")

# Création de données de démo si la base est vide
# Création de la fenêtre principale et lancement de l'application
fenetre = tk.Tk()
app = ApplicationSuiviFilms(fenetre, gestionnaire_films)
fenetre.mainloop()