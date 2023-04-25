from FilmController import FilmController
from FilmView import FilmView

if __name__ == "__main__":
    controller = FilmController()
    view = FilmView(controller)
    controller.set_view(view)
    view.run()


# todo pas d'enregistrement
#  pas d'affichage des séances
#  pas de stockage du nombre de séances dans l'objet