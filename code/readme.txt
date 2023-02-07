PROJET DAAR "A" : Moteur de recherche pour une bibliothèque.

Etudiants ( KABENE SAID , YANIS AZOUZ , HANAE CHIBANI )

Afin deffectuer un test de l'application web, il est necessaire d'avoir :

- Python et pip installé
- Un noeud Elasticsearch actif en localhost:9200

------------------------------------------------------------------------------------------------


Afin d'installer les packages python necessaire : executer le fichier code-source/requirements.txt
en utilisant la commande pip install -r requirement.txt


----------------------------------------------------------------------------------------------------

Une fois les packages installés, ouvrez un terminal dans le repertoire /code source  et executer la commande suivante:

python manage.py runserver

Pour un premier lancement, le programme va effectuer les taches suivante:

1) Calcul des distance entre les livres qui sont situés dans le repertoire code-source/bibliotheque
2) Générer le graphe de jaccard ( voir exemple dans /code-source/graphe-construit.html )
3) Structurer les données en format json
4) Indexer ces données dans le noeuds Elasticsearch (un index que l'on a appelé "livre")
5) Lancer le server web qui ecoute sur localhost:8000
6) ouvrir le navigateur en http://localhost:8000/ et commencez l'experience!

-------------------------------------------------------------------------------------------------------

Pour les prochains lancement de l'applications

Les actions 1 2 3 4 ne seront plus effectuer car la construction du graphe et l'indexation sont déjà faites.