import json
from requests.exceptions import MissingSchema
from modules import googlesearch
from modules.scrapper import Scrapper
from modules.info_reader import InfoReader
import re
from urllib.parse import urlsplit, urljoin
import threading

#"./urls_file.txt"
class CrawlerProcessor:

    def __init__(self) -> None:
        self.pendingUrlList = []
        self.thread_list    = []
        self.newUrls        = False

    def addURL(self, url):
        if len(self.thread_list) > 0:
            self.pendingUrlList.append(url)
        else:
            new_thread = threading.Thread(target=self.crawlURL,args=(url,))
            new_thread.start()

    def ProcessUrl(self, url):

        url = url.replace("\n", "")
        print("\n\n")
        print("*" * 50 + "\n" + f"Target: {url}\n" + "*" * 50)

        scrap = Scrapper(url=url)
        content = scrap.getText()
        IR = InfoReader(content=content)
        emails: list = IR.getEmails()
        numbers = IR.getPhoneNumber()

        for num in content["tels"]:
            try:
                if ":" in num:
                    num = re.sub("[^+-0123456789\.]","",num)
                    if len(num) > 8 and len(num) < 20:
                        if(num not in numbers):
                            if "," in num:
                                continue
                            n2 = ''.join(filter(str.isdigit, num))
                            if len(n2) > 8 and len(n2) < 20:
                                numbers.append(num)
            except:
                pass

        sm: list = IR.getSocials()

        out = {
            "URL": url,
            "E-Mails": emails,
            "SocialMedia": sm,
            "Numbers": numbers
        }
        base_url = urlsplit(url).netloc
        outputfile = base_url.replace('.','_')+'.json'
        curr_file = open(f"./output/" + outputfile, "w")
        json.dump(out, curr_file, indent=4)
        curr_file.flush()
        curr_file.close()
        return

    def crawlURL(self, urls):
        urlsDoneFile = open("./urls_file.txt", "a")

        sublist_urls = [urls[x: x + 6] for x in range(0, len(urls), 6)]
        for urls_list in sublist_urls:
            self.thread_list = []
            for url in urls_list:
                new_thread = threading.Thread(target=self.ProcessUrl,args=(url,))
                new_thread.start()
                self.thread_list.append(new_thread)
                urlsDoneFile.write(url + "\n")
                urlsDoneFile.flush()

            for th in self.thread_list:
                th.join()

        # if len(self.pendingUrlList) > 0:
        #     new_thread = threading.Thread(target=self.crawlURL,args=(self.pendingUrlList,))
        #     new_thread.start()


    def searchGoogle(self):
        keywordsList = open("./keywords.txt", "r").read().splitlines()

        for query in keywordsList:
            client = googlesearch.SearchClient(
                query,
                verbosity=4,
                num=10,
                max_search_result_urls_to_return=50,
                minimum_delay_between_paged_results_in_seconds=1,
                http_429_cool_off_time_in_minutes=45,
                http_429_cool_off_factor=1.5,
                googlesearch_manages_http_429s=True,  # Add to manage HTTP 429s.
            )
            client.assign_random_user_agent()

            urls = client.search()
            self.crawlURL(urls)

if __name__ == "__main__":
    processor = CrawlerProcessor()
    processor.searchGoogle()
