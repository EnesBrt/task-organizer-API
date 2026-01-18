"""
Module de gestion des outils (Le Magasinier).

Ce fichier sert à préparer et fournir automatiquement les outils nécessaires pour travailler.
C'est ce qu'on appelle l'injection de dépendances.

Imaginez un chirurgien (l'API) qui opère. Il ne va pas chercher ses scalpels lui-même.
Il tend la main et une infirmière (ce fichier) lui donne exactement l'outil dont il a besoin au bon moment.

Ici, on prépare deux choses principales :
1. L'accès à la base de données (la clé de l'entrepôt).
2. Le service de gestion des tâches (l'expert qualifié).
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_session
from services.task import TaskService


# La demande de clé (Le Passe-Partout).
# C'est une étiquette spéciale. Quand on la met sur une fonction,
# le système comprend qu'il doit d'abord aller chercher une connexion active
# à la base de données (via get_session) avant de lancer la fonction.
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_task_service(session: SessionDep) -> TaskService:
    """
    Le Recruteur (Préparateur de Service).

    Cette fonction prépare l'expert qui va gérer les tâches.
    Pour travailler, cet expert (TaskService) a besoin d'accéder aux dossiers (la session).

    Cette fonction fait donc l'assemblage :
    1. Elle prend la clé de la base de données (session).
    2. Elle la donne au gestionnaire de tâches.
    3. Elle renvoie le gestionnaire prêt à travailler.
    """
    return TaskService(session)


# L'Expert prêt à l'emploi.
# C'est le raccourci magique. Si une partie du code a besoin de gérer des tâches,
# elle utilise cette étiquette. Le système lui fournira alors automatiquement
# un TaskService tout prêt, déjà connecté à la base de données.
ServiceDep = Annotated[TaskService, Depends(get_task_service)]
