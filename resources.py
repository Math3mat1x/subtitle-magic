import requests
import json
from bs4 import BeautifulSoup as bs

class Subscene:
    def __init__(self):
        with open("subscene_languages.json", "r") as f:
            self.languages = json.loads(f.read())
        self.url = "https://subscene.com/"

    def search(self, name, language=""):
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

            search_results[name] = partial_url

        return search_results

    def _available_subtitles(self, name, language):

        url = self.url + "subtitles/" + name

        if language:
            if not language in self.languages.keys():
                raise Exception("Wrong language")
            language = self.languages[language]

        cookie = {"LanguageFilter":language}
        html = bs(requests.get(url, cookies=cookie).text, "lxml")

        subtitles = html.find("tbody").find_all("tr")
        
        reformat = lambda string : " ".join(string.split())

        infos = dict()

        for sub in subtitles:
            a = sub.find("td", {"class":"a1"}).find("a")
            spans = a.find_all("span")

            id = a.attrs["href"].split("/")[-1]
            name = reformat(spans[1].text)
            language = a.attrs["href"].split("/")[-2]
            state = spans[0].attrs["class"][2][:-5]

            if infos.__contains__(id): # multiple names can have the same id
                infos[id][0].append(name)
            else:
                infos[id] = [name], language, state

        return infos


test = Subscene()

print(test.search("the lord of the ring","french"))

# https://subscene.com/subtitles/the-lord-of-the-rings-the-fellowship-of-the-ring/french/1314014
