import requests
import json
import re
from bs4 import BeautifulSoup as bs

import zipfile
import io

class Subscene:
    """
    Object to interect with subscene.com to download subtitles.
    """

    def __init__(self):

        with open("subscene_languages.json", "r") as f:
            self.languages = json.loads(f.read())

        self.url = "https://subscene.com"
        self.search_results = dict()
        self.selected = dict()

    def search(self, name=str(), choice=None, language=""):
        """
        Search by movie name and outputs movie names registered in the
        subscene database: the function returns search results (partial_url).
        If the users specifies choice and/or language, the function returns
        informations about the search result chosen (choice is the position
        of the selected search result in the list provided by the function 
        with the name argument).

        Args:
            name: name of the movie
            choice: partial_url of the chosen search result
            language: the language of the subtitle
        Retuns (one only):
            (dict): List of subtitle ids with name(s), language and rank
            (list): Search results.
        """


        if self.search_results and isinstance(choice, int):
            partial_url = list(self.search_results.keys())[choice]
            self._available_subtitles(partial_url, language)
            return self.selected
        elif isinstance(choice, int) and not self.search_results:
            raise Exception("Please search by name first")

        name = "+".join(name.split())

        payload = {
                "query":name,
                "l":"",
                }

        url = self.url + "/subtitles/searchbytitle"
        results = requests.post(url, data=payload)
        results = bs(results.text, "lxml")

        search_results = dict()
        titles = results.find_all("div", {"class":"title"})
        for title in titles:
            name = title.find("a").text
            partial_url = title.find("a").attrs["href"].split("/")[-1]

            search_results[partial_url] = name

        self.search_results = search_results

        return list(self.search_results.values())

    def _available_subtitles(self, partial_url, language):
        """
        Takes the partial_url and language provided by the search method and
        returns a dictionnarry objects with informations about available 
        subtitles to download.
        
        Args:
            partial_url (str): partial_url of the search result
            language (str): language filter
        Retuns:
            infos (dict): Available subtitles : ids, names, languages, and ranks.
        """
        url = self.url + "/subtitles/" + partial_url

        if language:
            if not language in self.languages.keys():
                raise Exception("Wrong language")
            language = self.languages[language]

        cookie = {"LanguageFilter":language}
        html = bs(requests.get(url, cookies=cookie).text, "lxml")

        with open("result.html","w") as f:
            f.write(html.prettify())

        subtitles = html.find("tbody").find_all("tr")
        
        reformat = lambda string : " ".join(string.split())

        infos = dict()

        for sub in subtitles:

            try:
                a = sub.find("td", {"class":"a1"}).find("a")
            except:
                continue

            spans = a.find_all("span")

            id = a.attrs["href"].split("/")[-1]
            name = reformat(spans[1].text)
            language = a.attrs["href"].split("/")[-2]
            state = spans[0].attrs["class"][2][:-5]

            if infos.__contains__(id): # multiple names can have the same id
                infos[id][0].append(name)
            else:
                infos[id] = [name], partial_url, language, state

        self.selected.update(infos) 

    def download(self, id):
        """
        Download the srt subtitle with the id of the subtitle. Writes the
        result in a file.
        Args:
            id (str): id of the subtitle to download.
        Returns:
            None
        """

        id = str(id)
        partial_url = self.selected[id][1]
        language = self.selected[id][2]

        url = self.url +  "/subtitles/" + partial_url + "/" + language + "/" + id
        download_link = bs(requests.get(url).text, "lxml")
        download_link = download_link.find("a", {"id":"downloadButton"}).attrs["href"]
        download_link = self.url + download_link

        input_zip = requests.get(download_link).content

        zip = zipfile.ZipFile(io.BytesIO(input_zip))

        for name in zip.namelist():
            if bool(re.search(r"srt$", name)):
                with open(name,"wb") as f:
                    f.write(zip.read(name))

        return True


# How to download subtitles

search = "the lord of the ring"

test = Subscene()

search_results = test.search(name=search)
results = test.search(language="french", choice=0) # We'll take the first search result
id = list(results.keys())[0] # Take the first result provided
test.download(id) # Download the subtitles
