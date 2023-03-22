"""
- Implement the Google Search API to search nearby grocery stores.

"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class GoogleMap(object):
    r"""
    Implement the Google Search API to search nearby grocery stores.
    
    Args:
        online_mode:
        address (string): User's house address, the search engine will find grocery stores around this address. 
        standard (dict): Filter standard, ex. {"business_status": "OPERATIONAL", "rating": 3} implies all grocery stores found should be operational and their ratings are above 3.
        num (int): The number of grocery stores returned.
    """

    def __init__(self, online_mode, standard={"business_status": "OPERATIONAL", "rating": 3}, num=20):
        self.key = 'AIzaSyAI3x9BLFpqDi-Dw4roU9V4eiufWHBYvSA'
        self.radius_pattern = [100, 200, 500, 1000, 2000, 5000, 10000]
        self.standard = standard
        self.num = num
        self.online_mode = online_mode

    def generate_form(self, address):

        url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={address}&key={self.key}'
        r = requests.get(url)
        data = r.json()
        self.lat = data['results'][0]['geometry']['location']['lat']
        self.lng = data['results'][0]['geometry']['location']['lng']
        self.address = address
        self.form_create()

    def query(self, radius):
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={self.lat}%2C{self.lng}&radius={radius}&keyword=grocery store&key={self.key}"
        r = requests.get(url)
        data = r.json()
        collect = []
        for d in data['results']:
            if d["business_status"] == self.standard["business_status"] and d["rating"] >= self.standard["rating"]:
                collect.append(d)

        return collect

    def form_create(self):
        k = 0
        id = 0

        store_id = []
        store_name = []
        distance = []
        store_rating = []
        user_rating_total = []
        opening_status = []
        location = []

        while len(store_id) < self.num:
            if k == len(self.radius_pattern):
                id = 1
                break
            collect = self.query(self.radius_pattern[k])

            for j in collect:
                if j['place_id'] not in store_id:
                    store_id.append(j['place_id'])
                    store_name.append(j['name'])
                    store_rating.append(j['rating'])
                    user_rating_total.append(j['user_ratings_total'])
                    opening_status.append(
                        j['opening_hours']['open_now']) if 'opening_hours' in j else opening_status.append('Not available')
                    distance.append(self.radius_pattern[k])
                    location.append(j['vicinity'])

            k += 1

        diction = {}
        diction['grocery store'] = store_name if id == 1 else store_name[:self.num]
        diction['rating'] = store_rating if id == 1 else store_rating[:self.num]
        diction['distance <'] = distance if id == 1 else distance[:self.num]
        diction['rating_numbers'] = user_rating_total if id == 1 else user_rating_total[:self.num]
        diction['opening_now'] = opening_status if id == 1 else opening_status[:self.num]
        diction['location'] = location if id == 1 else location[:self.num]
        f = pd.DataFrame(data=diction, index=range(
            len(store_name) if id == 1 else len(store_name[:self.num])))

        if id == 1:
            print(
                'Warning! System can only show grocery stores within 10km away from your home.')

        self.form = f
        
    def counter(self, data):
        count = np.zeros(5)
        for d in data:
            if d < 4.0:
                count[4] += 1
            else:
                count[int(8-4*(d-3))] += 1
        return count

    """
    return all potential grocery stores info nearby.
    """
    def info(self):
        return self.form.iloc[:, :3]

    """
    return the store's details of the given id
    """
    def details(self, id):
        return self.form.iloc[id,]

    def plot_pie(self):
        data = self.form.iloc[:, 1].to_numpy()
        labels = '4.75-5.00', '4.50-4.75', '4.25-4.50', '4.00-4.25', '<=4.00'
        count = self.counter(data)

        plt.subplot(2,1,1)
        plt.pie(count, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        plt.title('Grocery Store Rating')
        # plt.savefig('rating.png')
        # plt.show()
    
    def plot_bar(self):
        plt.subplot(2,1,2)
        num_list = self.form['distance <']
        name_list = range(len(num_list))
        

        plt.bar(range(len(num_list)), num_list,tick_label=name_list)

        plt.xlabel('Grocery Store Index')
        plt.ylabel('Distance (m)')
        plt.title('Grocery Store Distance')
        # plt.savefig('rating_number_distribution.png')
        plt.show()
        


if __name__ == '__main__':
    address = "518 SHADY AVE, PITTSBURGH, PA"
    g = GoogleMap(online_mode=True)
    g.generate_form(address)
    grocery_dic = g.info()
    g.plot_pie()
    g.plot_bar()
    print(grocery_dic)