import datetime

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QTableView, QAbstractItemView, QMessageBox
import pickle

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PyQt5.QtWidgets import QMainWindow, QInputDialog

import modeleFilms
from GUIFilms import Ui_MainWindow


class FenetrePrincipale(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None, liste_films=None, parametres=None):
        super().__init__(parent)
        self.setupUi(self)

        # print("constructeur lancé")
        if liste_films is None:
            # charger automatiquement le film quand on ouvre
            # with open('mypicklefile', 'rb') as f1:
            try:
                with open('films.dontmiss', 'rb') as f1:
                    liste_films = pickle.load(f1)
            except Exception:
                liste_films = []

        # self._filmsActifs = list()
        # self._filmsArchived = list()
        self._listeFilm = liste_films
        self._filmsAffichables = []

        if parametres is None:
            try:
                with open('dontmiss.parametres', 'rb') as f1:
                    parametres = pickle.load(f1)
                print("Paramètres chargés")
            except:
                parametres = {
                    "Afficher archives": False,
                    "Afficher non sortis": True,
                    "Afficher sans seances": True,
                }
        self._parametres = parametres  # nom du film, boolean
        # todo : faire une fenetre puor changer/visualiser les paramètres encours

        # for film in self._listeFilm: print(str(film))

        self.updateFilmsAffichables(afficher=False)

        self.modelTable = TableModel3(self._filmsAffichables)

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.modelTable)

        self.tableFilms.setSortingEnabled(True)

        self.tableFilms.setModel(self.proxyModel)

        self.tableFilms.setColumnWidth(0, 315)

        self.proxyModel.sort(2, Qt.AscendingOrder)

        self.tableFilms.setSelectionBehavior(QTableView.SelectRows)
        self.tableFilms.setSelectionMode(QAbstractItemView.SingleSelection)

        print("modele en place")
        # https: // www.pythonguis.com / tutorials / modelview - architecture /
        self.pushButton.pressed.connect(self.refraichirTout)
        self.pushButton_2.pressed.connect(self.afficherPopUpFilm)
        self.pushButton_3.pressed.connect(self.supprimer)

    def updateFilmsAffichables(self, afficher=True):
        print("Nombre de films dans la liste avant update {0}".format(len(self._filmsAffichables)))
        self._filmsAffichables.clear()
        print("Update films affichables lancés")

        for film in self._listeFilm:
            if not self._parametres["Afficher archives"] and film.archived: continue
            if not self._parametres["Afficher non sortis"] and not film.estSorti(): continue
            if not self._parametres["Afficher sans seances"] and not film.aDesSeances(): continue

            self._filmsAffichables.append(film)

        print("Nombre de films dans la liste après update {0}".format(len(self._filmsAffichables)))
        # todo : comprendre pourquoi des lignes vides apparaissent
        if afficher:
            print(
                "Nombre de lignes dans la table avant refresh visuel : {0}".format(self.tableFilms.model().rowCount()))
            self.tableFilms.setSortingEnabled(False)
            # self.modelTable.layoutChanged.emit() #affichec equ'on vourait... mais fait tout planter, mais qui rend bien visuellement
            # self.proxyModel.layoutChanged.emit() #marche
            self.tableFilms.model().layoutChanged.emit()  # marche aussi, mais toujours pas ce qu'on voudrait comme affichage
            self.tableFilms.setSortingEnabled(True)
            self.tableFilms.sortByColumn(2, Qt.AscendingOrder)
            print("Update fini. on voit une différence?")
            print(
                "Nombre de lignes dans la table après refresh visuel : {0}".format(self.tableFilms.model().rowCount()))

    def refraichirTout(self):
        for film in self._listeFilm: film.update_seances()
        self.updateFilmsAffichables()

    def closeEvent(self, event):  # la méthode appellée quand on ferme, qui permet de sauver
        toDump = self._listeFilm

        # sauver autoamiquement quand on ferme
        with open('films.dontmiss', 'wb') as f1:
            pickle.dump(toDump, f1)

        # print("pif")

        secondSave = 'films.' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".dontmiss"

        print("secondsave = " + secondSave)

        with open(secondSave, 'wb') as f1:
            pickle.dump(toDump, f1)

        # # sauver les paramètres
        with open('dontmiss.parametres', 'wb') as f1:
            pickle.dump(self._parametres, f1)
        #
        print("et on quitte !")

    def afficherPopUpFilm(self):
        # item, ok = QInputDialog.getItem(self, "select input dialog",
        #                                 "list of languages", items, 0, False)
        print("poum")
        urlAllocine, ok = QInputDialog.getText(self, "Ajouter un nouveau film", "Url Allociné : ")
        print("url : " + urlAllocine)
        print("film Créé")

        if ok:
            print("ok")
            try:
                newFilm = modeleFilms.Film(urlAllocine)
            except Exception as e:
                print(f"erreur : {e}")
                # on n'a pas pu créer le film
                # print("URL invalide") #remplacé par une popup
                popup = QMessageBox()
                popup.setText("Url non valide")
                popup.setWindowTitle("Erreur")
                popup.exec_()
                return

            newFilm.update_seances()
            print("Film à vérifier / ajouter créé")

            # vérifier que le film n'est pas déjà dans la liste.
            # Si oui > on le désarchive
            # sinon > on l'ajoute SI IL NEST PAS DEJA PRESENT

            for chaqueFilm in self._listeFilm:
                print("Je suis en train de regarder {0}".format(chaqueFilm.titre))
                if chaqueFilm == newFilm:
                    print("j'ai trouvé un film !")
                    print(
                        "le film {0} est déjà présent dans les films archivés et il s'appelle {1}, et il est archivé : {2}".format(
                            newFilm, chaqueFilm, chaqueFilm.archived))
                    self.desarchiverFilm(chaqueFilm)  # on désarchive dans tous les cas
                    # self.updateFilmsAffichables()
                    return

            # a ce stade on sait que le film n'est pas dans les films, on l'ajoute à la liste et on update la liste à afficher
            print("Le film à ajouter n'existait pas déjà")

            # self._filmsActifs.append(newFilm)
            self._listeFilm.append(newFilm)
            print("film {0} ajouté".format(newFilm))
            # self.tableFilms.update()
            self.updateFilmsAffichables()

            return 1
        else:
            print("on a annulé")
            return -1

    def supprimer(self):
        # #selected cell value.
        # print("pouf 0")
        # index = self.tableFilms.selectionModel().currentIndex()
        # table = self.tableFilms
        # # print("pouf 1")
        #
        # selectionmodel = table.selectionModel()
        # # print("pouf 2")

        indexASupprimer = self.tableFilms.currentIndex()

        print("index = " + str(indexASupprimer.row()))
        # print("paf")
        # print("film à supprimer :" + self.proxyModele.data(indexASupprimer, 99))
        # print("titre film à supprimer depuis le proxy : " + self.proxyModel.data(indexASupprimer, 99))
        print("titre film à supprimer depuis l'index : " + indexASupprimer.data(99))
        # url = self.proxyModel.data(indexASupprimer, 99)
        url = indexASupprimer.data(99)

        # print("pif")

        # print("Url : " + url)
        # for film in self._filmsActifs:
        for film in self._listeFilm:

            # print("le film {0} est archivé? {1}".format(film.titre, str(film.archived)))

            if film.allocineUrl == url:
                print("film à supprimé trouvé ! Le film {0} est archivé? {1}".format(film.titre, str(film.archived)))
                # film.archived = True
                self.archiverFilm(film)
                print("et après? le film {0} est archivé? {1}".format(film.titre, str(film.archived)))
                break

        print("Suppression terminée")

    def archiverFilm(self, film):
        film.archived = True
        self.updateFilmsAffichables()

    def desarchiverFilm(self, film):
        film.archived = False
        self.updateFilmsAffichables()


