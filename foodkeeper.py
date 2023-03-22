"""
- Provide food keep advice

"""

'''
FoodKeeper
'''
import json
import pandas as pd


class FoodKeeper(object):
    def __init__(self, online_mode):
        self.online_mode = online_mode

    def get_value(self, x):
        if x:
            result = list(x.values())[0]
        else:
            result = x
        return result

    def data_format(self, df):
        cols = []
        for i in range(df.shape[1]):
            col = list(df[i][0].keys())[0]
            cols.append(col)
            df[i] = df[i].apply(lambda x: self.get_value(x))
        df.columns = cols
        return df

    def search_keywords(self, food, keywords):
        for words in keywords.split(','):
            if food == words.strip().capitalize():
                return True
            else:
                continue
        return False

    def food_keep_advise(self, food_name):
        f = open('foodkeeper.json', 'r', encoding='utf-8')
        text = json.loads(f.read())

        data_product = text['sheets'][2]["data"]
        df_product = pd.DataFrame(data_product)
        df_product = self.data_format(df_product)
        res = dict()
        for food in food_name:
            food = food.strip().capitalize()
            df_product = df_product.dropna(subset=['Keywords'])
            df_product['flag'] = df_product.apply(
                lambda row: self.search_keywords(food, row['Keywords']), axis=1)
            df_name = df_product[df_product['flag'] == True]
            if df_name.empty:
                res[food] = 'No food keep advice'
            else:
                head = df_name.head(1)
                head = head.dropna(axis=1, how='any')
                head = head.to_dict(orient='list')
                for key, value in head.items():
                    head[key] = value[0]
                res[food] = head
        return res


if __name__ == '__main__':
    food_name = input(
        "\nInput a list of food name:(divide with ,):").split(',')
    fk = FoodKeeper(online_mode='OFF')
    fk.food_keep_advise(food_name)
