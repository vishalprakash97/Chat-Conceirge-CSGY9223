import boto3
from matplotlib.pyplot import table

if __name__ == "__main__":
    try:
        db=boto3.client('dynamodb')
        table_name="yelp-restaurants"
        if table_name in db.list_tables()['TableNames']:
            print("Table already exists:\t%s\n" %(table_name))
        else:
            key_schema = [{
                "AttributeName": "restaurant_id",
                "KeyType": "HASH"
                }]
            attribute_definitions = [{
                "AttributeName": "restaurant_id",
                "AttributeType": "S"
                }]
            provisioned_throughput = {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
                }
            table_ref=db.create_table(TableName=table_name,
                                AttributeDefinitions=attribute_definitions,
                                KeySchema=key_schema,
                                ProvisionedThroughput=provisioned_throughput)
            print("%s Table created successfully" % (table_name))

    except Exception as ex:
        print("Error Occured:", ex.message)

        


