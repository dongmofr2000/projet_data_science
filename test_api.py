import requests
import pytest

# L'URL de base de votre API locale
API_URL = "http://127.0.0.1:8000"

def test_homepage_endpoint_status():
    """Vérifie que l'endpoint de la page d'accueil est accessible."""
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    assert response.json()["message"] == "Bienvenue sur l'API de données de Seattle ! Accédez aux données via le chemin /data."

def test_get_data_endpoint_returns_data():
    """Vérifie que l'endpoint /data retourne bien les données."""
    response = requests.get(f"{API_URL}/data")
    assert response.status_code == 200
    assert len(response.json()) == 5  # On s'attend à recevoir les 5 premières lignes

def test_get_data_by_year_valid():
    """Teste l'endpoint /data/year/{year} avec une année valide (2016)."""
    response = requests.get(f"{API_URL}/data/year/2016")
    assert response.status_code == 200
    assert "message" not in response.json() # On s'attend à des données, pas à un message d'erreur

def test_get_data_by_year_invalid():
    """Teste l'endpoint /data/year/{year} avec une année qui n'existe pas."""
    response = requests.get(f"{API_URL}/data/year/9999")
    assert response.status_code == 200 # L'API retourne 200 même si aucune donnée n'est trouvée
    assert response.json()["message"] == "Aucune donnée trouvée pour l'année 9999."

def test_submit_data_endpoint_valid():
    """Teste l'endpoint POST /data/submit avec des données valides."""
    valid_data = {
      "OSEBuildingID": 12345,
      "DataYear": 2023,
      "BuildingType": "Nonresidential",
      "PrimaryPropertyType": "Office",
      "PropertyName": "Test Building",
      "Address": "456 Test St",
      "GHGEmissionsIntensity": 10.5
    }
    response = requests.post(f"{API_URL}/data/submit", json=valid_data)
    assert response.status_code == 200
    assert "succès" in response.json()["message"]

def test_submit_data_endpoint_invalid():
    """Teste l'endpoint POST /data/submit avec des données invalides (champ manquant)."""
    invalid_data = {
      "OSEBuildingID": 12345,
      "DataYear": 2023,
      # Le champ 'BuildingType' est manquant ici
      "PrimaryPropertyType": "Office",
      "PropertyName": "Test Building",
      "Address": "456 Test St",
      "GHGEmissionsIntensity": 10.5
    }
    response = requests.post(f"{API_URL}/data/submit", json=invalid_data)
    assert response.status_code == 422 # 422 est le code d'erreur de validation de FastAPI
    assert response.json()["detail"][0]["msg"] == "Field required"


expliquer la séquence des étapes d’utilisation de l’API (serving en local, construction de l’image docker via bentofile.yaml, conteneurisation et déploiement dans le Cloud).

Étape 1 : Servir en local (Développement & Test)

C'est la première étape. L'objectif est de s'assurer que votre API fonctionne correctement sur votre propre machine avant de la mettre dans un conteneur.

    Le Rôle de BentoML : Vous créez un fichier Python (souvent nommé service.py) qui définit les endpoints de votre API à l'aide de décorateurs @bentoml.api. C'est dans ce fichier que vous chargerez votre modèle entraîné et que vous écrirez la logique de prédiction.

    La Commande : Vous utilisez la commande bentoml serve pour lancer l'API. Cela crée un serveur web local (généralement accessible via http://localhost:3000) qui vous permet de tester vos endpoints en temps réel.

Étape 2 : Construction de l'image Docker via bentofile.yaml (Packaging)

Une fois que votre API fonctionne en local, l'étape suivante est de la "packager" pour qu'elle puisse s'exécuter n'importe où. C'est le rôle de bentofile.yaml.

    Le Rôle de bentofile.yaml : Ce fichier est la "recette" pour construire votre application. Il indique à BentoML ce qu'il doit inclure dans le package final (le code source, le modèle entraîné, les fichiers de configuration, etc.) et quelles dépendances Python il doit installer.

    La Commande : Vous utilisez la commande bentoml build. Cette commande lit votre bentofile.yaml, regroupe tout ce dont l'API a besoin, et crée ce qu'on appelle un Bento. Ce Bento peut ensuite être transformé automatiquement en une image Docker.

Étape 3 : Conteneurisation (Standardisation)

La conteneurisation est le processus de mise en exécution de votre application dans un conteneur.

    Le Rôle de Docker : Docker est l'outil de conteneurisation le plus populaire. L'image Docker créée à l'étape précédente est un package léger, portable et autonome qui contient tout le nécessaire pour exécuter votre API (le code, les dépendances, le système d'exploitation minimal, etc.).

    La Commande : Vous utilisez la commande docker run pour lancer un conteneur à partir de votre image. Ce conteneur est un environnement isolé, ce qui garantit que votre API fonctionnera de la même manière sur n'importe quel ordinateur, quel que soit son environnement.

Étape 4 : Déploiement dans le Cloud (Mise en production)

C'est la dernière étape pour rendre votre API accessible au public via Internet.

    Le Processus : Le déploiement dans le Cloud (par exemple, sur Google Cloud Run, AWS Fargate ou Azure Container Apps) se déroule généralement en deux parties :

        Envoi de l'image : Vous poussez votre image Docker vers un registre de conteneurs dans le Cloud (comme Google Container Registry).

        Déploiement du service : Vous utilisez le service de votre fournisseur Cloud qui récupère votre image du registre et la lance en tant que service web. Ces services gèrent automatiquement le reste : la mise à l'échelle automatique (scaling), l'équilibrage de charge (load balancing), et la surveillance de la santé de l'application.

