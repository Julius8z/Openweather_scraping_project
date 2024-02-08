#!/usr/local/bin/python3

import json
import datetime
import time
import urllib.request
from cassandra.cluster import Cluster

# Attendre 60 sec avant de tenter la connexion à Cassandra
time.sleep(60)

# Connexion au cluster Cassandra
try:
    cluster = Cluster(['cassandra-1'], port=9042)
    session = cluster.connect()
    print("Connexion à Cassandra établie.")
except Exception as e:
    print(f"Une erreur s'est produite lors de la connexion à Cassandra : {e}")
    exit(1)

# Création du Keyspace weatherJbob s'il n'existe pas
try:
    session.execute("CREATE KEYSPACE IF NOT EXISTS weatherJbob WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}")
    print("Keyspace weatherJbob créé avec succès.")
except Exception as e:
    print(f"Une erreur s'est produite lors de la création du Keyspace : {e}")
    exit(1)

# Création de la table cities dans le Keyspace weatherJbob s'elle n'existe pas
try:
    session.set_keyspace('weatherJbob')
    session.execute('CREATE TABLE IF NOT EXISTS cities (idcity INT PRIMARY KEY, city TEXT, country TEXT, sky TEXT, temp DOUBLE, temp_max DOUBLE, temp_min DOUBLE, wind DOUBLE, wind_deg DOUBLE, humidity INT, cloudiness INT, pressure DOUBLE, sunrise TIMESTAMP, sunset TIMESTAMP, dt TIMESTAMP)')
    print("Table cities créée avec succès.")
except Exception as e:
    print(f"Une erreur s'est produite lors de la création de la table cities : {e}")
    exit(1)

# Fonction permettant de créer l'URL complet à partir de [API_key/city_id]  ou [API_Key/city_name/country].
def url_builder(city_id, city_name, country):
    user_api = '4e0f8959dab541379b863bd8868196a6'
    unit = 'metric'  # Valeur utilisée pour avoir les températures en Celsius.
    if city_name != "":
        api = 'http://api.openweathermap.org/data/2.5/weather?q='
        full_api_url = api + str(city_name) + ',' + str(country) + '&mode=json&units=' + unit + '&APPID=' + user_api
    else:
        api = 'http://api.openweathermap.org/data/2.5/weather?id='
        full_api_url = api + str(city_id) + '&mode=json&units=' + unit + '&APPID=' + user_api
    return full_api_url

# Fonction permettant d'utiliser l'URL complet pour récupérer les données en fonction des paramètres données (city_name/city_id/country)
def data_fetch(full_api_url):
    try:
        url = urllib.request.urlopen(full_api_url)
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output) # Convertir une chaine comme dictionnaire
        url.close() # Fermeture de la connexion SQL à l'API
        return raw_api_dict
    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des données météorologiques : {e}")
        return None

def time_converter(time):
    try:
        datetime_obj = datetime.datetime.fromtimestamp(int(time)) # Conversion du timestamp Unix en objet datetime
        formatted_time = datetime_obj.strftime('%Y-%m-%d %H:%M:%S') # Formattage de l'objet datetime en string de format : 'YYYY-MM-DD HH:MM:SS'
        return formatted_time
    except Exception as e:
        print(f"Erreur lors de la conversion du temps : {e}")
        return None

def data_organizer(raw_api_dict):
    try:
        data = {
            'id_city': raw_api_dict.get('id'),
            'city': raw_api_dict.get('name'),
            'country': raw_api_dict.get('sys').get('country'),
            'temp': raw_api_dict.get('main').get('temp'),
            'temp_max': raw_api_dict.get('main').get('temp_max'),
            'temp_min': raw_api_dict.get('main').get('temp_min'),
            'humidity': raw_api_dict.get('main').get('humidity'),
            'pressure': raw_api_dict.get('main').get('pressure'),
            'sky': raw_api_dict['weather'][0]['main'],
            'sunrise': time_converter(raw_api_dict.get('sys').get('sunrise')),
            'sunset': time_converter(raw_api_dict.get('sys').get('sunset')),
            'wind': raw_api_dict.get('wind').get('speed'),
            'wind_deg': raw_api_dict.get('wind').get('deg'),
            'dt': time_converter(raw_api_dict.get('dt')),
            'cloudiness': raw_api_dict.get('clouds').get('all')
        }
        return data
    except Exception as e:
        print(f"Erreur lors de l'organisation des données : {e}")
        return None

# Chemin vers le fichier JSON
json_file_path = 'current.city.list.json'

# Nombre de villes à récupérer
num_cities_to_fetch = 60

# Liste pour stocker les données des villes françaises
french_cities = []

# Ouvrir et lire le fichier JSON
try:
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

        # Parcourir les données pour récupérer les informations des villes françaises
        for city in data:
            if city.get('country') == 'FR':
                city_data = {
                    'id': city.get('id'),
                    'country': city.get('country'),
                    'name': city.get('name')
                }
                french_cities.append(city_data)

                # Sortir de la boucle une fois que le nombre de villes souhaité est atteint
                if len(french_cities) == num_cities_to_fetch:
                    break
except Exception as e:
    print(f"Erreur lors de la lecture du fichier JSON : {e}")
    exit(1)

# Pour chaque ville dans la liste obtenue, récupérer les valeurs de : id, name, country...
for city in french_cities:
    city_id = city['id']
    city_name = city['name']
    country = city['country']

    # afin de construire les URLs avec la fonction url_builder()...
    full_api_url = url_builder(city_id, city_name, country)
    # pour par la suite récupérer les données à l'aide de ces URLs grace à la fonction data_fetch()...
    weather_data = data_fetch(full_api_url)
    if weather_data:
        # enfin on organise les données pour garder celles qui seront insérées en base grace à la fonction data_organizer()...
        organized_data = data_organizer(weather_data)
        if organized_data:
            try:
                # On finit par exécuter la requête d'insertion pour chacunes des villes et données correspondantes récupérées.
                session.execute(insert_query, organized_data)
                print(f"Données pour la ville {city_name} insérées avec succès.")
            except Exception as e:
                print(f"Une erreur s'est produite lors de l'insertion des données pour la ville {city_name} : {e}")
    else:
        print(f"Données météorologiques non disponibles pour la ville {city_name}")

# Fermer la session Cassandra et terminer le programme
session.shutdown()
cluster.shutdown()