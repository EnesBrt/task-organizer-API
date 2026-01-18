"""
Point d'entrée principal de l'application (Main).

Ce fichier est le cœur de l'application. C'est ici que tout commence.
Imaginez ce fichier comme le chef d'orchestre qui :
1. Démarre l'application.
2. Prépare la base de données (crée les tables pour ranger les informations).
3. Connecte les différentes routes (les chemins pour accéder aux fonctionnalités).
4. Met à disposition une page de documentation pour comprendre comment utiliser l'API.

Même sans savoir coder, il suffit de comprendre que c'est le fichier qui lance le serveur web.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from api.router import router
from database.session import create_db_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application.

    Cette fonction est un peu spéciale : elle s'exécute automatiquement au démarrage et à l'arrêt de l'application.
    - **Au démarrage** : Elle s'assure que la base de données est prête (création des tables si elles n'existent pas).
    - **Pendant l'exécution** : Elle laisse l'application tourner (c'est le `yield`).

    C'est comme vérifier que les fondations de la maison sont là avant de laisser les gens entrer.
    """
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    """
    Page de documentation interactive.

    Cette fonction crée une page web accessible via `/scalar`.
    C'est un manuel d'utilisation visuel pour l'API. Elle permet de voir quelles actions sont possibles
    (créer une tâche, lire une tâche, etc.) et de les tester directement.
    """
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar API")
