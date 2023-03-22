from foodcom import FoodCom
import pickle as pkl

if __name__ == "__main__":
    myFoodCom = FoodCom(True)
    for _ in range(100):
        suc = False
        while not suc:
            rank_raw = myFoodCom.rank_page(_ + 1)[0]
            suc = True
        rank_page_data = {}
        rank_records = {}
        for recipe_name, recipe_id in rank_raw["recipes"].items():
            try:
                search_data = myFoodCom.search(recipe_id)[0]['recipes']
                assert len(search_data) == 1
                detail_data = myFoodCom.one_recipe_detail(recipe_id)[0]
                assert detail_data["legal"] and detail_data["recipe_available"]
            except:
                continue
            url = myFoodCom.recipe_records[recipe_id]
            rank_page_data[recipe_name] = recipe_id
            rank_records[recipe_id] = url
            with open("./foodComOfflineCache/search/data/" + recipe_name.replace(" ", "_") + ".pkl", "wb") as f:
                pkl.dump(search_data, f)
            with open("./foodComOfflineCache/search/records/" + recipe_name.replace(" ", "_") + ".pkl", "wb") as f:
                pkl.dump({recipe_id: url}, f)
            with open("./foodComOfflineCache/detail/" + recipe_id + ".pkl", "wb") as f:
                pkl.dump(detail_data, f)
        with open("./foodComOfflineCache/recommend/data/" + str(_ + 1) + ".pkl", "wb") as f:
            pkl.dump(rank_page_data, f)
        with open("./foodComOfflineCache/recommend/records/" + str(_ + 1) + ".pkl", "wb") as f:
            pkl.dump(rank_records, f)