class TableModel3(QtCore.QAbstractTableModel):  # le modele repris du site
    def __init__(self, films):
        super(TableModel3, self).__init__()
        self._listeFilms = films

    def data(self, index, role):
        # print("index = {0}, role = {1}".format(str(index), role))
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            # structure pour un tableau de data : return self._data[index.row()][index.column()]
            if index.column() == 0:  # titre film
                #     print("la méthode data a été appelée dans le tableview pour afficher le titre ")
                return self._listeFilms[index.row()].titre  # ca, ca marche, commenté pour tester

            elif index.column() == 1:  # date sortie
                # print("date sortie : " + str(self._listeFilms[index.row()].dateSortie))
                return str(self._listeFilms[index.row()].dateSortie)
            #                return "date sortie"

            elif index.column() <= 7:
                try:
                    clef = modeleFilms.Film.niemeDerniereDate(index.column() - 2)
                    # clef = datetime.date.today()
                    # print("key = " + str(clef))
                    # offset = (clef.weekday() - 2) % 7  # on décale du nombre de jours nécessaire
                    # offset += (index.column() - 2) * (7)
                    # clef -= datetime.timedelta(days=offset)  # on a la date du précédent mercredi, qui sert de clef

                    # print("key adjusted = " + str(clef))
                    # print("nb cinema au {0} : {1}".format(str(clef), self._listeFilms[index.row()].nbCinemas[clef]))
                    #                    return str(self._listeFilms[index.row()].nbCinemas[clef])
                    return int(str(self._listeFilms[index.row()].nbCinemas[clef]))
                    # return str(self._listeFilms[index.row()].dateSortie)
                except Exception as e:
                    # print("erreur survenue en {0}, {1} : {2}".format(index.row(), index.column(), e))
                    pass
            else:
                print("{0} est en dehors des limites".format(index.column()))
            # else:
            #     return "pas titre"
        if role == Qt.BackgroundColorRole:
            if self._listeFilms[index.row()].dateSortie > datetime.date.today():
                return QColor(Qt.gray)
        if role == 99:  # dans ce cas on appelle pour avoir l'URL du film
            print("on m'a demandé l'url film avec l'index {0}, {1}".format(index.row(), index.column()))
            return self._listeFilms[index.row()].allocineUrl

    def rowCount(self, index):
        # The length of the outer list.
        # print("taille table = " + str(len(self._listeFilms)))
        return len(self._listeFilms)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return 7

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                # return ["X", "Y", "Z"][section]
                return (["Titre", "Date sortie"] + modeleFilms.Film.nDernieresDates(5, True))[section]

                # print(header)

