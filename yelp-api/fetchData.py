
import requests
from decouple import config
import json

API_KEY = config("API_KEY")
API_URL_ENDPOINT = config("API_URL_ENDPOINT")
API_PER_REQUEST_LIMIT_COUNT = 50

HEADERS={  "Authorization": 'bearer %s' % API_KEY}


def fetch_data(type,total_records=1000):
    data=[]
    for count in range(0,total_records,API_PER_REQUEST_LIMIT_COUNT):
        params={
            "location":"New York City",
            "term":type,
            "categories":"Restaurants",
            "limit":API_PER_REQUEST_LIMIT_COUNT,
            "offset": count
        }
        response=requests.get(API_URL_ENDPOINT,params=params,headers=HEADERS).json()
        #print(response)
        for row in response['businesses']:
            data.append(row)
    print("%d %s records fetched" % (count+API_PER_REQUEST_LIMIT_COUNT, type))
    with open(type+'.json','w') as fd:
        json.dump(data,fd)

if __name__ == "__main__" :
    cuisines=['Indian',"Thai","Chinese","Italian","Japanese","Mediterranean"]
    for item in cuisines:
        fetch_data(item)

