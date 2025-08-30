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