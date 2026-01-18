"""
Module de définition des Schémas (Les Formulaires d'échange).

Ce fichier sert de "douane" ou de filtre pour les informations qui entrent et sortent de l'API.
Il définit la forme exacte que doivent avoir les données.

Imaginez des formulaires papier :
- Quand vous voulez créer une tâche, vous remplissez un formulaire spécifique.
- Quand l'ordinateur vous montre une tâche, il vous donne une fiche avec des informations supplémentaires (comme le numéro de dossier).

Ce fichier garantit que personne n'envoie d'informations incomplètes ou incorrectes.
"""

from pydantic import BaseModel, Field
from database.models import Status_Task


class BaseTask(BaseModel):
    """
    Le socle commun (Les informations de base).

    C'est la liste des informations qui sont toujours présentes, qu'on soit en train de créer
    ou de lire une tâche :
    - Le titre.
    - La description.
    - La personne responsable (assignee).
    """

    title: str
    description: str
    assignee: str


class TaskRead(BaseTask):
    """
    La fiche de lecture (Ce que l'utilisateur reçoit).

    C'est le format des données quand l'application répond à une demande.
    En plus des infos de base, elle inclut :
    - L'ID (le numéro unique du dossier).
    - Le statut (où en est la tâche).
    """

    id: int
    status: Status_Task


class TaskCreate(BaseTask):
    """
    Le formulaire de création (Ce que l'utilisateur envoie).

    C'est le formulaire vierge à remplir pour créer une nouvelle tâche.
    Il demande juste le strict nécessaire (Titre, Description, Responsable).
    """

    pass


class TaskUpdate(BaseModel):
    """
    Le formulaire de modification (Pour les mises à jour).

    Ce modèle est utilisé quand on veut changer quelque chose sur une tâche existante.
    Ici, il permet spécifiquement de mettre à jour le statut (par exemple pour dire qu'une tâche est finie).
    """

    status: Status_Task | None = Field(default=None)
