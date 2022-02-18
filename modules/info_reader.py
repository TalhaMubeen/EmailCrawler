import re
import string
from socid_extractor import parse, extract
from typing import List


class InfoReader:
    """
    InfoReader Class
    """

    def __init__(self, content: dict = None, social_path: str = "./socials.txt") -> None:
        """Contructor

        Args:
            content (dict): [description]. Defaults to None.
            social_path (str): [description]. Defaults to "./socials.txt".
        """

        if content is None:
            content: dict = {
                "text": [],
                "urls": []
            }

        self.content: list = content
        self.social_path: str = social_path
        self.res: dict = {
            "phone": "/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,7}$/gm",
            "email": r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        }

    def getPhoneNumber(self) -> list:
        """getPhoneNumber function

        Returns:
            list: [description]
        """
        # Doesnt work that good
        numbers: list = []
        texts: list = self.content["text"]

        for text in texts:
            for n in text.split("\n"):
                if re.match(self.res["phone"], n):
                    for letter in string.ascii_letters:
                        n: object = n.replace(letter, "")
                    numbers.append(n)
                elif ":" in n:
                    n = re.sub("[^+-0123456789.]","",n)
                    if len(n) > 8 and len(n) < 20:
                        if "," in n:
                            continue
                        if(n not in numbers):
                            n2 = ''.join(filter(str.isdigit, n))
                            if len(n2) > 8 and len(n2) < 20:
                                numbers.append(n)

        return list(dict.fromkeys(numbers))

    def getEmails(self) -> list:
        """getEmails Function

        Returns:
            list: [description]
        """
        emails: list = []
        texts: object = self.content["text"]

        for text in texts:
            for s in text.split("\n"):
                s = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', s, re.I))
                skip_email = False
                for email in s:
                    if "@" in email:
                        print(email)
                    skip_email = False
                    for checker in ['jpg','jpeg','png']:
                        if email.endswith(checker):
                            skip_email = True
                            break
                    
                    if not skip_email:
                        emails.append(email)

        for link in self.content["urls"]:
            if link is None:
                continue
            s = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', link, re.I))
            skip_email = False
            for email in s:
                skip_email = False
                for checker in ['jpg','jpeg','png']:
                    if email.endswith(checker):
                        skip_email = True
                        break
                
                if not skip_email:
                    emails.append(email)

        return list(dict.fromkeys(emails))

    def getSocials(self) -> list:
        """getSocials Function

        Returns:
            list: [description]
        """
        sm_accounts: list = []
        socials: object = open(self.social_path, "r+").readlines()

        for url in self.content["urls"]:
            for s in socials:
                if url is None:
                    continue
                if s.replace("\n", "").lower() in url.lower():
                    sm_accounts.append(url)
        return list(dict.fromkeys(sm_accounts))

    def getSocialsInfo(self) -> List[dict]:
        urls = self.getSocials()
        sm_info = []
        for url in urls:
            text, _ = parse(url)
            sm_info.append({"url": url, "info": extract(text)})
        return sm_info
