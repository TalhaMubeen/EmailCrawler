from time import sleep
from tkinter.messagebox import NO
from typing import Any
import requests
from requests.models import Response
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import platform


class Scrapper:
    """
    Scrapper Class
    """

    def __init__(self, url: str = None, contents: list = [], crawl=False) -> None:
        """Contructor

        Args:
            url (str): [description]. Defaults to None.
            contents (list, optional): Defaults to [].
            crawl (bool): Defaults to False.
        """
        self.telNo = []
        self.url = url
        self.urls = []
        self.contents = contents
        self.urls_flagged = []
        self.scrapContent = []
        self.crawl = crawl

    async def async_clean(self, content):
        soup = BeautifulSoup(content, "html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        cleaned: str = soup.get_text()
        lines: object = (line.strip() for line in cleaned.splitlines())
        chunks: object = (phrase.strip() for line in lines for phrase in line.split("  "))
        return '\n'.join(chunk for chunk in chunks if chunk)

    def getURLs(self) -> list:
        """getURLs function

        Returns:
            list: [description]
        """

        urls: list = []
        content: str = requests.get(self.url).text
        soup = BeautifulSoup(content, "html.parser")
        garbage_extensions = ['.aif','.cda','.mid','.midi','.mp3','.mpa','.ogg',
        '.wav','.wma','.wpl','.7z','.arj','.deb','.pkg','.rar','.rpm','.tar.gz','.z',
        '.zip','.bin','.dmg','.iso','.toast','.vcd','.csv','.dat','.db','.dbf','.log',
        '.mdb','.sav','.sql','.tar','.apk','.bat','.bin','.cgi','.pl','.exe','.gadget',
        '.jar','.py','.wsf','.fnt','.fon','.otf','.ttf','.ai','.bmp','.gif','.ico','.jpeg',
        '.jpg','.png','.ps','.psd','.svg','.tif','.tiff','.asp','.cer','.cfm','.cgi','.pl',
        '.part','.py','.rss','.key','.odp','.pps','.ppt','.pptx','.c','.class','.cpp','.cs',
        '.h','.java','.sh','.swift','.vb','.ods','.xlr','.xls','.xlsx','.bak','.cab','.cfg',
        '.cpl','.cur','.dll','.dmp','.drv','.icns','.ico','.ini','.lnk','.msi','.sys','.tmp',
        '.3g2','.3gp','.avi','.flv','.h264','.m4v','.mkv','.mov','.mp4','.mpg','.mpeg','.rm',
        '.swf','.vob','.wmv','.doc','.docx','.odt','.pdf','.rtf','.tex','.txt','.wks','.wps','.wpd']

        for link in soup.find_all('a'):
            if link.get("href") is not None:
                skip = False
                url = link.get("href")
                for extension in garbage_extensions:
                    if url.endswith(extension) or url.endswith(extension+'/'):
                        skip = True
                        break
                if skip:
                    continue

                if self.url not in url:
                    if "http" not in url and "https" not in url and "mailto:" not in url:
                        if "tel:" in url or "Phone:" in url:
                            if(url not in self.telNo):
                                self.telNo.append(url)
                            else:
                                continue
                        else:    
                            urls.append(self.url + link.get('href'))
                        continue
            urls.append(link.get("href"))
        return urls

    def getContent(self, url:str) -> list:
        try:
            if url is not None:
                header = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0; X11; Linux x86_64) Gecko/20100101 AppleWebKit/537.36 (KHTML, like Gecko) Firefox/66.0 Ubuntu Chromium/78.0.3904.70 Chrome/78.0.3904.70 Safari/537.36",
                    "Accept-Encoding": "*",
                    "Connection": "keep-alive"}
                req: Response = requests.get(url, headers=header)
                self.scrapContent.append(req.text)
        except:
            pass


    async def fetch(self, session, url):
        sleep_time = 0.2
        try:
            if url is not None and len(url) > 0:
                async with session.get(url) as resp:
                    try:
                        if resp.status == 508:
                            sleep_time = 1
                            await asyncio.sleep(sleep_time)
                            self.urls_flagged.append(url)
                        else:
                            text = await resp.text()
                            retContent = await self.async_clean(text)
                            self.scrapContent.append(retContent)
                            await asyncio.sleep(sleep_time)
                    except:
                        pass
        except:
            pass


    async def process_urls(self, urls):
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = [self.fetch(session, url) for url in urls]
            await asyncio.gather(*tasks)

    def getText(self) -> dict:
        """getText function

        Returns:
            dict
        """
        if platform.system()=='Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        urls = self.getURLs()
        sublist_urls = [urls[x:x+16] for x in range(0, len(urls), 16)]
        run = True
        while run:
            for urls_list in sublist_urls:
                asyncio.new_event_loop().run_until_complete (self.process_urls(urls_list)) 
                sleep(5)
            
            if len(self.urls_flagged) > 0:
                sublist_urls.clear()
                sublist_urls = [self.urls_flagged[x:x+8] for x in range(0, len(self.urls_flagged), 8)]
                sleep(30)
            else:
                run = False

        print(self.scrapContent)

        return {"text": self.scrapContent, "urls": urls, "tels":self.telNo}
