"""
The back-end version of Recivery APP.


Team Member
- Wenyu Liu (wenyuliu)
- Yanjun Chen (yanjunch)
- Longyang Xu (lonyanx)
- Xinyu Wang (xwang5)
- Prachee Talwar (ptalwar)
"""

from foodcom import FoodCom
from googlemap import GoogleMap
from foodkeeper import FoodKeeper
import time


class Reciveray(object):
    def __init__(self, online_mode):
        self.online_mode = online_mode
        self.FoodCom = FoodCom(self.online_mode)
        self.GoogleMap = GoogleMap(self.online_mode)
        self.FoodKeeper = FoodKeeper(self.online_mode)

    def food_recommend(self, rank_page_no=None):
        return self.FoodCom.rank_page(rank_page_no)

    def food_search(self, keywords=None):
        return self.FoodCom.search(keywords)

    def food_keep_advise(self, keywords):
        return self.FoodKeeper.food_keep_advise(keywords)

    def workflow(self):

        tag = input(
            "\nDo you want to search a specific dish or our recommended dishes？S/R: ").lower()
        recommendation_mode = tag == 'r'

        # recommend dish
        if (recommendation_mode):
            try:
                # recommend intro
                intro_success = False
                while not intro_success:
                    recommendation_dic, display = self.food_recommend(1)
                    print(display)
                    # bad network
                    if not recommendation_dic["available"]:
                        print("Retry in 10 seconds\nCheck you Internet status please")
                        time.sleep(10)
                    else:
                        intro_success = True

                # recommend more pages
                tag = input(
                    "\nDo you want to see other recommendation? Y/N: ").lower()
                next_page_tag = tag == "y"
                while (next_page_tag):
                    recommendation_dic, display = self.food_recommend()
                    print(display)
                    tag = input(
                        "\nDo you want to see other recommendation? Y/N: ").lower()
                    next_page_tag = tag == "y"
            except:
                print("\nTODO: recommend dish")

        else:
            # search dish
            keywords = input("\nPlease input any dish you want to search: ")
            try:
                # search intro
                intro_success = False
                while not intro_success:
                    search_dic, display = self.food_search(keywords)
                    print(display)
                    # bad network
                    if not search_dic["available"]:
                        print("Retry in 10 seconds\nCheck you Internet status please")
                        time.sleep(10)
                        continue
                    # meaningless input, 0 search result
                    if len(search_dic["recipes"]) == 0:
                        keywords = input(
                            "\nPlease input any dish you want to search: ")
                    else:
                        intro_success = True
                # search more pages
                tag = input("\nDo you want to see next page? Y/N: ").lower()
                next_page_tag = tag == "y"
                while (next_page_tag):
                    search_dic, display = self.food_search()
                    print(display)
                    tag = input(
                        "\nDo you want to see next page? Y/N: ").lower()
                    next_page_tag = tag == "y"
            except:
                print("TODO: search dish")

        # display dish
        dish_id = input(
            "\nChoose the recipy you want to see detail？Only Number: ")
        dish_id = str(dish_id)
        try:
            detail_suc = False
            while not detail_suc:
                detail_dic, display = self.FoodCom.one_recipe_detail(dish_id)
                print(display)
                # unknown id
                if not detail_dic["legal"]:
                    dish_id = input(
                        "\nChoose the recipy you want to see detail？Only Number: ")
                    dish_id = str(dish_id)
                    continue
                # sucess
                if detail_dic["recipe_available"]:
                    detail_suc = True
                # bad network
                else:
                    print("Retry in 10 seconds\nCheck you Internet status please")
                    time.sleep(10)
        except:
            print("\nTODO: display dish")

        # bug ingredient
        tag = input(
            "\nDo you want to buy the ingredients and try it? Y/N: ").lower()
        buy_tag = tag == "y"
        if (buy_tag):
            address = input(
                "\nPlease input your address so that we can recommend the best grocery stores for you: ")

            try:
                self.GoogleMap.generate_form(address)
                grocery_dic = self.GoogleMap.info()
                print(grocery_dic)

                grocery_id = input(
                    "\nChoose the grocery stores you want to see detail？Only Numbers (divide with ,) : ").split(',')
                print(grocery_id)
                rows = []
                for id in grocery_id:
                    rows.append(eval(id))
                grocery_detail = self.GoogleMap.details(rows)
                print(grocery_detail, "\n")

            except:
                print("\nTODO: bug ingredient")

            print("\nYour order has been confirmed.")

        # display food keep advise
        tag = input(
            "\nDo you want to know how to keep the ingredients? Y/N: ").lower()
        food_keeper_tag = tag == "y"
        if (food_keeper_tag):
            try:
                print(self.FoodCom.display_ingredients())
                ingredients_id = input(
                    "Choose the ingredients you want to know how to keep? Only Numbers (divide with ,) : ").split(',')
                ingredients = []
                for id in ingredients_id:
                    ingredients.append(self.FoodCom.ingredients[eval(id)])

                keep_dict = self.food_keep_advise(ingredients)
                advise = ""
                for food, head in keep_dict.items():
                    print(
                        'For freshness and quality, {} should be consumed within:'.format(food))
                    advise = advise + \
                        'For freshness and quality, {} should be consumed within:'.format(
                            food)
                    if 'Pantry_Metric' in head.keys():
                        print('{} - {} {} if in the pantry from the date of purchase'
                              .format(head['Pantry_Min'], head['Pantry_Max'], head['Pantry_Metric']))
                        advise = advise + '{} - {} {} if in the pantry from the date of purchase'.format(
                            head['Pantry_Min'], head['Pantry_Max'], head['Pantry_Metric'])
                    if 'DOP_Pantry_Metric' in head.keys():
                        print('{} - {} {} if pantry stored after opening'
                              .format(head['DOP_Pantry_Min'], head['DOP_Pantry_Max'], head['DOP_Pantry_Metric']))
                        advise = advise + '{} - {} {} if pantry stored after opening'.format(
                            head['DOP_Pantry_Min'], head['DOP_Pantry_Max'], head['DOP_Pantry_Metric'])
                    if 'DOP_Refrigerate_Metric' in head.keys():
                        print('{} - {} {} if refrigerated from the date of purchase'
                              .format(head['DOP_Refrigerate_Min'], head['DOP_Refrigerate_Max'], head['DOP_Refrigerate_Metric']))
                        advise = advise + '{} - {} {} if refrigerated from the date of purchase'.format(
                            head['DOP_Refrigerate_Min'], head['DOP_Refrigerate_Max'], head['DOP_Refrigerate_Metric'])
                    if 'DOP_Freeze_Metric' in head.keys():
                        print('{} - {} {} if pantry stored after opening'
                              .format(head['DOP_Freeze_Min'], head['DOP_Freeze_Max'], head['DOP_Freeze_Metric']))
                        advise = advise + '{} - {} {} if pantry stored after opening'.format(
                            head['DOP_Freeze_Min'], head['DOP_Freeze_Max'], head['DOP_Freeze_Metric'])
                    print('\n')
                    advise = advise + "\n"

            except:
                print('Sorry, no more food keep advice for this ingredient')

        print("\nThanks for using!")


if __name__ == '__main__':

    tag = input(
        "\nDo you want to access the app online or offline? ON/OFF: ").lower()
    reciveray = Reciveray(online_mode=tag == 'on')
    reciveray.workflow()
