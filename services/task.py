"""
Module de gestion des tâches (Le "Cerveau" des opérations).

Ce fichier contient la logique "métier". C'est ici que l'on décide quoi faire avec les données.
Imaginez que ce fichier est le **gestionnaire** ou l'artisan qualifié :
- L'API (le guichet) reçoit une demande du client.
- Elle transmet cette demande ici.
- Ce fichier effectue le travail réel : il calcule, vérifie et parle à la base de données (l'entrepôt) pour sauvegarder ou récupérer les informations.

C'est l'intermédiaire indispensable entre la demande de l'utilisateur et le stockage des données.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.task import TaskCreate
from database.models import Task


class TaskService:
    """
    Le Gestionnaire de Tâches.

    Cette classe regroupe toutes les actions possibles sur les tâches.
    C'est comme une boîte à outils spécialisée qui contient les instructions pour :
    - Créer une tâche.
    - Lire une tâche.
    - Modifier une tâche.
    - Supprimer une tâche.
    """

    def __init__(self, session: AsyncSession):
        """
        Démarrage du service.

        Pour travailler, ce service a besoin d'un accès à la base de données.
        On lui donne ici une "session" (une connexion active), un peu comme on donnerait
        les clés de l'entrepôt au magasinier pour qu'il puisse aller chercher les cartons.
        """
        self.session = session

    async def get_task(self, id: int) -> Task:
        """
        Trouver une tâche.

        Cette fonction cherche une tâche spécifique dans la base de données en utilisant son numéro unique (ID).
        C'est comme chercher un dossier dans une armoire en utilisant son numéro de référence.
        """
        return await self.session.get(Task, id)

    async def add_task(self, task_create: TaskCreate) -> Task:
        """
        Ajouter une nouvelle tâche.

        Cette fonction prend les informations fournies par l'utilisateur (titre, description...),
        crée une nouvelle fiche "Tâche", et l'enregistre dans la base de données pour ne pas la perdre.
        """
        new_task = Task(**task_create.model_dump())

        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)

        return new_task

    async def update_task(self, id: int, task_update: dict) -> Task:
        """
        Modifier une tâche existante.

        Cette fonction récupère une tâche déjà enregistrée et change certaines informations
        (par exemple, changer le statut de "à faire" à "terminé").
        Ensuite, elle sauvegarde les modifications.
        """
        task = await self.get_task(id)
        task.sqlmodel_update(task_update)

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete_task(self, id: int) -> None:
        """
        Supprimer une tâche.

        Cette fonction retire définitivement une tâche de la base de données.
        C'est comme passer le dossier à la déchiqueteuse : on ne pourra plus le récupérer.
        """
        await self.session.delete(await self.get_task(id))
        await self.session.commit()
