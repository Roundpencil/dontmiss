import json
import os
import re
from tkinter import simpledialog, messagebox

from Film import Film


class FilmController:
    # def __init__(self, view):
    #     self.model = model
    #     self.view = view
    #     self.setup_callbacks()

    def __init__(self):
        self.view = None
        self.films = []

    def set_view(self, view):
        self.view = view

    def load_films(self):
        if os.path.exists("films.json"):
            with open("films.json", "r") as f:
                data = json.load(f)
                self.films = [Film.from_json(film_data) for film_data in data]
        else:
            self.films = []

        self.view.update_treeview(self.films)

    def save_films(self):
        data = [film.to_json() for film in self.films]
        with open("films.json", "w") as f:
            json.dump(data, f)

    def add_film(self):
        if url := simpledialog.askstring(
            "Ajouter film", "Entrez l'URL Allociné du film"
        ):
            allocine_id_pattern = re.compile(r"film\/fichefilm_gen_cfilm=(\d+).html")
            if match := allocine_id_pattern.search(url):
                allocine_id = match[1]
                film = Film(allocine_id)
                self.films.append(film)
                self.view.update_treeview(self.films)
            else:
                messagebox.showerror("Erreur", "L'URL Allociné entrée est invalide.")

    def delete_film(self):
        if selected_item := self.view.treeview.selection():
            index = self.view.treeview.index(selected_item)
            self.films[index].archived = True
            self.view.update_treeview(self.films)

    def refresh_data(self):
        for film in self.films:
            if not film.archived:
                for wednesday in self.view.treeview["columns"][2:]:
                    film.fetch_screenings(wednesday)

        self.view.update_treeview(self.films)

    def on_close(self):
        self.save_films()
        self.view.destroy()
