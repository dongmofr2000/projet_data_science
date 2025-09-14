import pytest
import requests
import json
import os

# L'URL de votre API. Utilisez le port 3000 par défaut de BentoML.
API_URL = "http://localhost:3000/predict_single"

# Données valides pour tester la prédiction
VALID_DATA_PREDICTION = {
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

# --- Tests de cohérence des données ---
def test_valid_data_coherence():
    """Teste une requête avec des données logiquement cohérentes."""
    response = requests.post(API_URL, json=VALID_DATA_PREDICTION)
    assert response.status_code == 200

def test_inconsistent_gfa_data():
    """
    Teste une incohérence logique : PropertyGFATotal est plus petit que PropertyGFAParking.
    Ce test nécessite le validateur de modèle que vous avez ajouté dans votre classe Building.
    """
    inconsistent_data = {
        **VALID_DATA_PREDICTION,
        "PropertyGFATotal": 4000.0,  # Plus petit que le parking
        "PropertyGFAParking": 5000.0
    }
    response = requests.post(API_URL, json=inconsistent_data)
    assert response.status_code == 422
    response_data = response.json()
    assert "data_coherence_error" in str(response_data)

# --- Tests de performance du modèle ---
def test_prediction_is_reasonable():
    """
    Teste si la prédiction de consommation d'énergie est dans une plage raisonnable.
    """
    response = requests.post(API_URL, json=VALID_DATA_PREDICTION)
    
    assert response.status_code == 200
    response_data = response.json()
    
    # Vérifie que les champs de prédiction sont présents
    assert "prediction" in response_data
    assert "consommation_energie_kBtu" in response_data["prediction"]

    # Récupère la valeur prédite
    predicted_energy = response_data["prediction"]["consommation_energie_kBtu"]
    
    # Vérifie que la prédiction est dans une plage attendue
    assert 50000 < predicted_energy < 5000000

    # Teste également la prédiction des émissions de GES
    assert "emission_ges" in response_data["prediction"]
    predicted_ges = response_data["prediction"]["emission_ges"]
    assert 100 < predicted_ges < 10000

---
### **Ajout : Teste et affiche la prédiction**

def test_and_print_prediction():
    """
    Fait un appel à l'API, vérifie que la réponse est valide et imprime les valeurs prédites.
    Ce n'est pas un test avec un résultat attendu spécifique, mais une vérification visuelle.
    """
    print("\n--- Exécution du test de prédiction et affichage du résultat ---")
    try:
        response = requests.post(API_URL, json=VALID_DATA_PREDICTION)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP

        # Vérifie que la réponse est réussie
        assert response.status_code == 200
        response_data = response.json()
        
        # Affiche les valeurs prédites
        predicted_energy = response_data['prediction']['consommation_energie_kBtu']
        predicted_ges = response_data['prediction']['emission_ges']

        print("\nPrédiction réussie !")
        print("-" * 50)
        print(f"Consommation d'énergie (kBtu) : {predicted_energy:.2f}")
        print(f"Émissions de GES (tonnes) : {predicted_ges:.2f}")
        print("-" * 50)

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Échec de l'appel à l'API : {e}")
