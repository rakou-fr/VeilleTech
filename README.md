# 📡 TechWatch Data Store — BTS SIO

Ce dépôt sert d'**API statique et automatisée** pour alimenter un système de veille technologique. Il héberge un script d'agrégation Python exécuté à intervalles réguliers via GitHub Actions, ainsi que le fichier `news.json` consommé par les applications clientes.

---

## 🎯 Objectif du projet

Dans le cadre du diplôme **BTS SIO (Services Informatiques aux Organisations)**, la mise en place d'une veille technologique structurée est essentielle. Ce projet répond aux besoins suivants :

* **Centralisation des sources :** Agrégation automatique de multiples flux RSS/Atom spécialisés (développement, cybersécurité, cloud, infrastructure, IA).
* **Catégorisation & Tagging :** Classification automatique des articles grâce à un moteur de mots-clés optimisé.
* **Déduplication :** Génération d'empreintes uniques (SHA256) pour garantir l'absence de doublons dans la base.
* **Automation (CI/CD) :** Automatisation complète de la collecte via GitHub Actions sans nécessiter de serveur dédié.

---

## 🏗️ Architecture des fichiers

* `sources.json` : Liste de configuration des flux RSS/Atom suivis.
* `main.py` : Script de collecte, nettoyage HTML, tagging et parsing de dates.
* `requirements.txt` : Dépendances Python nécessaires au projet.
* `news.json` : Base de données générée contenant les articles triés du plus récent au plus ancien.

---

## ⚡ Récupération du fichier JSON (URL Raw)

L'accès au fichier `news.json` se fait directement via l'URL d'export brut fourni par GitHub :

https://raw.githubusercontent.com/rakou-fr/VeilleTech/main/news.json

---

## 💻 Exemples de récupération (HTTP Requests)

### Option 1 : En ligne de commande (Linux / macOS / Windows Terminal)

Via curl (sauvegarde directe dans un fichier local) :
curl -s "https://raw.githubusercontent.com/rakou-fr/VeilleTech/main/news.json?t=$(date +%s)" -o news_local.json

Via curl + jq (lecture directe formatée dans le terminal) :
curl -s "https://raw.githubusercontent.com/rakou-fr/VeilleTech/main/news.json?t=$(date +%s)" | jq '.articles[0:5]'

---

### Option 2 : En Python (avec la bibliothèque requests)

import time
import requests

RAW_URL = "https://raw.githubusercontent.com/rakou-fr/VeilleTech/main/news.json"
url_with_cache_buster = f"{RAW_URL}?t={int(time.time())}"

try:
    response = requests.get(url_with_cache_buster)
    response.raise_for_status()
    
    data = response.json()
    print(f"Dernière mise à jour : {data.get('updated_at')}")
    print(f"Nombre d'articles   : {data.get('count')}\n")

    for article in data.get("articles", [])[:3]:
        print(f"[{article['category'].upper()}] {article['title']}")
        print(f"Source : {article['source']} | URL : {article['url']}\n")

except requests.exceptions.RequestException as error:
    print(f"Erreur lors de la récupération des données : {error}")

---

## 🤖 Automatisation GitHub Actions

La mise à jour de la base de données `news.json` est entièrement automatisée :

* **Fréquence :** Toutes les 6 heures via une tâche cron (`0 */6 * * *`).
* **Exécution manuelle :** Déclenchable à tout moment depuis l'onglet Actions du dépôt (Workflow Dispatch).
