import pytest
import requests
import json

# L'URL de votre API locale. Assurez-vous que votre service est bien lancé.
API_URL = "http://localhost:3000/predict_single"

# Données valides pour un test réussi
VALID_DATA = {
    "DataYear": 2016,
    "BuildingType": "Commercial",
    "PrimaryPropertyType": "Office",
    "SecondLargestPropertyUseType": "Other",
    "ThirdLargestPropertyUseType": None,
    "ZipCode": "98101",
    "CouncilDistrictCode": 7,
    "Neighborhood": "DOWNTOWN",
    "YearBuilt": 1980,
    "NumberofBuildings": 1,
    "NumberofFloors": 10,
    "PropertyGFATotal": 150000.0,
    "PropertyGFAParking": 5000.0,
    "ListOfAllPropertyUseTypes": "Office, Other",
    "LargestPropertyUseType": "Office"
}

# Données invalides pour tester les validations
INVALID_DATA_NEG_GFA = {
    **VALID_DATA,  # On reprend les données valides...
    "PropertyGFATotal": -100.0 # ... et on insère une valeur invalide
}

INVALID_DATA_NEG_PARKING = {
    **VALID_DATA,
    "PropertyGFAParking": -50.0
}

INVALID_DATA_COUNCIL_DISTRICT = {
    **VALID_DATA,
    "CouncilDistrictCode": 99 # Une valeur hors de la plage 0-8
}

def test_valid_data_prediction():
    """Teste une requête avec des données valides. Le statut attendu est 200."""
    response = requests.post(API_URL, json=VALID_DATA)
    
    assert response.status_code == 200
    response_data = response.json()
    assert "prediction" in response_data
    assert "consommation d'énergie (kBtu)" in response_data["prediction"]


def test_invalid_property_gfa():
    """Teste la validation de PropertyGFATotal avec une valeur négative."""
    response = requests.post(API_URL, json=INVALID_DATA_NEG_GFA)
    
    assert response.status_code == 422
    response_data = response.json()
    assert "errors" in response_data
    assert "validation" in response_data["errors"]
    assert "PropertyGFATotal" in str(response_data)


def test_invalid_property_parking():
    """Teste la validation de PropertyGFAParking avec une valeur négative."""
    response = requests.post(API_URL, json=INVALID_DATA_NEG_PARKING)
    
    assert response.status_code == 422
    response_data = response.json()
    assert "errors" in response_data
    assert "validation" in response_data["errors"]
    assert "PropertyGFAParking" in str(response_data)


def test_invalid_council_district():
    """Teste la validation de CouncilDistrictCode avec une valeur hors plage."""
    response = requests.post(API_URL, json=INVALID_DATA_COUNCIL_DISTRICT)

    assert response.status_code == 422
    response_data = response.json()
    assert "errors" in response_data
    assert "validation" in response_data["errors"]
    assert "CouncilDistrictCode" in str(response_data)