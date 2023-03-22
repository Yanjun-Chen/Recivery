"""
- Recommend or search food
- Provide recipe

"""

import os
import requests
import lxml.etree as etree
import re
import json
import pickle as pkl


class FoodCom:
    def __init__(self, online_mode: bool, retry: int = 3):
        """
        :param online_mode:
        :param retry: time for retry when bad network
        """
        self.postcode = 15213
        self.rank_page_no = 0
        self.recipe_records = {}
        self.search_key_words = "grape salad"
        self.retry = retry
        self.online_mode = online_mode
        self.dish_id = None
        self.ingredients = []

    def __display_rank_page(self, info: dict) -> str:
        """
        convert raw dict rank page to formatted string for display
        :param info: info dict by rank page
        :return:formatted string for display
        """
        out_s = "------------recommendation page {}------------\n".format(
            self.rank_page_no)
        if info["available"]:
            for k, v in info["recipes"].items():
                out_s += "%-6s : %s\n" % (v, k)
        else:
            out_s += "bad network\n"
        return out_s

    def rank_page(self, rank_page_no: int = None) -> dict:
        """
        get one page of top ranked recipes (ranked by trending)
        :param rank_page_no: page_number
        :return: info["available"] (bool) means network status, info["recipes"] is the ranked recipes result
        """
        if self.online_mode:
            return self.online_rank_page(rank_page_no)
        else:
            return self.offline_rank_page(rank_page_no)

    def offline_rank_page(self, rank_page_no: int = None) -> dict:
        """
        get one page of top ranked recipes (ranked by trending)
        :param rank_page_no: page_number
        :return: info["available"] (bool) means network status, info["recipes"] is the ranked recipes result
        """
        if rank_page_no is None:
            # go to the next page
            self.rank_page_no += 1
        else:
            # go to the input page
            self.rank_page_no = rank_page_no
        info = {"available": True}
        try:
            with open("./foodComOfflineCache/recommend/data/" + str(self.rank_page_no) + ".pkl", "rb") as f:
                info["recipes"] = pkl.load(f)
            with open("./foodComOfflineCache/recommend/records/" + str(self.rank_page_no) + ".pkl", "rb") as f:
                records = pkl.load(f)
            self.recipe_records.update(records)
        except:
            info["recipes"] = {}
        return info, self.__display_rank_page(info)

    def online_rank_page(self, rank_page_no: int = None) -> dict:
        """
        get one page of top ranked recipes (ranked by trending)
        :param rank_page_no: page_number
        :return: info["available"] (bool) means network status, info["recipes"] is the ranked recipes result
        """
        if rank_page_no is None:
            # go to the next page
            self.rank_page_no += 1
        else:
            # go to the input page
            self.rank_page_no = rank_page_no

        # the website use 2 different urls when getting ranked recipes on the first page and on other pages
        # the first page
        if self.rank_page_no == 1:
            headers = {
                'authority': 'www.food.com',
                'method': 'GET',
                'path': '/recipe/all/trending',
                'scheme': 'https',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cookie': '_pbjs_userid_consent_data=3524755945110770; usprivacy=1YNY; gig_bootstrap_3_-YpMMN5PDDnj1ri65ssss6K9Hq9y-y13U1TnjyjKSIxXJOuvE81IhyaP-BOkmb0v=_gigya_ver4; OneTrustWPCCPAGoogleOptOut=false; __gads=ID=5712bf5d1c1dfe1b:T=1668261613:S=ALNI_Maan8VDrSBOTvWFgZgxpdUOXThRfQ; _gcl_au=1.1.1430657068.1668261619; _lr_env_src_ats=false; _bs=cb83858f-1a45-65f2-aa4c-8d4b9105ef53; s_nr=1668262402323; krg_uid=%7B%22v%22%3A%7B%22clientId%22%3A%2241dfc787-4780-413a-850a-e101f150f94a%22%2C%22userId%22%3A%22523fbff4-e717-018a-111b-0dba48050e01%22%2C%22optOut%22%3Afalse%7D%7D; krg_crb=%7B%22v%22%3A%22eyJjbGllbnRJZCI6IjQxZGZjNzg3LTQ3ODAtNDEzYS04NTBhLWUxMDFmMTUwZjk0YSIsInRkSUQiOiIyODUxMzZkYi0xODA0LTQ2YjMtYmE2Yi0yYjhmYjFlMDUxZWQiLCJsZXhJZCI6IjUyM2ZiZmY0LWU3MTctMDE4YS0xMTFiLTBkYmE0ODA1MGUwMSIsInN5bmNJZHMiOnsiMjMiOiI4MTA2NjJkZi01ZTAzLTQ2MDAtYjI5YS02ZGY5ODJjM2IyYzciLCIyNSI6IjI4NTEzNmRiLTE4MDQtNDZiMy1iYTZiLTJiOGZiMWUwNTFlZCIsIjI5IjoiNjY0NjEwNzU4OTI4NTU1NzY4NyIsIjc0IjoiQ0FFU0VNcFFMMmtQeklBZnQxLWx0a2pscUt3IiwiOTciOiJ5LUZ0VXNFMmhFMnB1aE1aWmdjV0NNUzc0QTlGSG1NQkFGZnRZLX5BIiwiMl8xNiI6IkNBRVNFTXBRTDJrUHpJQWZ0MS1sdGtqbHFLdyIsIjJfODAiOiI4MTA2NjJkZi01ZTAzLTQ2MDAtYjI5YS02ZGY5ODJjM2IyYzciLCIyXzkzIjoiMjg1MTM2ZGItMTgwNC00NmIzLWJhNmItMmI4ZmIxZTA1MWVkIn0sImt0Y0lkIjoiYTM1OTMwMGUtZDk3Yi0wMmFhLTU1YmQtOGI4ZDNiNGQ5NmE0IiwiZXhwaXJlVGltZSI6MTY2ODQwMDI2Mzc2MSwibGFzdFN5bmNlZEF0IjoxNjY4MzEzODYzNzYxLCJwYWdlVmlld0lkIjoiIiwicGFnZVZpZXdUaW1lc3RhbXAiOjE2NjgzMTM4NTc1ODIsInBhZ2VWaWV3VXJsIjoiaHR0cHM6Ly93d3cuZm9vZC5jb20vc2VhcmNoLyIsInVzcCI6IjFZTlkifQ%3D%3D%22%7D; gig_canary=true; cto_bundle=quZAZF9KcXc2aUliRkNtUXZrUWVVWlp5a2Z3SnBySSUyQiUyQmtDTVV0a3pma3YwWU9vRXhMT3IwZ0tTYTFGQ3FlSnJBJTJCQXQlMkJTcW1JMkNsNjVDdE1oMkJFOHJMWE9ZJTJGVlo2VGs5UGVxJTJCSzg5TkV0aVU1NWRCJTJGV0dFRlhYeFE1TnJXTGNnJTJGNCUyRnVZZ2NRMzRKY2tXSzRhN0R4dmRPN1ElM0QlM0Q; _lr_geo_location=HK; RT="z=1&dm=food.com&si=42b3c2a2-6d55-4832-833d-f4e67e784fba&ss=lah07ibi&sl=0&tt=0&bcn=%2F%2F684d0d4a.akstat.io%2F"; AMCVS_BC501253513148ED0A490D45%40AdobeOrg=1; AMCV_BC501253513148ED0A490D45%40AdobeOrg=-2121179033%7CMCIDTS%7C19311%7CMCMID%7C25059505012901603493820485581044046737%7CMCAAMLH-1669126147%7C11%7CMCAAMB-1669126147%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1668528547s%7CNONE%7CvVersion%7C5.3.0; s_cc=true; gig_canary=false; gig_canary_ver=13455-3-27808650; __gpi=UID=000008f8203a002e:T=1668261613:RT=1668521358:S=ALNI_MY-Z7sbEsavTkVzAqfKD_lmXKfU9w; s_sq=%5B%5BB%5D%5D; OptanonConsent=isIABGlobal=false&datestamp=Tue+Nov+15+2022+22%3A09%3A53+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202209.2.0&hosts=&consentId=7dff4759-a3a6-4f33-97d0-c97f4392e309&interactionCount=1&landingPath=NotLandingPage&groups=BG1673%3A1%2CC0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0005%3A1%2CC0004%3A1&AwaitingReconsent=false&geolocation=HK%3B; OptanonAlertBoxClosed=2022-11-15T14:09:53.037Z',
                'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'
            }
            suc = False
            for i in range(self.retry):
                try:
                    r = requests.get(
                        url="https://www.food.com/recipe/all/trending", headers=headers)
                    if r.status_code == requests.status_codes.codes.ok:
                        suc = True
                        break
                except:
                    continue
            if suc and r.status_code == requests.status_codes.codes.ok:
                s = r.text
                pattern = r'"https://www\.food\.com/recipe/[a-z0-9\-]+-[0-9]+"'
                recipes_urls = set(re.findall(pattern=pattern, string=s))
                recipes_urls = {i[1:-1] for i in recipes_urls}
                info = {"available": True}
                info["recipes"] = {}
                for url in recipes_urls:
                    tmp = url.split("/")[-1].split("-")
                    recipe_name = tmp[:-1]
                    recipe_name = "".join([_ + " " for _ in recipe_name])[:-1]
                    recipe_id = tmp[-1]
                    info["recipes"][recipe_name] = recipe_id
                    self.recipe_records[recipe_id] = url
                r.close()
            else:
                info = {"available": False}

        # other pages
        else:
            headers = {
                "authority": r"api.food.com",
                "method": r"GET",
                "path": r"/services/mobile/fdc/search/sectionfront?pn={page_number}&recordType=Recipe&sortBy=trending&collectionId=17".format(
                    page_number=self.rank_page_no),
                "scheme": r"https",
                "accept": r"application/json, text/javascript, */*; q=0.01",
                "accept-encoding": r"gzip, deflate, br",
                "accept-language": r"zh-CN,zh;q=0.9",
                "content-type": r"application/json",
                "origin": r"https://www.food.com",
                "referer": r"https://www.food.com/",
                "sec-ch-ua": r'"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                "sec-ch-ua-mobile": r"?0",
                "sec-ch-ua-platform": r'"macOS"',
                "sec-fetch-dest": r"empty",
                "sec-fetch-mode": r"cors",
                "sec-fetch-site": r"same-site",
                "user-agent": r"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36"
            }
            url = "https://api.food.com/services/mobile/fdc/search/sectionfront?pn={page_number}&recordType=Recipe&sortBy=trending&collectionId=17".format(
                page_number=self.rank_page_no)
            suc = False
            for i in range(self.retry):
                try:
                    r = requests.get(url, headers=headers)
                    if r.status_code == requests.status_codes.codes.ok:
                        suc = True
                        break
                except:
                    continue
            if suc and r.status_code == requests.status_codes.codes.ok:
                recipes_urls_new_page = []
                for _ in r.json()["response"]["results"]:
                    try:
                        if _["recordType"] == "Recipe":
                            recipes_urls_new_page.append(_["record_url"])
                    except:
                        continue
                info = {"available": True}
                info["recipes"] = {}
                for url in set(recipes_urls_new_page):
                    tmp = url.split("/")[-1].split("-")
                    recipe_name = tmp[:-1]
                    recipe_name = "".join([_ + " " for _ in recipe_name])[:-1]
                    recipe_id = tmp[-1]
                    info["recipes"][recipe_name] = recipe_id
                    self.recipe_records[recipe_id] = url
                r.close()
            else:
                info = {"available": False}

        return info, self.__display_rank_page(info)

    def __display_search(self, info: dict) -> str:
        """
        convert raw dict search page to formatted string for display
        :param info: info dict by rank page
        :return:formatted string for display
        """
        out_s = "------------search page {}------------\n".format(
            self.search_page)
        if info["available"]:
            if len(info["recipes"]) == 0:
                out_s += "no result\n"
            for k, v in info["recipes"].items():
                # out_s += "%-6s : %s, %s minutes, %s steps, rated %s/5 by %s people\n" % (
                #     v["recipe_id"], v["title"], v["time_by_minutes"], v["num_steps"], v["rating"], v["num_ratings"])
                out_s += "%-6s : %s\n" % (
                    v["recipe_id"], v["title"])
        else:
            out_s += "bad network\n"
        return out_s

    def search(self, key_words: str = None) -> dict:
        """
        search for recipes according to any keywords input and get the one page of searching results
        :param key_words: keywords related the intended recipe
        :return: info["available"] (bool) means network status, info["recipes"] is the searching results
        """
        if self.online_mode:
            return self.online_search(key_words)
        else:
            return self.offline_search(key_words)

    def offline_search(self, key_words: str = None) -> dict:
        """
        search for recipes according to any keywords input and get the one page of searching results
        :param key_words: keywords related the intended recipe
        :return: info["available"] (bool) means network status, info["recipes"] is the searching results
        """
        if key_words is None:
            self.search_page += 1
        else:
            self.search_page = 1
            self.search_key_words = key_words
        if self.search_page == 1:
            self.recipe_pool = [name[:-4].replace("_", " ").lower() for name in
                                os.listdir("./foodComOfflineCache/search/data")]

        if len(self.recipe_pool) == 0:
            stop_search = True
        else:
            stop_search = False
        info = {"available": True, "recipes": {}}
        data = info["recipes"]
        data_count = 0
        match = self.search_key_words.split(" ")
        while not stop_search:
            name = self.recipe_pool.pop()
            if any([_ in name for _ in match]):
                with open("./foodComOfflineCache/search/data/" + name.replace(" ", "_") + ".pkl", "rb") as f:
                    data.update(pkl.load(f))
                with open("./foodComOfflineCache/search/records/" + name.replace(" ", "_") + ".pkl", "rb") as f:
                    self.recipe_records.update(pkl.load(f))
                data_count += 1
            if len(self.recipe_pool) == 0 or data_count == 10:
                stop_search = True
        return info, self.__display_search(info)

    def online_search(self, key_words: str = None) -> dict:
        """
        search for recipes according to any keywords input and get the one page of searching results
        :param key_words: keywords related the intended recipe
        :return: info["available"] (bool) means network status, info["recipes"] is the searching results
        """
        if key_words is None:
            self.search_page += 1
        else:
            self.search_page = 1
            self.search_key_words = key_words
        headers = {
            "authority": "api.food.com",
            "method": "POST",
            "path": "/external/v1/nlp/search",
            "scheme": "https",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/json",
            "origin": "https://www.food.com",
            "referer": "https://www.food.com/",
            "sec-ch-ua": '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36"
        }
        payload = {"contexts": [],
                   "searchTerm": self.search_key_words, "pn": self.search_page}
        data = json.dumps(payload)
        headers["content-length"] = str(len(data) - 5)
        suc = False
        for i in range(self.retry):
            try:
                r = requests.post(url="https://api.food.com/external/v1/nlp/search", headers=headers,
                                  data=json.dumps(payload))
                if r.status_code == requests.status_codes.codes.ok:
                    suc = True
                    break
            except:
                continue
        info = {}
        if suc and r.status_code == requests.status_codes.codes.ok:
            response_dict = r.json()
            r.close()
            info["available"] = True
            info["recipes"] = {}
            available_count = int(response_dict["response"]["totalResultsCount"]) - \
                int(response_dict["response"]["parameters"]["offset"])
            if available_count > 0:
                for record in response_dict["response"]["results"]:
                    if record["recordType"] == "Recipe":
                        try:
                            url = record["record_url"]
                            tmp = url.split("/")[-1].split("-")
                            recipe_name = tmp[:-1]
                            recipe_name = "".join(
                                [_ + " " for _ in recipe_name])[:-1]
                            recipe_id = tmp[-1]
                            tmp_recipe = {
                                "title": record["main_title"],
                                "time_by_minutes": record["recipe_totaltime"],
                                "num_steps": record["num_steps"],
                                "num_ratings": record["main_num_ratings"],
                                "rating": record["main_rating"],
                                "recipe_id": recipe_id
                            }
                            self.recipe_records[recipe_id] = url
                            info["recipes"][recipe_name] = tmp_recipe
                        except:
                            continue
        else:
            info["available"] = False
        return info, self.__display_search(info)

    def __display_one_recipe_detail(self, info: dict) -> str:
        """
        convert raw dict search page to formatted string for display
        :param info: info dict by rank page
        :return:formatted string for display
        """
        if info["legal"]:
            if info["recipe_available"]:
                data = info["data"]
                output_s = ""
                output_s += "-------------------------"
                output_s += info["data"]["title"]
                output_s += "-------------------------"
                output_s += "\n"
                output_s += "recipe id : "
                output_s += data["id"]
                output_s += "\n"
                output_s += "author : "
                output_s += data["author"]
                output_s += "\n"
                output_s += "description : "
                output_s += data["description"]
                output_s += "\n"
                output_s += "cooking time : "
                output_s += data["time"]
                output_s += "\n"
                output_s += "ingredients : "
                output_s += data["ingredients"]["kinds"]
                output_s += "\n"
                output_s += "----------"
                output_s += "directions"
                output_s += "----------"
                output_s += "\n"
                for di, d in enumerate(data["directions"]):
                    output_s += "%-2d %s\n" % (di + 1, d)
                output_s += "----------"
                output_s += "ingredients"
                output_s += "----------"
                output_s += "\n"
                for igd in data["ingredients"]["detail"]:
                    output_s += "%-8s %s\n" % (igd["amt"], igd["detail"])
                output_s += "----------"
                output_s += "nutrition table"
                output_s += "----------"
                output_s += "\n"
                output_s += "calories %.2f kcal\n" % data["nutrition"]["calories"]
                output_s += "fat %.2f g\n" % data["nutrition"]["fatContent"]
                output_s += "\t saturated fat %.2f g\n" % data["nutrition"]["saturatedFatContent"]
                output_s += "cholesterol %.2f mg\n" % data["nutrition"]["cholesterolContent"]
                output_s += "sodium %.2f mg\n" % data["nutrition"]["sodiumContent"]
                output_s += "carbohydrate %.2f g\n" % data["nutrition"]["carbohydrateContent"]
                output_s += "\t fiber %.2f g\n" % data["nutrition"]["fiberContent"]
                output_s += "\t sugar %.2f g\n" % data["nutrition"]["sugarContent"]
                output_s += "protein %.2f g\n" % data["nutrition"]["proteinContent"]
                if info["price available"]:
                    output_s += "----------"
                    output_s += "purchase recommendation"
                    output_s += "----------"
                    output_s += "\n"
                    if data["price"] is None:
                        output_s += "estimated cost per serve unavailable\n"
                    else:
                        output_s += 'estimated cost per serve %.2f $\n' % (
                            data["price"] / 100)
                    if data["product_list"] is None or len(data["product_list"]) == 0:
                        output_s += "recommended product list unavailable\n"
                    else:
                        output_s += "recommended product list :\n"
                        for s in data["product_list"]:
                            output_s += "\t"
                            output_s += s
                            output_s += "\n"
                else:
                    output_s += "purchase data unavailable\n"
            else:
                output_s = "bad network"
        else:
            output_s = "unknown recipe id"
        return output_s

    def one_recipe_detail(self, recipe_id: str) -> dict:
        """
        get detailed information about one recipe
        :param recipe_id:
        :return: dict recipe info
        """
        if self.online_mode:
            return self.online_one_recipe_detail(recipe_id)
        else:
            return self.offline_one_recipe_detail(recipe_id)

    def offline_one_recipe_detail(self, recipe_id: str) -> dict:
        """
        get detailed information about one recipe
        :param recipe_id:
        :return: dict recipe info
        """
        self.dish_id = None
        self.ingredients = []
        info = {}
        if recipe_id in self.recipe_records:
            with open("./foodComOfflineCache/detail/" + recipe_id + ".pkl", "rb") as f:
                info = pkl.load(f)
            self.dish_id = recipe_id
            self.ingredients = info["data"]["product_list"]
        else:
            info["legal"] = False
        return info, self.__display_one_recipe_detail(info)

    def online_one_recipe_detail(self, recipe_id: str) -> dict:
        """
        get detailed information about one recipe
        :param recipe_id:
        :return: dict recipe info
        """
        self.dish_id = None
        self.ingredients = []
        info = {}
        if recipe_id in self.recipe_records:
            info["legal"] = True
            # get basic recipe information
            url = self.recipe_records[recipe_id]
            headers = {
                "authority": r'www.food.com',
                "method": r'GET',
                "path": '/recipe/{}?units=metric&scale=1'.format(url.split("/")[-1]),
                "scheme": r'https',
                "accept": r'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                "accept-encoding": r'gzip, deflate, br',
                "accept-language": r'zh-CN,zh;q=0.9',
                "cookie": r'_pbjs_userid_consent_data=3524755945110770; usprivacy=1YNY; gig_bootstrap_3_-YpMMN5PDDnj1ri65ssss6K9Hq9y-y13U1TnjyjKSIxXJOuvE81IhyaP-BOkmb0v=_gigya_ver4; OneTrustWPCCPAGoogleOptOut=false; __gads=ID=5712bf5d1c1dfe1b:T=1668261613:S=ALNI_Maan8VDrSBOTvWFgZgxpdUOXThRfQ; _gcl_au=1.1.1430657068.1668261619; _lr_env_src_ats=false; _bs=cb83858f-1a45-65f2-aa4c-8d4b9105ef53; s_nr=1668262402323; krg_uid=%7B%22v%22%3A%7B%22clientId%22%3A%2241dfc787-4780-413a-850a-e101f150f94a%22%2C%22userId%22%3A%22523fbff4-e717-018a-111b-0dba48050e01%22%2C%22optOut%22%3Afalse%7D%7D; krg_crb=%7B%22v%22%3A%22eyJjbGllbnRJZCI6IjQxZGZjNzg3LTQ3ODAtNDEzYS04NTBhLWUxMDFmMTUwZjk0YSIsInRkSUQiOiIyODUxMzZkYi0xODA0LTQ2YjMtYmE2Yi0yYjhmYjFlMDUxZWQiLCJsZXhJZCI6IjUyM2ZiZmY0LWU3MTctMDE4YS0xMTFiLTBkYmE0ODA1MGUwMSIsInN5bmNJZHMiOnsiMjMiOiI4MTA2NjJkZi01ZTAzLTQ2MDAtYjI5YS02ZGY5ODJjM2IyYzciLCIyNSI6IjI4NTEzNmRiLTE4MDQtNDZiMy1iYTZiLTJiOGZiMWUwNTFlZCIsIjI5IjoiNjY0NjEwNzU4OTI4NTU1NzY4NyIsIjc0IjoiQ0FFU0VNcFFMMmtQeklBZnQxLWx0a2pscUt3IiwiOTciOiJ5LUZ0VXNFMmhFMnB1aE1aWmdjV0NNUzc0QTlGSG1NQkFGZnRZLX5BIiwiMl8xNiI6IkNBRVNFTXBRTDJrUHpJQWZ0MS1sdGtqbHFLdyIsIjJfODAiOiI4MTA2NjJkZi01ZTAzLTQ2MDAtYjI5YS02ZGY5ODJjM2IyYzciLCIyXzkzIjoiMjg1MTM2ZGItMTgwNC00NmIzLWJhNmItMmI4ZmIxZTA1MWVkIn0sImt0Y0lkIjoiYTM1OTMwMGUtZDk3Yi0wMmFhLTU1YmQtOGI4ZDNiNGQ5NmE0IiwiZXhwaXJlVGltZSI6MTY2ODQwMDI2Mzc2MSwibGFzdFN5bmNlZEF0IjoxNjY4MzEzODYzNzYxLCJwYWdlVmlld0lkIjoiIiwicGFnZVZpZXdUaW1lc3RhbXAiOjE2NjgzMTM4NTc1ODIsInBhZ2VWaWV3VXJsIjoiaHR0cHM6Ly93d3cuZm9vZC5jb20vc2VhcmNoLyIsInVzcCI6IjFZTlkifQ%3D%3D%22%7D; gig_canary=true; cto_bundle=quZAZF9KcXc2aUliRkNtUXZrUWVVWlp5a2Z3SnBySSUyQiUyQmtDTVV0a3pma3YwWU9vRXhMT3IwZ0tTYTFGQ3FlSnJBJTJCQXQlMkJTcW1JMkNsNjVDdE1oMkJFOHJMWE9ZJTJGVlo2VGs5UGVxJTJCSzg5TkV0aVU1NWRCJTJGV0dFRlhYeFE1TnJXTGNnJTJGNCUyRnVZZ2NRMzRKY2tXSzRhN0R4dmRPN1ElM0QlM0Q; _lr_geo_location=HK; OptanonConsent=isIABGlobal=false&datestamp=Tue+Nov+15+2022+01%3A05%3A40+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202209.2.0&hosts=&consentId=7dff4759-a3a6-4f33-97d0-c97f4392e309&interactionCount=1&landingPath=NotLandingPage&groups=BG1673%3A1%2CC0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0005%3A1%2CC0004%3A1&AwaitingReconsent=false&geolocation=HK%3B; OptanonAlertBoxClosed=2022-11-14T17:05:40.327Z; RT="z=1&dm=food.com&si=42b3c2a2-6d55-4832-833d-f4e67e784fba&ss=lah07ibi&sl=0&tt=0&bcn=%2F%2F684d0d4a.akstat.io%2F"; AMCVS_BC501253513148ED0A490D45%40AdobeOrg=1; AMCV_BC501253513148ED0A490D45%40AdobeOrg=-2121179033%7CMCIDTS%7C19311%7CMCMID%7C25059505012901603493820485581044046737%7CMCAAMLH-1669126147%7C11%7CMCAAMB-1669126147%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1668528547s%7CNONE%7CvVersion%7C5.3.0; s_cc=true; gig_canary=false; gig_canary_ver=13455-3-27808650; __gpi=UID=000008f8203a002e:T=1668261613:RT=1668521358:S=ALNI_MY-Z7sbEsavTkVzAqfKD_lmXKfU9w; s_sq=%5B%5BB%5D%5D',
                "sec-ch-ua": r'"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                "sec-ch-ua-mobile": r'?1',
                "sec-ch-ua-platform": r'"Android"',
                "sec-fetch-dest": r'document',
                "sec-fetch-mode": r'navigate',
                "sec-fetch-site": r'none',
                "sec-fetch-user": r'?1',
                "upgrade-insecure-requests": r'1',
                "user-agent": r'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'
            }
            suc = False
            for i in range(self.retry):
                try:
                    r = requests.get(
                        url + r'?units=metric&scale=1', headers=headers)
                    if r.status_code == requests.status_codes.codes.ok:
                        suc = True
                        break
                except:
                    continue
            if suc and r.status_code == requests.status_codes.codes.ok:
                try:
                    info["recipe_available"] = True
                    info["data"] = {}
                    data = info["data"]

                    # recipe id
                    data["id"] = recipe_id
                    html = etree.HTML(r.text)
                    r.close()

                    # title
                    for div in html.xpath('//*[@id="recipe"]/div'):
                        if div.get("class").startswith("layout__item title svelte-"):
                            break
                    assert div.get("class").startswith(
                        "layout__item title svelte-")
                    data["title"] = div.xpath('./h1/text()')[0]

                    # author & description
                    try:
                        for div in html.xpath('//*[@id="recipe"]/div'):
                            if div.get("class").startswith("layout__item author-description svelte-"):
                                break
                        assert div.get("class").startswith(
                            "layout__item author-description svelte-")
                        for div in div.xpath('./div'):
                            if div.get("class").startswith("author-description svelte-"):
                                break
                        assert div.get("class").startswith(
                            "author-description svelte-")
                        author_description = div
                        # author
                        try:
                            for div in author_description.xpath('div'):
                                if div.get("class").startswith("author svelte-"):
                                    break
                            assert div.get("class").startswith(
                                "author svelte-")
                            for div in div.xpath('div'):
                                if div.get("class").startswith("byline svelte"):
                                    break
                            assert div.get("class").startswith("byline svelte")
                            author = div
                            assert author.text.replace(" ", "").replace(
                                "\n", "") == 'Submittedby'
                            data["author"] = author.xpath('./a/text()')[0]
                        except:
                            data["author"] = "unknown"
                        # description
                        try:
                            div = author_description.xpath(
                                './div[@class="recipe-description paragraph"]')[0]
                            for div in div.xpath('./div'):
                                if div.get("class").startswith("text-truncate svelte-"):
                                    break
                            assert div.get("class").startswith(
                                "text-truncate svelte-")
                            for div in div.xpath('./div'):
                                s = div.get("class")
                                if s.startswith("text svelte-") and s.endswith(" truncated"):
                                    break
                            assert s.startswith(
                                "text svelte-") and s.endswith(" truncated")
                            data["description"] = "".join([x + " " for x in
                                                           "".join([_ + " " for _ in div.xpath('./text()')]).replace(
                                                               "\n",
                                                               " ").split(
                                                               " ") if len(x) > 0])[:-1]
                        except:
                            data["description"] = "..."
                    except:
                        data["author"] = "unknown"
                        data["description"] = "..."

                    # cooking time & kinds of ingredients
                    has_time = False
                    has_kinds = False
                    data["ingredients"] = {}
                    ingredients = data["ingredients"]
                    try:
                        for div in html.xpath('//*[@id="recipe"]/div'):
                            if div.get("class").startswith("layout__item details svelte-"):
                                break
                        assert div.get("class").startswith(
                            "layout__item details svelte-")
                        for div in div.xpath('./div'):
                            if div.get("class").startswith("facts svelte-"):
                                break
                        assert div.get("class").startswith("facts svelte-")
                        for dl in div.xpath('./dl'):
                            if dl.get("class").startswith("svelte-"):
                                break
                        assert dl.get("class").startswith("svelte-")
                        div_list = []
                        for div in dl.xpath('./div'):
                            if div.get("class").startswith("facts__item svelte-"):
                                div_list.append(div)
                        assert len(div_list) > 0
                        for div in div_list:
                            prefix = div.xpath("./dt/text()")[0]
                            if prefix == 'Ready In:':  # cooking time
                                data["time"] = div.xpath("./dd/text()")[0]
                                has_time = True
                            elif prefix == 'Ingredients:':  # kinds
                                ingredients["kinds"] = div.xpath(
                                    "./dd/text()")[0].replace(" ", "").replace("\n", "")
                                has_kinds = True
                        if not has_time:
                            data["time"] = "unknown"
                        if not has_kinds:
                            ingredients["kinds"] = "unknown"
                    except:
                        data["time"] = "unknown"
                        ingredients["kinds"] = "unknown"

                    # ingredient list dedtail
                    for section in html.xpath('//*[@id="recipe"]/section'):
                        if section.get("class").startswith("layout__item ingredients svelte-"):
                            break
                    assert section.get("class").startswith(
                        "layout__item ingredients svelte-")
                    for ul in section.xpath('./ul'):
                        if ul.get("class").startswith("ingredient-list svelte-"):
                            break
                    assert ul.get("class").startswith(
                        "ingredient-list svelte-")
                    igd_all = ul.xpath('./li')
                    igd_all_detail = []
                    for li in igd_all:
                        try:
                            amt = [_.xpath('./text()') for _ in li.xpath("./span") if
                                   _.get("class").startswith("ingredient-quantity svelte-")][0]
                            amt = "".join(amt)
                            if float(amt) == 0:
                                amt = ""
                            igd_detail = "".join(
                                ["".join([s + " " for s in x.replace("\n", " ").split(" ") if len(s) > 0]) for x in
                                 [_.itertext() for _ in li.xpath("./span") if
                                  _.get("class").startswith("ingredient-text svelte-")][0]])[:-1]
                            igd_all_detail.append(
                                {"amt": amt, "detail": igd_detail})
                        except:
                            continue
                    ingredients["detail"] = igd_all_detail

                    # cooking directions
                    section = [_ for _ in html.xpath('//*[@id="recipe"]/section') if
                               _.get("class").startswith("layout__item directions svelte-")][0]
                    ul = [_ for _ in section.xpath(
                        './ul') if _.get("class").startswith("direction-list svelte-")][0]
                    data["directions"] = [_.text.replace("\n", " ").replace("\t", " ") for _ in ul.xpath('./li') if
                                          _.get("class").startswith("direction svelte-")]

                    # get nutrition table
                    div = [_ for _ in html.xpath(
                        '//*[@id="top"]/div') if _.get("class").startswith("body svelte-")][0]
                    script_info = json.loads(
                        div.xpath('./script[@type="application/ld+json"]/text()')[0])
                    yields_text = script_info["recipeYield"]
                    # number start
                    for si, s in enumerate(yields_text):
                        if s in '1234567890':
                            break
                    yields_text = yields_text[si:]
                    # number end
                    for si, s in enumerate(yields_text):
                        if s not in '1234567890':
                            break
                    yields = int(yields_text[:si])
                    yields = max(1, yields)
                    nutrition_raw = script_info["nutrition"]
                    nutrition = {}
                    for key in ['calories', 'fatContent', 'saturatedFatContent', 'cholesterolContent',
                                'sodiumContent',
                                'carbohydrateContent', 'fiberContent', 'sugarContent', 'proteinContent']:
                        nutrition[key] = float(nutrition_raw[key]) / yields
                    data["nutrition"] = nutrition
                    self.dish_id = recipe_id
                except:
                    info["recipe_available"] = False
            else:
                info["recipe_available"] = False

            # get approximate price and product list
            if info["recipe_available"]:
                recipe_tag = url.split("/")[-1]
                headers = {
                    'authority': r'widget.whisk.com',
                    'method': r'GET',
                    'path': '/api/v2/recipes/_widget?url=https%3A%2F%2Fwww.food.com%2Frecipe%2F{recipe_tag}&user_country=US&user_zip={code}'.format(
                        code=self.postcode, recipe_tag=recipe_tag),
                    'scheme': r'https',
                    'accept': r'*/*',
                    'accept-encoding': r'gzip, deflate, br',
                    'accept-language': r'zh-CN,zh;q=0.9',
                    'origin': r'https://cdn.whisk.com',
                    'referer': r'https://cdn.whisk.com/',
                    'sec-ch-ua': r'"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                    'sec-ch-ua-mobile': r'?1',
                    'sec-ch-ua-platform': r'"Android"',
                    'sec-fetch-dest': r'empty',
                    'sec-fetch-mode': r'cors',
                    'sec-fetch-site': r'same-site',
                    'user-agent': r'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
                    'whisk-timezone': r'Asia/Shanghai'
                }
                price_url = "https://widget.whisk.com/api/v2/recipes/_widget?url=https%3A%2F%2Fwww.food.com%2Frecipe%2F{recipe_tag}&user_country=US&user_zip={code}".format(
                    recipe_tag=recipe_tag, code=self.postcode)
                suc = False
                for i in range(self.retry):
                    try:
                        r = requests.get(price_url, headers=headers)
                        if r.status_code == requests.status_codes.codes.ok:
                            suc = True
                            break
                    except:
                        continue
                if suc and r.status_code == requests.status_codes.codes.ok:
                    info["price available"] = True
                    response_json = r.json()
                    r.close()

                    # price
                    if response_json["checkoutOptions"]["displayCost"]:
                        totoal_price = response_json["checkoutOptions"]["availableInventories"][0]["priceDetails"][
                            'totalPrice']
                        try:
                            resipe_serves = response_json["checkoutOptions"]["recipe"]["recipeYield"]
                        except:
                            resipe_serves = yields
                        if resipe_serves == 0:
                            resipe_serves = yields
                        data["price"] = totoal_price / resipe_serves
                        if data["price"] == 0:
                            data["price"] = None
                    else:
                        data["price"] = None

                    # product list
                    try:
                        data["product_list"] = [s.lower()
                                                for s in response_json["metadata"]["productsInRecipe"]]
                        self.ingredients = data["product_list"]
                    except:
                        data["product_list"] = None
                else:
                    info["price available"] = False
        else:
            info["legal"] = False
        return info, self.__display_one_recipe_detail(info)

    def display_ingredients(self):
        """
        print a list of ingredients' names for food keeper
        :return:str
        """
        out_s = ""
        for i, s in enumerate(self.ingredients):
            out_s += "%-4d %s\n" % (i, s)
        return out_s


