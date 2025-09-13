import bentoml
from fastapi import FastAPI
from pydantic import BaseModel, Field, PositiveFloat
import pandas as pd
from typing import List, Dict, Any, Optional
import json

# Chargez les données une seule fois
try:
    df = pd.read_csv("DONNEES SEATTLE.csv")
except FileNotFoundError:
    # Gérer l'erreur si le fichier n'est pas trouvé
    df = pd.DataFrame()

# Créez l'application FastAPI
app = FastAPI(
    title="API de Données de Seattle",
    description="Une API pour accéder aux données du fichier 'DONNEES SEATTLE.csv'."
)

# Définissez le service BentoML et montez l'application FastAPI
svc = bentoml.Service(
    name="seattle-data-api"
)
svc.mount_asgi_app(app)

# Définissez une classe Pydantic pour valider le schéma de données
# J'ai ajouté des règles de validation plus strictes pour empêcher les incohérences
class BuildingData(BaseModel):
    OSEBuildingID: int = Field(..., description="ID unique du bâtiment")
    DataYear: int = Field(..., ge=2016, le=2023, description="Année des données, doit être >= 2016")
    BuildingType: str = Field(..., min_length=1, description="Type de bâtiment")
    PrimaryPropertyType: str = Field(..., min_length=1, description="Type de propriété principal")
    PropertyName: str = Field(..., min_length=1, description="Nom de la propriété")
    Address: str = Field(..., min_length=1, description="Adresse de la propriété")
    # GHGEmissionsIntensity est un champ optionnel, et doit être un nombre positif
    GHGEmissionsIntensity: Optional[PositiveFloat] = None
    
# Ajoutez des points d'accès à l'API
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de données de Seattle !"}

@app.get("/data", response_model=List[Dict[str, Any]])
def get_data_head():
    if df.empty:
        return {"error": "Le jeu de données est vide."}
    records = df.head().to_dict(orient='records')
    return records

@app.get("/data/year/{year}", response_model=List[Dict[str, Any]])
def get_data_by_year(year: int):
    if df.empty:
        return {"error": "Le jeu de données est vide."}
    filtered_df = df[df['DataYear'] == year]
    if filtered_df.empty:
        return {"message": f"Aucune donnée trouvée pour l'année {year}."}
    records = filtered_df.to_dict(orient='records')
    return records

@app.post("/data/submit")
def submit_new_building_data(building_data: BuildingData):
    return {
        "message": "Données de bâtiment reçues et validées avec succès !",
        "data_received": building_data.dict()
    }
    
    Création de la classe de prédiction
    
    import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer

class EnergyConsumptionPredictor:
    """
    Une classe pour encapsuler le pipeline de modélisation
    et faire des prédictions sur la consommation d'énergie.
    """
    def __init__(self, modele_entraine):
        self.modele = modele_entraine

    def predict(self, nouvelles_donnees):
        """
        Fait une prédiction sur de nouvelles données.

        Args:
            nouvelles_donnees (pd.DataFrame): DataFrame contenant les
                                             features pour la prédiction.

        Returns:
            float: La prédiction de la consommation d'énergie en kBtu.
        """
        # S'assurer que les nouvelles données sont un DataFrame
        if not isinstance(nouvelles_donnees, pd.DataFrame):
            nouvelles_donnees = pd.DataFrame(nouvelles_donnees)

        # Faire la prédiction avec le pipeline
        # La prédiction est sur l'échelle logarithmique
        prediction_log = self.modele.predict(nouvelles_donnees)

        # Reconvertir la prédiction à l'échelle originale (kBtu)
        prediction_originale = np.expm1(prediction_log)

        return prediction_originale[0]

# Assurez-vous d'avoir entraîné votre modèle et qu'il est stocké dans
# la variable `modele_pipeline` ou `modele_random_forest` si vous avez
# utilisé ce modèle
# Par exemple, si vous avez utilisé le Gradient Boosting
# modele_entraine = modele_pipeline

# Vous pouvez également utiliser le meilleur modèle issu de votre GridSearchCV
# modele_entraine = grid_search_large.best_estimator_

# Exemple d'utilisation de la classe
# Remplacez les valeurs ci-dessous par de nouvelles données de bâtiment
nouvelles_donnees = {
    'PropertyGFABuilding(s)': [150000],
    'NumberOfBuildings': [1],
    'NumberofFloors': [5],
    'PropertyGFAParking': [5000],
    'AgeDuBatiment': [20],
    'NombreDeTypesUsage': [2],
    'PresenceElectricite': [1],
    'PresenceGazNaturel': [1],
    'PresenceVapeur': [0],
    'PrimaryPropertyType': ['Office'],
    'PropertyUseType': ['Office']
}

# Créer une instance de la classe avec votre modèle entraîné
# NOTE : remplacez `modele_random_forest` par le nom de la variable
# contenant votre meilleur modèle
predictor = EnergyConsumptionPredictor(modele_random_forest)

# Obtenir la prédiction
prediction = predictor.predict(nouvelles_donnees)

print(f"La prédiction de la consommation d'énergie est de {prediction:,.2f} kBtu.")


les décorateurs nécessaires pour identifier le service et ses endpoints

from flask import Flask, request

# 1. Le décorateur de l'application
# Il instancie l'application et la prépare à gérer les requêtes.
app = Flask(__name__)

# 2. Le décorateur de l'endpoint
# Il lie le chemin d'accès ('/') à la fonction 'home()'.
@app.route('/')
def home():
    return "Bienvenue sur l'accueil !"

# Un autre endpoint pour un chemin différent
@app.route('/salut')
def salut():
    return "Salut, c'est un autre endpoint !"

# Un endpoint avec des méthodes HTTP spécifiques
@app.route('/donnees', methods=['GET', 'POST'])
def donnees():
    if request.method == 'POST':
        return "Données reçues via une requête POST."
    else:
        return "Ceci est le point d'accès pour les requêtes GET."

if __name__ == '__main__':
    app.run(debug=True)

