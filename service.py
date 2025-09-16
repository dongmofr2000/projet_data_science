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
    


import bentoml
import pandas as pd
from bentoml.io import JSON
from pydantic import BaseModel, Field, ValidationError
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional, List
import bentoml
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional

class Building(BaseModel):
    DataYear: int = 2017
    BuildingType: str
    PrimaryPropertyType: str
    SecondLargestPropertyUseType: Optional[str]
    ThirdLargestPropertyUseType: Optional[str]
    ZipCode: str
    CouncilDistrictCode: int
    Neighborhood: str
    YearBuilt: int
    NumberofBuildings: int
    NumberofFloors: int
    PropertyGFATotal: float
    PropertyGFAParking: float
    ListOfAllPropertyUseTypes: str
    LargestPropertyUseType: str

    @field_validator('CouncilDistrictCode')
    @classmethod
    def validate_council_district(cls, CouncilDistrictCode: int) -> int:
        if not (0 < CouncilDistrictCode < 8):
            raise PydanticCustomError(
                'validation_error',
                'Le district doit être entre 1 et 7.',
            )
        return CouncilDistrictCode

    @field_validator('YearBuilt')
    @classmethod
    def validate_year(cls, YearBuilt: int) -> int:
        if YearBuilt < 1850 or YearBuilt > 2025:
            raise PydanticCustomError(
                'validation_error',
                'L\'année de construction est invalide.',
            )
        return YearBuilt

    @field_validator('NumberofFloors')
    @classmethod
    def validate_floors(cls, NumberofFloors: int) -> int:
        if NumberofFloors <= 0:
            raise PydanticCustomError(
                'validation_error',
                'Le nombre d\'étages doit être supérieur à 0.',
            )
        return NumberofFloors

    @field_validator('NumberofBuildings')
    @classmethod
    def validate_buildings(cls, NumberofBuildings: int) -> int:
        if NumberofBuildings <= 0:
            raise PydanticCustomError(
                'validation_error',
                'Le nombre de bâtiments doit être supérieur à 0.',
            )
        return NumberofBuildings

class BuildingList(BaseModel):
    buildings: List[Building]


# --- Définition des schémas de données pour l'API ---
class InputData(BaseModel):
    NumberofFloors: int
    LargestPropertyuseTypeGFA: float
    SecondLargestPropertyuseTypeGFA: Optional[float]
    ENERGYSTARScore: Optional[int]
    SteamUse_kBtu: Optional[float] = Field(None, alias="Steamused")
    NaturalGas_therms: Optional[float] = Field(None, alias="NaturalGasused")
    PrimaryPropertyType: str
    Neighborhood: str

# --- Définition du service BentoML ---
@bentoml.service(name="building_energy_predictor")
class Prediction:
    def __init__(self) -> None:
        """Charge le modèle enregistré."""
        self.pipeline = bentoml.sklearn.load_model("energy_pipeline:latest")
        
        # Définition de toutes les colonnes attendues par le modèle
        self.expected_columns = [
            'OSEBuildingID', 'DataYear', 'BuildingType', 'PrimaryPropertyType', 'PropertyName', 'Address', 'City', 
            'State', 'ZipCode', 'TaxParcelIdentificationNumber', 'CouncilDistrictCode', 'Neighborhood', 'Latitude', 
            'Longitude', 'YearBuilt', 'NumberofBuildings', 'NumberofFloors', 'PropertyGFATotal', 'PropertyGFAParking', 
            'PropertyGFABuilding(s)', 'ListOfAllPropertyUseTypes', 'LargestPropertyUseType', 'LargestPropertyUseTypeGFA', 
            'SecondLargestPropertyUseType', 'SecondLargestPropertyUseTypeGFA', 'ThirdLargestPropertyUseType', 
            'ThirdLargestPropertyUseTypeGFA', 'YearsENERGYSTARCertified', 'ENERGYSTARScore', 'SiteEUI(kBtu/sf)', 
            'SiteEUIWN(kBtu/sf)', 'SourceEUI(kBtu/sf)', 'SourceEUIWN(kBtu/sf)', 'SiteEnergyUse(kBtu)', 'SiteEnergyUseWN(kBtu)', 
            'SteamUse(kBtu)', 'Electricity(kWh)', 'Electricity(kBtu)', 'NaturalGas(therms)', 'NaturalGas(kBtu)', 
            'DefaultData', 'Comments', 'ComplianceStatus', 'Outlier', 'TotalGHGEmissions', 'GHGEmissionsIntensity'
        ]

    # Le décorateur est ajusté pour une compatibilité maximale
    @bentoml.api
    def predict(self, input_data: InputData) -> dict:
        # Pydantic valide l'entrée automatiquement, donc pas besoin de 'try/except'
        
        full_data = {col: None for col in self.expected_columns}
        
        # Met à jour le dictionnaire avec les données de la requête
        full_data.update(input_data.dict())

        df = pd.DataFrame([full_data])
        
        df['PrimaryPropertyType'] = df['PrimaryPropertyType'].fillna('').str.lower()
        df['Neighborhood'] = df['Neighborhood'].fillna('').str.lower()

        prediction = self.pipeline.predict(df)[0]
        
        return {"prediction (kBtu)": round(float(prediction), 2)}


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