if __name__ == "__main__":

    for mode in [True, False]:

        # init a FoodCom obj
        myFoodCom = FoodCom(online_mode=mode)
        # debug:
        self = myFoodCom

        # get top ranked recipes
        # how to use rank_page method ?

        # page 1 top ranked recipes
        info, display = myFoodCom.rank_page()
        print(display)

        # page 2 top ranked recipes
        info, display = myFoodCom.rank_page()
        print(display)

        # page 99 top ranked recipes
        info, display = myFoodCom.rank_page(rank_page_no=99)
        print(display)

        # if you then call it again, it will continue based on the last call
        # page 100
        info, display = myFoodCom.rank_page()
        print(display)

        # how to use search method ?
        key_words = "shrimp salad"
        # page 1
        page1, display = myFoodCom.search(key_words=key_words)
        print(display)

        # the results may be more than 1 page
        for _ in range(3):
            pagen, display = myFoodCom.search()
            print(display)

        # what if we input meaningless words "asd fgh jkl;"
        key_words = "asd fgh jkl;"
        pagen, display = myFoodCom.search(key_words=key_words)
        print(display)

        # how to use one_recipe_detail method
        recipe_id = page1["recipes"][list(page1["recipes"].keys())[
            0]]["recipe_id"]
        info, display = myFoodCom.one_recipe_detail(recipe_id)
        print(display)

        # food keeper input
        print(myFoodCom.ingredients)
        print(myFoodCom.display_ingredients())

        # unknown recipe id
        recipe_id = "99"
        info, display = myFoodCom.one_recipe_detail(recipe_id)
        print(display)
