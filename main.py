from FilmController import FilmController
from FilmView import FilmView

if __name__ == "__main__":
    view = FilmView()
    controller = FilmController(view)
    view.run()