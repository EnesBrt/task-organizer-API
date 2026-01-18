"""
Module de connexion à la base de données (Le "Tuyau").

Ce fichier gère la communication technique entre l'application et la base de données.
Imaginez que c'est le service de télécommunications :
1. Il établit la ligne téléphonique (le moteur).
2. Il vérifie que les meubles de rangement sont bien là (création des tables).
3. Il distribue des combinés téléphoniques temporaires (sessions) pour chaque conversation.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from sqlmodel import SQLModel

from config import settings

# create a database engine to connect to the database
# C'est le moteur principal : la ligne directe permanente vers le serveur de données.
engine = create_async_engine(
    url=settings.POSTGRES_URL,
    echo=True,
)


async def create_db_tables():
    """
    L'Architecte / Le Constructeur.

    Cette fonction est appelée au démarrage de l'application.
    Son rôle est simple :
    1. Elle entre dans la base de données.
    2. Elle regarde si la table pour ranger les tâches existe déjà.
    3. Si elle n'existe pas, elle la construit (crée la table).
    4. Si elle existe déjà, elle ne fait rien (pour ne pas écraser les données existantes).

    C'est comme vérifier qu'il y a bien une armoire avant d'essayer de ranger des dossiers dedans.
    """
    async with engine.begin() as conection:
        from database.models import Task

        # check if table already exist
        def check_table_exists(conn):
            return inspect(conn).has_table(Task.__tablename__)

        if not await conection.run_sync(check_table_exists):
            await conection.run_sync(SQLModel.metadata.create_all)
        else:
            print("Table already exists")


# La fabrique de sessions : c'est la machine qui crée les tickets d'accès.
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    """
    Le Guichetier (Fournisseur d'accès).

    Cette fonction est utilisée à chaque fois qu'une demande arrive (par exemple, "montre-moi les tâches").
    Elle :
    1. Ouvre une connexion temporaire (une session).
    2. La prête le temps de faire le travail (le `yield`).
    3. La referme proprement une fois le travail fini, même s'il y a eu une erreur.
    """
    async with async_session() as session:
        yield session
