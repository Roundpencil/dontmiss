import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import datetime

class FilmView(tk.Tk):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        self.title("Gestion des films")
        self.geometry("800x400")

        self.treeview = ttk.Treeview(self, columns=("Titre", "Date de sortie") + tuple(f"Mercredi {i}" for i in range(1, 7)), show="headings")
        for column in self.treeview["columns"]:
            self.treeview.heading(column, text=column)
            self.treeview.column(column, anchor="w", width=100)

        self.treeview.pack(fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.X)

        self.add_film_button = ttk.Button(self.button_frame, text="Ajouter film", command=self.controller.add_film)
        self.add_film_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_film_button = ttk.Button(self.button_frame, text="Supprimer film", command=self.controller.delete_film)
        self.delete_film_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.refresh_data_button = ttk.Button(self.button_frame, text="Rafraîchir les données", command=self.controller.refresh_data)
        self.refresh_data_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.options_button = ttk.Button(self.button_frame, text="Options")
        self.options_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.controller.on_close)
        self.update_wednesdays()

    def run(self):
        self.mainloop()

    def update_wednesdays(self):
        today = datetime.date.today()
        last_wednesday = today - datetime.timedelta(days=(today.weekday() - 2) % 7)
        wednesdays = [last_wednesday - datetime.timedelta(weeks=i) for i in range(6)]

        for i, wednesday in enumerate(wednesdays, start=1):
            self.treeview.heading(f"Mercredi {i}", text=wednesday.strftime("%d/%m/%Y"))

    def update_treeview(self, films):
        self.treeview.delete(*self.treeview.get_children())

        for film in films:
            if not film.archived:
                values = (film.title, film.release_date) + tuple(
                    film.nb_cinemas.get(wednesday, "") for wednesday in self.treeview["columns"][2:])
                self.treeview.insert("", "end", values=values)

