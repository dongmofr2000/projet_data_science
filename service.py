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
    
     
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional, List

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

# Modèle pour l'OUTPUT de l'API
class PredictionResult(BaseModel):
    consommation_energie_kBtu: float
    emission_ges: float
    statut_code: int = 200
    message: str = "Prédiction réussie"





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



Créer le script service.py pour la prédiction


import bentoml
import pandas as pd
from bentoml.io import JSON
from pydantic import BaseModel, Field
from typing import Optional

# --- Définition des schémas de données pour l'API ---
class Building(BaseModel):
    OSEBuildingID: Optional[int] = None
    DataYear: Optional[int] = None
    BuildingType: Optional[str] = None
    PrimaryPropertyType: Optional[str] = None
    PropertyName: Optional[str] = None
    Address: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    ZipCode: Optional[int] = None
    TaxParcelIdentificationNumber: Optional[str] = None
    CouncilDistrictCode: Optional[int] = None
    Neighborhood: Optional[str] = None
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None
    YearBuilt: Optional[int] = None
    NumberofBuildings: Optional[int] = None
    NumberofFloors: Optional[int] = None
    PropertyGFATotal: Optional[int] = None
    PropertyGFAParking: Optional[int] = None
    PropertyGFABuilding_s: Optional[int] = Field(None, alias='PropertyGFABuilding(s)')
    ListOfAllPropertyUseTypes: Optional[str] = None
    LargestPropertyUseType: Optional[str] = None
    LargestPropertyUseTypeGFA: Optional[float] = None
    SecondLargestPropertyUseType: Optional[str] = None
    SecondLargestPropertyUseTypeGFA: Optional[float] = None
    ThirdLargestPropertyUseType: Optional[str] = None
    ThirdLargestPropertyUseTypeGFA: Optional[float] = None
    YearsENERGYSTARCertified: Optional[str] = None
    ENERGYSTARScore: Optional[int] = None
    SiteEUI_kBtu_sf: Optional[float] = Field(None, alias='SiteEUI(kBtu/sf)')
    SourceEUI_kBtu_sf: Optional[float] = Field(None, alias='SourceEUI(kBtu/sf)')
    SteamUse_kBtu: Optional[float] = Field(None, alias='SteamUse(kBtu)')
    Electricity_kWh: Optional[float] = Field(None, alias='Electricity(kWh)')
    NaturalGas_therms: Optional[float] = Field(None, alias='NaturalGas(therms)')
    
class PredictionResult(BaseModel):
    consommation_energie_kBtu: float
    emission_ges: float

# --- Définition du service BentoML ---
@bentoml.service(name="building_energy_predictor")
class BuildingPredictorService:
    def __init__(self):
        self.energy_pipeline = bentoml.sklearn.load_model("energy_pipeline")
        self.ges_pipeline = bentoml.sklearn.load_model("ges_pipeline")
        self.features = [
            'OSEBuildingID', 'DataYear', 'BuildingType', 'PrimaryPropertyType', 'PropertyName', 'Address', 'City', 'State', 'ZipCode', 'TaxParcelIdentificationNumber', 'CouncilDistrictCode', 'Neighborhood', 'Latitude', 'Longitude', 'YearBuilt', 'NumberofBuildings', 'NumberofFloors', 'PropertyGFATotal', 'PropertyGFAParking', 'PropertyGFABuilding(s)', 'ListOfAllPropertyUseTypes', 'LargestPropertyUseType', 'LargestPropertyUseTypeGFA', 'SecondLargestPropertyUseType', 'SecondLargestPropertyUseTypeGFA', 'ThirdLargestPropertyUseType', 'ThirdLargestPropertyUseTypeGFA', 'YearsENERGYSTARCertified', 'ENERGYSTARScore', 'SiteEUI(kBtu/sf)', 'SourceEUI(kBtu/sf)', 'SteamUse(kBtu)', 'Electricity(kWh)', 'NaturalGas(therms)'
        ]

    @bentoml.api(input=JSON(pydantic_model=Building), output=JSON(pydantic_model=PredictionResult))
    def predict(self, input_data: Building) -> PredictionResult:
        input_df = pd.DataFrame([input_data.model_dump(by_alias=True)])

        # Assurez-vous que le DataFrame d'entrée a toutes les colonnes attendues
        input_df = input_df.reindex(columns=self.features, fill_value=None)

        energy_use = self.energy_pipeline.predict(input_df)[0]
        total_ges = self.ges_pipeline.predict(input_df)[0]

        return PredictionResult(
            consommation_energie_kBtu=round(float(energy_use), 2),
            emission_ges=round(float(total_ges), 2)
        )

