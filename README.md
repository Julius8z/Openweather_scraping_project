# Openweather_scraping_project


Ce projet vise à collecter des données météorologiques à partir de l'API OpenWeatherMap pour 60 villes françaises, les stocker dans une base de données Cassandra et exposer ces données via une application Python.

--------Contenu du Projet

* crawler.py : Contient le script Python pour collecter les données météorologiques, se connecter à la base de données Cassandra et exposer les données via une API.
* current.city.list.json : Fichier JSON contenant la liste des villes disponibles avec leurs identifiants.
* Dockerfile : Fichier Docker pour le service Python.
* requirements.txt : Liste des dépendances Python.
* docker-compose.yml : Fichier Docker Compose pour orchestrer les services Python et Cassandra.
* README.md : Ce fichier, contenant des informations sur le projet.

  
--------Installation et Utilisation

* Assurez-vous d'avoir Docker et Docker Compose installés sur votre système.
* Clonez ce dépôt Git sur votre machine locale.
* Dans le répertoire du projet, lancez la commande docker-compose up --build pour construire et démarrer les services.
* Une fois les services démarrés, l'application Python devrait commencer à collecter et stocker les données météorologiques.
* Vous pouvez accéder à l'API exposée à l'adresse http://localhost:5000 pour obtenir les données météorologiques.
* Pour arrêter les services, utilisez la commande docker-compose down.

--------Remarques

- Assurez-vous que les ports 5000 et 9042 ne sont pas utilisés par d'autres applications sur votre machine.
- Veuillez consulter les logs des containers pour diagnostiquer d'éventuels problèmes.
- Ce projet est fourni à titre éducatif et peut être adapté selon les besoins spécifiques.

--------Note

- Il est tout à fait possible de tester vous même l'application en modifiant les paramètres tels que le nombre de villes ou le pays, cependant rien ne garantie des performances similaires à celles observées par la configuration initiale.
