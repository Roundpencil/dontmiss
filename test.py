from FilmControler import *
import modeleFilms
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import sys
import datetime
import pickle


#todo :  génrer une page web et l'afficher sur Yogi
#todo : comprendre ce qu'il se passe quand on supprime, et forcer la mise à jour quand on ajoute


# #commencer par charger une liste de fims par défaut
# #SI KO > on part de zéro
# #sinon on charge
# #manuellement, sauver à la fin du programme > rajouter bouton sauvegarder // sinon trouver comment faire automatiquement
#
# premierFilm = modeleFilms.Film("titane", allocineUrl="https://www.allocine.fr/film/fichefilm_gen_cfilm=277192.html")
# #premierFilm.update_seances()
# #print(testfilm.nbCinema)
#
# premierFilm.listeEvolutionsSeances()
#
# print("update dates")
#
# premierFilm.update_seances(datetime.date(2021, 9, 15))
# premierFilm.listeEvolutionsSeances()
#
#
# # testdict = dict()
# #
# # testdict[1] = "un"
# #
# # print(testdict[1])
# # print(testdict[2])
#
# secondFilm = modeleFilms.Film("Serre moi fort", dateSortie=datetime.date(2021, 1, 1), allocineUrl="https://www.allocine.fr/film/fichefilm_gen_cfilm=271838.html")
# #secondFilm.update_seances()
#
# #monC = FenetrePrincipale()

# listeFilm = list()
# # listeFilm.append(premierFilm)
# # listeFilm.append(secondFilm)
# #


mode = "run"

if mode == "run":
    app = QtWidgets.QApplication(sys.argv)

    # window = FenetrePrincipale(listeFilms=listeFilm) #version sans pickles, NE PAS UTLISER

    window = FenetrePrincipale() #marche parfaitement !!!!! Commenté pour d'autres tests

    window.show()
    app.exec_()

if mode=="readadaptiondata":
    with open('mypicklefile', 'rb') as f1:
        listeFilms = pickle.load(f1)

if mode=="QT indexes":
    # for role in QtCore.Qt.ItemDataRole:
    print(QtCore.Qt.ItemDataRole.value)




# filmTest = modeleFilms.Film.filmFromUrl("https://www.allocine.fr/film/fichefilm_gen_cfilm=271838.html")
#
# filmTest = modeleFilms.Film.filmFromUrl("https://www.allocine.fr/film/fichefilm_gen_cfilm=133392.html")

# filmTest = modeleFilms.Film("https://www.allocine.fr/film/fichefilm_gen_cfilm=133392.html")
# filmTest.update_seances()
# print(filmTest)

