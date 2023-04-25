import requests
from bs4 import BeautifulSoup
import datetime
import json

class Film:
    URL = "https://www.allocine.fr/film/fichefilm_gen_cfilm={}.html"

    def __init__(self, allocine_id):
        self.allocine_id = allocine_id
        self.fetch_details()
        self.nb_cinemas = {}
        self.archived = False

    def fetch_details(self):
        url = self.URL.format(self.allocine_id)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        self.title = soup.find('div', class_='titlebar-title titlebar-title-lg').text.strip()
        self.release_date = soup.find('span', class_='date blue-link').text.strip()

    def fetch_screenings(self, date):
        if date not in self.nb_cinemas:
            # TODO: Fetch the number of screenings for the given date and update self.nb_cinemas

            # Example:
            self.nb_cinemas[date] = 42

    def to_json(self):
        return {
            "allocine_id": self.allocine_id,
            "title": self.title,
            "release_date": self.release_date,
            "nb_cinemas": self.nb_cinemas,
            "archived": self.archived,
        }

    @classmethod
    def from_json(cls, data):
        film = cls(data["allocine_id"])
        film.title = data["title"]
        film.release_date = data["release_date"]
        film.nb_cinemas = data["nb_cinemas"]
        film.archived = data["archived"]
        return film
