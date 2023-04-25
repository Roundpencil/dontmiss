import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import datetime

class FilmView(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gestion des films")
        self.geometry("800x400")

        self.treeview = ttk.Treeview(self, columns=("Titre", "Date de sortie") + tuple(f"Mercredi {i}" for i in range(1, 7)), show="headings")
        for column in self.treeview["columns"]:
            self.treeview.heading(column, text=column)
            self.treeview.column(column, anchor="w", width=100)

        self.treeview.pack(fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.X)

        self.add_film_button = ttk.Button(self.button_frame, text="Ajouter film")
        self.add_film_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_film_button = ttk.Button(self.button_frame, text="Supprimer film")
        self.delete_film_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.refresh_data_button = ttk.Button(self.button_frame, text="Rafraîchir les données")
        self.refresh_data_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.options_button = ttk.Button(self.button_frame, text="Options")
        self.options_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.add_film_button.configure(command=self.add_film)
        self.update_wednesdays()

    def add_film(self):
        allocine_url = simpledialog.askstring("Ajouter un film", "Entrez l'URL Allociné du film:")
        if allocine_url:
            print(f"URL Allociné du film: {allocine_url}")
            # TODO: Create and add the new movie here

    def run(self):
        self.mainloop()

    def update_wednesdays(self):
        today = datetime.date.today()
        current_weekday = today.weekday()
        last_wednesday = today - datetime.timedelta(days=(current_weekday - 2) % 7)
        for i in range(1, 7):
            self.treeview.heading(f"Mercredi {i}", text=last_wednesday.strftime("%d/%m/%Y"))
            last_wednesday -= datetime.timedelta(days=7)

if __name__ == "__main__":
    app = FilmView()
    app.run()
