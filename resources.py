import requests
import json
from bs4 import BeautifulSoup as bs

class OpenSubtitles:

    def __init__(self):
        self.url = "https://www.opensubtitles.org/"

        with open("languages.json", "r") as f:
            self.languages = json.loads(f.read())

    def _search_php(self, search, lang):
        """Search for subtitles ids from a movie title using the suggestion
        private API (safest solution).

        Args:
            search (str): the movie title
            lang (str): language keycode (see language.json)
        Returns:
            result: a list of matching results containing names and ids or
            returns None if nothing is found.
        """

        data = {
                "format":"json3",
                "MovieName":search,
                "SubLanguageID":lang
                }

        try:
            result = requests.get("https://opensubtitles.org/libs/suggest.php", params=data)
            result = json.loads(result.text)
        except:
            result = None

        return result

    def _search_html(self, search, lang):
        """Search for subtitles ids from a movie title by analyzing the html
        response from the website.

        Args:
            search (str): the movie title
            lang (str): language keycode (see language.json)
        Returns:
            result: a list of matching results containing names and ids or
            returns None if nothing is found.
        """

        search = "+".join(search.split())
        url = self.url + "search2/sublanguageid-" + lang + "/moviename-" + search
        html = requests.get(url)
        html = bs(html.text, "lxml")

        trs = html.find("table", {"id":"search_results"}).find("tbody").find_all("tr")

        movies = list()

        for tr in trs:
            try:
                if "name" in tr.get("id"):
                    id = tr.get("id")[4:]
                    name, year = tuple(tr.find("strong").find("a").text.split("\n"))
                    year = year[1:-1]
                    movies.append({
                        "name":name,
                        "year":year,
                        "id":id,
                    })

            except TypeError:
                    pass

        if movies:
            return movies
        else:
            return None


    def search(self, search, lang="eng"):
        """
        Search for informations (ids) about a movie

        Args:
            search (str): the movie title
            lang (str) (optional): language keycode (see language.json)
        Returns:
            result (list): matching information about the title.
        """

        if not lang in self.languages.keys():
            raise Exception("Wrong country code.")

        infos = self._search_html(search, lang)
        if not infos:
            infos = self._search_php(search, lang)
        if not infos:
            raise Exception("Unable to fetch any information about this movie.")

        return infos
