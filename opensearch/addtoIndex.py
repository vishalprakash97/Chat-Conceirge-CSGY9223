from decouple import config
import yaml
import json
import requests


list_cuisines=['Indian',"Thai","Chinese","Italian","Japanese","Mediterranean"]
path="../YelpAPI/"
credentials = (config("username"),config("password"))
host_url = config("host_url")
index_name = 'restaurants'
type_name = 'Restaurant'
region = 'us-east-1' 
service = 'es'


def create_index(index_name):
    url = '%s/%s' % (host_url, index_name)
    response = requests.put(url, auth=credentials)
    print (response.json())


def create_type(index_name, type_name):
    url = '%s/%s/%s/_mapping' % (host_url, index_name, type_name)
    headers = {"Content-Type": "application/json"}
    body = {
        "Restaurant": {
            "properties": {
                "restaurant_id": {
                    "type": "text"
                },
                "cuisine": {
                    "type": "text"
                }
            }
        }
    }
    params = {
        "include_type_name": "true"
    }
    response = requests.put(url, auth=credentials, data=json.dumps(body), params=params, headers=headers)
    print (response.json())


def upload_json_to_index(index_name):
    url = '%s/%s/_doc/' % (host_url, index_name)
    for filename in list_cuisines:
        data = yaml.safe_load(open("%s%s.json" % (path, filename)))
        for record in data:
            document = {"restaurant_id": record["id"], "cuisine": filename}
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, auth=credentials, data=json.dumps(document), headers=headers)
            print(response.json())
    #print("%s Cuisine Done" %(index_name))


def delete_index(index_name):
    url = '%s/%s' % (host_url, index_name)
    response = requests.delete(url, auth=credentials)
    print (response.json())


def search_data_on_index(index_name, cuisine):
    # Search for the document.
    query = {
        'query': {
            'multi_match': {
                'query': cuisine,
                'fields': ['cuisine']
            }
        }
    }
    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = {"Content-Type": "application/json"}
    url = "%s/%s/_search" % (host_url, index_name)
    # Make the signed HTTP request
    response = requests.get(url, auth=credentials, headers=headers, data=json.dumps(query)).json()
    print('\nSearch results:')
    count=0;
    for record in response['hits']['hits']:
        count+=1
        print(record)
    print(count)


if __name__ == "__main__":
    #create_index(index_name)
    #create_type(index_name,type_name)
    upload_json_to_index(index_name)
    #search_data_on_index(index_name,"mediterranean")
    #---------WARNING----------
    #delete_index('restaurants')