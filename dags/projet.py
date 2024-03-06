from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import pymongo

def retrieve_api_result():
    url_profile = 'https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=LS6T2uIqVqLOhncDAxobPZtlR9EvRk4X'
    url_rating = 'https://financialmodelingprep.com/api/v3/rating/AAPL?apikey=LS6T2uIqVqLOhncDAxobPZtlR9EvRk4X'

    response_profile = requests.get(url_profile)

    response_rating = requests.get(url_rating)

    data = {
        "profile": response_profile.json(),
        "rating": response_rating.json(),
        "timestamp": str(datetime.now())
    }

    with open('jsontomongo.json', 'w') as json_file:
        json.dump(data, json_file)


def dump_to_mongodb():
    with open('jsontomongo.json', 'r') as json_file:
        data = json.load(json_file)

    clientMongoDB = pymongo.MongoClient("mongodb://mongodb:27017/")

    db = clientMongoDB["projet"]
    collection = db["data3"]

    collection.insert_one(data)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 6),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fetch_data_and_dump_to_mongodb',
    default_args=default_args,
    description='DAG to fetch data and dump to MongoDB',
    schedule_interval=timedelta(minutes=1),
)

retrieve_api_task = PythonOperator(
    task_id='retrieve_api_result_task',
    python_callable=retrieve_api_result,
    dag=dag,
)

dump_to_mongodb_task = PythonOperator(
    task_id='dump_to_mongodb_task',
    python_callable=dump_to_mongodb,
    dag=dag,
)

retrieve_api_task >> dump_to_mongodb_task