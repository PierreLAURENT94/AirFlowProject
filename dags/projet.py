import requests
import pymongo
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

clientMongoDB = pymongo.MongoClient("mongodb://mongodb:27017/")

url_profile = 'https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=LS6T2uIqVqLOhncDAxobPZtlR9EvRk4X'
url_rating = 'https://financialmodelingprep.com/api/v3/rating/AAPL?apikey=LS6T2uIqVqLOhncDAxobPZtlR9EvRk4X'

def fetch_data_and_insert_to_mongodb():
    response_profile = requests.get(url_profile)

    response_rating = requests.get(url_rating)

    if response_profile.status_code == 200:
        profile_data = response_profile.json()
    else:
        print('Erreur lors de la requête pour le profil :', response_profile.status_code)
        profile_data = None

    if response_rating.status_code == 200:
        rating_data = response_rating.json()
    else:
        print('Erreur lors de la requête pour la notation :', response_rating.status_code)
        rating_data = None

    data = {
        "profile": profile_data,
        "rating": rating_data,
        "timestamp": datetime.now()
    }

    db = clientMongoDB["projet"]
    collection = db["data"]

    collection.insert_one(data)

# Paramètres du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 6),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définition du DAG
dag = DAG(
    'fetch_data_and_insert_to_mongodb',
    default_args=default_args,
    description='DAG pour récupérer les données et les insérer dans MongoDB',
    schedule_interval=timedelta(minutes=1),
)

# Définition de l'opérateur Python
fetch_data_operator = PythonOperator(
    task_id='fetch_data_and_insert_to_mongodb_task',
    python_callable=fetch_data_and_insert_to_mongodb,
    dag=dag,
)

fetch_data_operator