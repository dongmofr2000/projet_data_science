from fastapi import FastAPI
import pandas as pd
from typing import List, Dict, Any

# Initialise une instance de l'application FastAPI
app = FastAPI(
    title="API de Données de Seattle",
    description="Une API pour accéder aux données du fichier 'DONNEES SEATTLE.csv'."
)

# Définit un chemin d'accès au fichier CSV. Assurez-vous que ce fichier se trouve dans le même dossier que service.py.
DATA_FILE = "DONNEES SEATTLE.csv"

# Endpoint de la page d'accueil de l'API
@app.get("/")
def read_root():
    """
    Retourne un message de bienvenue à la racine de l'API.
    """
    return {"message": "Bienvenue sur l'API de données de Seattle ! Accédez aux données via le chemin /data."}

# Endpoint pour lire et retourner les premières lignes du fichier CSV
@app.get("/data", response_model=List[Dict[str, Any]])
def get_data_head():
    """
    Charge les données du fichier CSV et retourne les 5 premières lignes.
    """
    try:
        # Tente de lire le fichier CSV
        df = pd.read_csv(DATA_FILE)
        
        # Convertit les 5 premières lignes en un dictionnaire de listes pour la réponse JSON
        # Utilisez .to_dict(orient='records') pour obtenir une liste d'objets JSON
        records = df.head().to_dict(orient='records')
        
        return records
    except FileNotFoundError:
        # Gère l'erreur si le fichier n'est pas trouvé
        return {"error": f"Le fichier {DATA_FILE} n'a pas été trouvé. Veuillez vous assurer qu'il se trouve dans le même répertoire."}
    except Exception as e:
        # Gère toute autre erreur
        return {"error": f"Une erreur s'est produite lors du chargement des données : {e}"}

# Vous pouvez ajouter d'autres endpoints pour filtrer les données, rechercher des enregistrements, etc.
# Par exemple, pour un endpoint qui retourne les données d'une année spécifique :
@app.get("/data/year/{year}", response_model=List[Dict[str, Any]])
def get_data_by_year(year: int):
    """
    Charge les données du fichier CSV et retourne tous les enregistrements pour une année donnée.
    """
    try:
        df = pd.read_csv(DATA_FILE)
        
        # Filtre le DataFrame pour ne garder que les lignes de l'année spécifiée
        filtered_df = df[df['DataYear'] == year]
        
        if filtered_df.empty:
            return {"message": f"Aucune donnée trouvée pour l'année {year}."}
        
        records = filtered_df.to_dict(orient='records')
        
        return records
    except FileNotFoundError:
        return {"error": f"Le fichier {DATA_FILE} n'a pas été trouvé."}
    except Exception as e:
        return {"error": f"Une erreur s'est produite lors du filtrage des données : {e}"}








