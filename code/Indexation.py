from elasticsearch import Elasticsearch
import nltk
nltk.download('punkt')
import json
import glob
from pyvis.network import Network
import networkx as nx
import os
index = 'gutenberg'


def titreLivre(txt):
    titre = ""
    for sent in nltk.sent_tokenize(txt):
        if "Titre:" in sent:
            titre = sent.split('Titre: ')[1].split("\n")[0]
            return titre


def auteurLivre(txt):
    auteur = "Pas d'auteur"
    try:
        auteur = txt.split("Author: ")[1].split("Release Date")[0].replace('\n', '')
    except:
        try:
            auteur = txt.split("Authors: ")[1].split("Release Date")[0].replace('\n', '')
        except:
            auteur = txt.split("Editor: ")[1].split("Release Date")[0].replace('\n', '')

    return auteur


def idLivre(txt):
    id = ""
    for sent in nltk.sent_tokenize(txt):
        if ("[eBook" in sent):
            id = sent.split("#")[1].split("]")[0]
            break
    return id


def distance(s1, s2):

    #découper un text en token
    word_tokens1 = nltk.word_tokenize(s1)
    word_tokens2 = nltk.word_tokenize(s2)

    # parcour le mot dans la source pour voir si il contient uniquement des string
    words1 = []
    for i in word_tokens1:
        if i.isalpha():
            words1.append(i)
    word_tokens1 = words1

    words2 = []
    for i in word_tokens2:
        if i.isalpha():
           words2.append(i)
    word_tokens2 = words2

    # contruction d'une list sans doublon
    l = list(set(words1) & set(words2))

    #on calcule le nombre d'occurences des mots communs
    occurences = [max(words1.count(word), words2.count(word)) for word in l]

    #on fait la somme des max d'occurences
    numerateur = sum(occurences)

    #on fait la somme des occurences des mots de la liste 1
    denominateur = sum(words1.count(word) for word in l)

    return numerateur / denominateur


def dic_crank(tresh):
    files = glob.glob("*.txt")  # définit une variable files qui contient une liste des fichiers txt dans le répertoire courant
    id_list = []
    G = nx.Graph()
    nt = Network(height='100%', width='100%')
    nodes = []
    doc_neigh = {}
    id_titre = {}
    id_auteur = {}
    dic_distance = {}
    dic_crank = {}

    for f in files:
        id_list.append(int(f.split('g')[1].split('.')[0])) # ajoute l'id du livre à la liste id_list

    N = len(id_list)
    li = []

    for i in id_list:
        f = open("pg" + str(i) + ".txt", "r", encoding="utf8") # ouvre un fichier pour chaque id dans le répertoire
        t = f.read()
        li.append(t)
        dic_distance[i] = []
        G.add_node(i, titre=str(titreLivre(t)))
        nodes.append(i)
        id_titre[i] = titreLivre(t)
        id_auteur[i] = auteurLivre(t)
    for i in range(len(id_list)):
        doc_neigh[id_list[i]] = []

    for i in range(len(id_list)):
        for j in range(len(id_list)):
            if i != j:
                id1 = li[i].split('[eBook #')[1].split(']')[0]
                id2 = li[j].split('[eBook #')[1].split(']')[0]
                d = distance(li[i], li[j])
                if d < tresh and not G.has_edge(nodes[i], nodes[j]):
                    G.add_edge(nodes[i], nodes[j])  # ajoute un lien entre les noeuds à l'index i et j
                    doc_neigh[id_list[i]].append(id_list[j])  # ajoute l'id à l'index j à la liste associée à la clé à l'index i dans le dictionnaire doc_neigh
                    doc_neigh[id_list[j]].append(id_list[i]) # ajoute l'id à l'index i à la liste associée à la clé à l'index j dans le dictionnaire doc_neigh
                dic_distance[int(id1)].append(d)  # ajoute la distance entre les ebook à la liste associée à la clé id1 dans le dictionnaire dic_distance
                dic_distance[int(id2)].append(d) # ajoute la distance entre les ebook à la liste associée à la clé id2 dans le dictionnaire dic_distance
                print(f"d({id1},{id2}) = ", round(d, 5), "--- Pregress ... ",
                      100 * (j + 1 + i * len(id_list)) / len(id_list) ** 2, "%") # calcule le pourcentage de progrès

    for i in id_list:
        dic_distance[i] = list(dict.fromkeys(dic_distance[i])) # définit un dictionnaire qui contient les distances sans doublons
        dic_crank[i] = (N - 1) / sum(dic_distance[i]) # définit un dictionnaire qui contient le score de crank pour chaque livre

    print(dic_distance)
    print(dic_crank)
    nt.from_nx(G)
    nt.show_buttons(filter_=True)
    nt.show('nx.html')
    print(doc_neigh)
    return dic_crank, id_list, doc_neigh, id_titre, id_auteur



def text_json(txt, i, voisin, titre_voisin, auteur_voisin):

    # crée un dictionnaire contenant le titre du livre, l'auteur du livre, l'id du livre, le score du livre,
    # le texte du livre, ses voisins, les titres de ces voisins et les auteurs de ces voisins et convertit le tout en format json
    dict = {"titre": titreLivre(txt), "author": auteurLivre(ind), "Id": idLivre(txt), "crank": dic_crank[i],
            "content": txt, "voisin": voisin[i], "titre_voisin": {str(sugg): titre_voisin[sugg] for sugg in voisin[i]},
            "author_voisin": {str(sugg): auteur_voisin[sugg] for sugg in voisin[i]}}
    # print(dict)
    return json.dumps(dict)

os.chdir(os.getcwd() + '/bibliotheque')

dic_crank, id_list, doc_neigh, id_titre, id_auteur = dic_crank(0.5)

elastic = Elasticsearch([{'host': '127.0.0.1', 'port': 9200, 'scheme': 'http'}])
if elastic.indices.exists(index=index):
    elastic.indices.delete(index=index, ignore=[400, 404])

for i in id_list:
    f = open("pg" + str(i) + ".txt", "r", encoding="utf8")
    ind = f.read()
    response = elastic.index(index=index, doc_type='books', body=text_json(ind, i, doc_neigh, id_titre, id_auteur))


os.chdir('..')
