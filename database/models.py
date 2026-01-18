"""
Module de définition des "Plans" de données (Les Modèles).

Ce fichier sert de plan d'architecte pour la base de données.
Il explique à l'ordinateur comment structurer et ranger les informations.

Imaginez que la base de données est un grand classeur Excel.
Ce fichier définit les colonnes de ce classeur :
- Qu'est-ce qu'une "Tâche" ?
- Quelles informations doit-on garder pour chaque tâche (Titre, Description...) ?

C'est ici que l'on crée le "moule" qui servira à fabriquer toutes les futures tâches.
"""

from enum import Enum
from sqlalchemy import Enum as SAEnum
from sqlmodel import SQLModel, Field


class Status_Task(str, Enum):
    """
    Les étiquettes de statut autorisées (Le Menu Déroulant).

    Cette liste définit les seules options possibles pour l'état d'une tâche.
    C'est une sécurité : on oblige l'utilisateur à choisir parmi ces choix précis
    (À faire, En cours, Terminé) plutôt que de le laisser écrire n'importe quoi.
    """

    to_do = "to_do"
    in_progress = "in_progress"
    completed = "completed"


class Task(SQLModel, table=True):
    """
    Le plan de construction d'une Tâche (Le Formulaire).

    Cette classe décrit la fiche d'identité d'une tâche.
    Elle liste toutes les cases qu'il faut remplir pour créer une tâche valide :
    - Un numéro unique (ID) pour la retrouver.
    - Un titre et une description pour savoir ce qu'il faut faire.
    - Un statut pour savoir où ça en est.
    - Un responsable (assignee) pour savoir qui travaille dessus.
    """

    __tablename__ = "task"

    id: int = Field(default=None, primary_key=True)
    title: str
    description: str
    status: Status_Task = Field(
        sa_type=SAEnum(Status_Task, native_enum=False), default=Status_Task.to_do
    )
    assignee: str
