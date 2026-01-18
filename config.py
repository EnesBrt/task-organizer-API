"""
Module de configuration de l'application.

Ce fichier sert de "panneau de configuration" pour l'application.
C'est ici que l'on définit comment l'application doit se comporter et où elle doit aller chercher ses informations sensibles, comme les mots de passe.

Imaginez que c'est le carnet d'adresses sécurisé de l'application :
il lit un fichier caché (appelé `.env`) pour savoir comment se connecter à la base de données sans écrire les mots de passe directement dans le code visible par tous.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """
    Paramètres de la base de données.

    Cette classe liste toutes les informations nécessaires pour que l'application puisse "téléphoner" à la base de données :
    - L'adresse du serveur (où elle habite).
    - Le port (la porte d'entrée).
    - L'utilisateur et le mot de passe (la clé pour entrer).
    - Le nom de la base de données (le dossier spécifique à ouvrir).
    """

    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_DB: str

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    @property
    def POSTGRES_URL(self):
        """
        Construit l'adresse complète de connexion.

        Cette fonction prend tous les morceaux d'informations (utilisateur, mot de passe, adresse, etc.)
        et les assemble pour former une phrase complète (une URL) que l'ordinateur comprend pour établir la connexion.
        """
        return f"postgresql+asyncpg://{self.POSTGRES_USER}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = DatabaseSettings()
