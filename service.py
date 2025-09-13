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
from bentoml.io import JSON
from bentoml import service
from pydantic import BaseModel, ValidationError

# On importe les modules de Scikit-learn
# Note: dans une vraie application, vous chargeriez ces objets depuis des fichiers
# comme dans votre code.

# Voici une classe simple pour les données d'entrée, inspirée par votre code
class BuildingData(BaseModel):
    # Liste simplifiée des features nécessaires pour la prédiction
    PropertyGFABuilding_s: float
    NumberofFloors: int
    AgeDuBatiment: int
    PropertyGFAParking: float
    PrimaryPropertyType: str
    
    # Configuration pour autoriser les types de données complexes
    class Config:
        arbitrary_types_allowed = True


# La classe de service qui fait la prédiction
@service
class SimpleBuildingPredictor:
    
    # C'est ici que l'on charge tous les objets nécessaires (modèles, pipelines, etc.)
    # Cette méthode est exécutée une seule fois au démarrage du service
    def __init__(self):
        # NOTE : Les lignes ci-dessous sont commentées car nous n'avons pas
        # les fichiers de votre modèle. Dans votre code, elles sont cruciales.
        # self.pipeline = pd.read_pickle("votre_pipeline.pkl")
        # self.model = pd.read_pickle("votre_modele.pkl")
        pass

    # Décorateur d'API pour créer un endpoint
    # On précise le type de données d'entrée (JSON) et son schéma (BuildingData)
    @bentoml.api(input=JSON(pydantic_model=BuildingData))
    def predict(self, input_data: BuildingData) -> dict:
        
        try:
            # Conversion des données de Pydantic en un DataFrame Pandas
            data_dict = input_data.model_dump()
            data_df = pd.DataFrame([data_dict])

            # Exemple d'application du pipeline et de la prédiction
            # Remplacez ceci par votre vraie logique de prédiction
            # transformed_data = self.pipeline.transform(data_df)
            # prediction = self.model.predict(transformed_data)
            
            # Exemple de résultat de prédiction simple pour la démonstration
            # On simule un résultat de prédiction ici
            prediction = [4242.42]

            # Reconvertir la prédiction à l'échelle d'origine si nécessaire
            # prediction_finale = np.expm1(prediction)
            
            return {
                "prediction": round(float(prediction[0]), 2),
                "status": "success",
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
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

