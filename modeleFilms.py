import urllib.request
import urllib.error
import re
import datetime
import dateparser


# modele :
# film
#   date sortie
#   nb séances
#   titre
#   id



class Film:
    #Entrées :
    # url allociné : obligatoire
    # titre : si vide, on lit l'URL
    # dateSortie : si vide on lit l'url
    def __init__(self, allocineUrl, titre=None, dateSortie=None, ):
        self.allocineUrl = allocineUrl
        webpage = ""

        if titre is None or dateSortie is None:
            webpage = self.lire_url_allocine()

        if webpage is None:
            return


            # fid = urllib.request.urlopen(allocineUrl)
            # webpage = fid.read().decode('utf-8')

        if titre is None:
            # trouver le titre
            # format : <title>Serre Moi Fort - film 2020 - AlloCiné</title>
            matches = re.findall("<title>(.*?)- film", webpage)
            titre = matches[0]
        self.titre = titre

        print('two')

        if dateSortie is None:
            # trouver la date de sortie
            # format : date blue-link">8 septembre 2021</span> SANS les sauts de ligne
            matches = re.findall("date blue-link\">(.*?)</", webpage.replace('\n', " "))
            # dateNonformatee = matches[0]
            dateSortie = dateparser.parse(matches[0], languages=['fr']).date()

        print('three')

        self.dateSortie = dateSortie
        self.archived = False
        self.nbCinemas = {}  # date, nb séances

    def lire_url_allocine(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.3'
        }

        req = urllib.request.Request(self.allocineUrl, headers=headers)

        try:
            response = urllib.request.urlopen(req)
            return response.read().decode('utf-8')
            # content = response.read()
            # print(content)
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None

    def __str__(self):
        return "Le film {0} est sorti le {1}, a l'url ({2} et l'historique suivant {3})".format(self.titre, str(self.dateSortie), self.allocineUrl, self.nbCinemas)

    def __eq__(self, other):
        return self.allocineUrl == other.allocineUrl

    def listeEvolutionsSeances(self):
        for clef in sorted(self.nbCinemas.keys()):
            print("au {0} il y avait {1} salles pour {2}".format(str(clef), self.nbCinemas[clef], self.titre))

    def update_seances(self, date=None):
        try:
            # fid = urllib.request.urlopen(self.allocineUrl)
            # webpage = fid.read().decode('utf-8')
            webpage = self.lire_url_allocine()
            # texte allociné : 70
        except Exception as e:
            print(f"Exception : {e}")

        if date == None:
            clef = datetime.date.today()  # on trouve la date d'aujourd'hui
        else:
            clef = date

        offset = (clef.weekday() - 2) % 7  # on décale du nombre de jours nécessaire
        clef = clef - datetime.timedelta(days=offset)  # on a la date du précédent mercredi, qui sert de clef

        if clef in self.nbCinemas:
            print("A la date {0}, il y a déjà {1} séances pour {2}".format(str(clef), self.nbCinemas[clef], self.titre))
            pass
        else:
            try:
                matches = re.findall("<span class=\"txt\">Séances \((.*?)\)</span>", webpage)
                nbCinemas = matches[0]

                #        print("seances allocine pour {0} : {1}".format(self.titre, str(matches[0])))
                print("seances ajoutée pour {0}, au {2} : {1}".format(self.titre, nbCinemas, str(clef)))
                self.nbCinemas[clef] = nbCinemas
            except:
                print("il n'y avait pas de séances pour {0} à la date {1}".format(self.titre, str(clef)))
                pass

        # mk2url = "https://www.mk2.com/films/" + str(self.film_id_mk2) + "-" + self.titre
        # ugcurl = "https://www.ugc.fr/film.html?id=" + str(self.film_id_ugc)
        # print("Pour " + self.titre + " : ")
        #
        # # fid = urllib.request.urlopen(ugcurl)
        # # webpage = fid.read().decode('utf-8')
        # # seancesugc = webpage.count("options_nav_cinemas_")
        # # seancesugc = seancesugc
        # # print("seances ugc : " + str(seancesugc))
        #
        # fid = urllib.request.urlopen(mk2url)
        # webpage = fid.read().decode('utf-8')
        # seancesmk2 = webpage.count("/salles/")
        # seancesmk2 = (seancesmk2-8)/4
        # print("seances mk2 : " + str(seancesmk2))

    def estSorti(self):
        return self.dateSortie < datetime.date.today()

    def aDesSeances(self):
        try:
            if self.nbCinemas[Film.niemeDerniereDate(1)] == 0:
                return False
            else:
                return True
        except:
            return False



    @staticmethod
    def niemeDerniereDate(n):
        sortie = datetime.date.today()
        # print("key = " + str(sortie))
        offset = (sortie.weekday() - 2) % 7  # on décale du nombre de jours nécessaire
        offset += n * 7
        sortie -= datetime.timedelta(days=offset)  # on a la date du précédent mercredi, qui sert de clef
        return sortie

    @staticmethod
    def nDernieresDates(monRange, asString=False):
        if asString:
            return [str(Film.niemeDerniereDate(n)) for n in range(monRange)]
        else:
            return [Film.niemeDerniereDate(n) for n in range(monRange)]

    @staticmethod
    def filmFromUrl(allocineUrl):
        fid = urllib.request.urlopen(allocineUrl)
        webpage = fid.read().decode('utf-8')

        # faire un ajouter ou on ne saisit que l'url et ou les autres options sont optionnelles et à Null.
        #  puis, selon les infos fournies, il lit le fichier dans l'ordre du code html pour deviner su r la page les infos manquantes.
        #  au passage, il remplit la première séance en fcontion de la date de création,
        #  et qui devine le titre grace à la balise <title>
        #  et la date sortie grace à la balise date blue-link">   https://stackoverflow.com/questions/26294333/parse-french-date-in-python pour parser les dates

        # trouver le titre
        # format : <title>Serre Moi Fort - film 2020 - AlloCiné</title>
        matches = re.findall("<title>(.*?)- film", webpage)
        titre = matches[0]
        print("titre Trouvé : " + titre)
        # titre marche ok

        # trouver la date de sortie
        # format : date blue-link">8 septembre 2021</span> SANS les sauts de ligne
        webpageSansSaut = webpage.replace('\n', " ")
        matches = re.findall("date blue-link\">(.*?)</", webpageSansSaut)
        # dateNonformatee = matches[0]
        dateSortie = dateparser.parse(matches[0], languages=['fr'])
        print("date Trouvée : " + str(dateSortie.date()))

        return Film(titre=titre, allocineUrl=allocineUrl, dateSortie=dateSortie.date())
