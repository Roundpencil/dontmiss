import urllib.error
import urllib.request

import dateparser
from bs4 import BeautifulSoup


class Film:
    def __init__(self, allocine_url, title=None, release_date=None):
        """
        Initialize a Film object.

        Args: allocine_url (str): The URL of the film on Allocine. title (str, optional): The title of the film. If
        not provided, it will be parsed from the Allocine URL. release_date (datetime.date, optional): The release
        date of the film. If not provided, it will be parsed from the Allocine URL.
        """
        self.allocine_url = allocine_url
        self.title = title
        self.release_date = release_date
        self.archived = False
        self.nb_cinemas = {}  # date, number of séances

    def __str__(self):
        """
        String representation of the Film object.
        """
        # return "Le film {0} est sorti le {1}, a l'url ({2} et l'historique suivant {3})".format(self.title,
        # str(self.release_date), self.allocine_url, self.nb_cinemas)

        return f"Le film {self.title} est sorti le {str(self.release_date)}, " \
               f"à l'url ({self.allocine_url}) et l'historique suivant {self.nb_cinemas}."

    # Other methods ...


def fetch_webpage(url):
    """
    Fetch the webpage at the given URL.

    Args:
        url (str): The URL to fetch the content from.

    Returns:
        str: The HTML content of the webpage, or None if there was an error.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        response = urllib.request.urlopen(req)
        return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return None


def parse_film_data(allocine_url):
    """
    Parse the film data from the given Allocine URL.

    Args:
        allocine_url (str): The URL of the film on Allocine.

    Returns: tuple: A tuple containing the title (str) and release_date (datetime.date) of the film, or None if there
    was an error.
    """
    webpage = fetch_webpage(allocine_url)
    if not webpage:
        return None

    soup = BeautifulSoup(webpage, 'html.parser')

    title = soup.title.string.split(" - ")[0].strip()
    release_date_raw = soup.find("span", class_="date blue-link").text.strip()
    release_date = dateparser.parse(release_date_raw, languages=['fr']).date()

    return title, release_date


def film_from_url(allocine_url):
    """
    Create a Film object from the given Allocine URL.

    Args:
        allocine_url (str): The URL of the film on Allocine.

    Returns:
        Film: A Film object with the data parsed from the Allocine URL, or None if there was an error.
    """
    title, release_date = parse_film_data(allocine_url)
    if not title or not release_date:
        return None

    return Film(allocine_url=allocine_url, title=title, release_date=release_date)
