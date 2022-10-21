import time
import boto3
import yaml

table_name="yelp-restaurants"
list_cuisines=['Indian',"Thai","Chinese","Italian","Japanese","Mediterranean"]
path="../YelpAPI/"
db=boto3.resource('dynamodb')
table=db.Table(table_name)

for file in list_cuisines:
    file_path=path+file+".json"
    data=yaml.safe_load(open(file_path))
    count=0
    for row in data:
        item={
            "restaurant_id":str(row["id"]),
            "name": row["name"],
            "address": row["location"]["display_address"],
            "zipcode": str(row["location"]["zip_code"]),
            "coordinates": {"latitude": str(row["coordinates"]["latitude"]),
                            "longitude": str(row["coordinates"]["longitude"])},
            "contact": str(row["phone"]),
            "rating": str(row["rating"]),
            "review_count": str(row["review_count"]),
            "transactions": row["transactions"],
            "insertAtTimestamp": str(time.time())
        }
        table.put_item(TableName=table_name,Item=item)
        count+=1
    
    print("%d Records added from %s " %(count,file))