# archivé avant l'insertion des films affichables
# class FenetrePrincipale(QMainWindow, Ui_MainWindow):
#
#     def __init__(self, parent=None, listeFilms=None, filtres=None):
#         super().__init__(parent)
#         self.setupUi(self)
#
#         # print("constructeur lancé")
#         if listeFilms == None:
#             # charger automatiquement le film quand on ouvre
#             # with open('mypicklefile', 'rb') as f1:
#             try:
#                 with open('films.dontmiss', 'rb') as f1:
#                     listeFilms = pickle.load(f1)
#             except:
#                 listeFilms = list()
#
#         self._filmsActifs = list()
#         self._filmsArchived = list()
#         self._listeFilm = listeFilms
#         self._filmsAffichables = list()
#
#         if filtres == None:
#             try:
#                 with open('filtres.dontmiss', 'rb') as f1:
#                     listeFilms = pickle.load(f1)
#             except:
#                 filtres = dict()  # initialisation du dictionnaire avec des vfaleurs par défaut
#                 filtres["Archive"] = False
#                 filtres["Non sorti"] = False
#                 filtres["Sans seances"] = False
#
#         self._filtres = filtres  # nom du film, boolean
#
#         for film in listeFilms:
#             # film.archived = False #utilisé pour resetter les etats archived > utilisé pour des tests
#             if film.archived:
#                 self._filmsArchived.append(film)
#             else:
#                 self._filmsActifs.append(film)
#
#         print("films actifs " + str(self._filmsActifs))
#         print("films archived " + str(self._filmsArchived))
#
#         self.modelTable = TableModel3(self._filmsActifs)
#
#         self.proxyModel = QSortFilterProxyModel()
#         self.proxyModel.setSourceModel(self.modelTable)
#
#         self.tableFilms.setSortingEnabled(True)
#
#         self.tableFilms.setModel(self.proxyModel)
#
#         self.tableFilms.setColumnWidth(0, 315)
#
#         self.proxyModel.sort(2, Qt.AscendingOrder)
#
#         # print("modele chargé" + str(listeFilms))
#
#         # self.tableFilms.setModel(self.modelTable) #remplacé par l'arrivée du proxy
#
#         self.tableFilms.setSelectionBehavior(QTableView.SelectRows)
#         self.tableFilms.setSelectionMode(QAbstractItemView.SingleSelection)
#
#         print("modele en place")
#         # https: // www.pythonguis.com / tutorials / modelview - architecture /
#         self.pushButton.pressed.connect(self.refraichirTout)
#         self.pushButton_2.pressed.connect(self.afficherPopUpFilm)
#         self.pushButton_3.pressed.connect(self.supprimer)
#
#     def updateFilmsAffichables(self):
#         self._filmsAffichables = list()
#         for film in self._listeFilm:
#             # if film.archived:
#             #     self._filmsArchived.append(film)
#             # else:
#             #     self._filmsActifs.append(film)
#             if filtres["Archive"] or not film.archived: continue
#             if filtres["Non sorti"] or not film.dateSortie < datetime.datetime.now(): continue
#             if filtres["Sans seances"] or film.nbCinemas[modeleFilms.Film.niemeDerniereDate(1)] == 0: continue
#             self._filmsAffichables.append(film)
#
#     def refraichirTout(self):
#         for film in self._filmsActifs:
#             film.update_seances()
#         for film in self._filmsArchived:
#             film.update_seances()
#
#     def closeEvent(self, event):  # la méthode appellée quand on ferme, qui permet de sauver
#         toDump = self._filmsActifs + self._filmsArchived
#         # sauver autoamiquement quand on ferme
#         with open('films.dontmiss', 'wb') as f1:
#             pickle.dump(toDump, f1)
#
#         # print("pif")
#
#         secondSave = 'films.' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".dontmiss"
#
#         print("secondsave = " + secondSave)
#
#         with open(secondSave, 'wb') as f1:
#             pickle.dump(toDump, f1)
#         # print("et on quitte !")
#
#     def afficherPopUpFilm(self):
#         # item, ok = QInputDialog.getItem(self, "select input dialog",
#         #                                 "list of languages", items, 0, False)
#         print("poum")
#         urlAllocine, ok = QInputDialog.getText(self, "Ajouter un nouveau film", "Url Allociné : ")
#         print("url : " + urlAllocine)
#         print("film Créé")
#         if ok:
#             newFilm = modeleFilms.Film(urlAllocine)
#             newFilm.update_seances()
#
#             # vérifier que le film n'est pas déjà dans la liste.
#             # Si oui > on le désarchive
#             # sinon > on l'ajoute SI IL NEST PAS DEJA PRESENT
#             for chaqueFilm in self._filmsArchived:
#                 # if chaqueFilm.allocineurl == newFilm.allocineUrl:
#                 if chaqueFilm == newFilm:
#                     print("le film {0} est déjà présent dans les films archivés et il s'appelle {1}".format(newFilm,
#                                                                                                             chaqueFilm))
#                     self.desarchiverFilm(chaqueFilm)
#                     # chaqueFilm.archived = False
#                     self.tableFilms.update()
#                     return 0
#
#             for chaqueFilm in self._filmsActifs:
#                 # if chaqueFilm.allocineurl == newFilm.allocineUrl:
#                 if chaqueFilm == newFilm:
#                     print("le film {0} est déjà présent dans les films actifs et il s'appelle {1}".format(newFilm,
#                                                                                                           chaqueFilm))
#                     self.tableFilms.update()
#                     return 0
#
#             self._filmsActifs.append(newFilm)
#             print("film {0} ajouté".format(newFilm))
#             # self.tableFilms.model().layoutChanged.emit() #pour dire à la table qu'on a rajouté une ligne #ne marche pas, supprimer
#             self.tableFilms.update()
#             return 1
#         else:
#             print("on a annulé")
#             return -1
#
#     def supprimer(self):
#         # #selected cell value.
#         # print("pouf 0")
#         # index = self.tableFilms.selectionModel().currentIndex()
#         table = self.tableFilms
#         # print("pouf 1")
#
#         selectionmodel = table.selectionModel()
#         # print("pouf 2")
#
#         indexASupprimer = self.tableFilms.currentIndex()
#
#         print("index = " + str(indexASupprimer.row()))
#         print("paf")
#         # print("film à supprimer :" + self.proxyModele.data(indexASupprimer, 99))
#         # print("titre film à supprimer depuis le proxy : " + self.proxyModel.data(indexASupprimer, 99))
#         print("titre film à supprimer depuis l'index : " + indexASupprimer.data(99))
#         # url = self.proxyModel.data(indexASupprimer, 99)
#         url = indexASupprimer.data(99)
#
#         # print("pif")
#
#         # print("Url : " + url)
#         for film in self._filmsActifs:
#             # film.archived = False #test pour remettre en place la valeur archivée
#             # print("le film {0} est archivé? {1}".format(film.titre, str(film.archived)))
#
#             if film.allocineUrl == url:
#                 print("le film {0} est archivé? {1}".format(film.titre, str(film.archived)))
#                 # film.archived = True
#                 self.archiverFilm(film)
#                 print("et après? le film {0} est archivé? {1}".format(film.titre, str(film.archived)))
#                 break
#
#         self.tableFilms.update()
#         # self.proxyModel.sort(2, Qt.AscendingOrder)
#
#     def archiverFilm(self, film):
#         film.archived = True
#         self._filmsActifs.remove(film)
#         self._filmsArchived.append(film)
#         self.tableFilms.model().layoutChanged.emit()
#
#     def desarchiverFilm(self, film):
#         film.archived = False
#         self._filmsArchived.remove(film)
#         self._filmsActifs.append(film)
#         self.tableFilms.model().layoutChanged.emit()
