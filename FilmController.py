import json
import os
from tkinter import simpledialog

from modeleFilms import Film


class FilmController:
    def __init__(self, view):
        self.view = view
        self.load_films()

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
        url = simpledialog.askstring("Ajouter film", "Entrez l'URL Allociné du film")
        if url:
            allocine_id = # Extract the Allocine ID from the URL
            film = Film(allocine_id)
            self.films.append(film)
            self.view.update_treeview(self.films)

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


