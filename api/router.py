"""
Module de définition des Routes (Le Standard Téléphonique / L'Aiguilleur).

Ce fichier est le point d'entrée des demandes externes.
Quand quelqu'un appelle l'API (par exemple via une application mobile ou un site web), c'est ici que l'appel arrive.
Ce fichier regarde ce que la personne veut faire (lire, créer, modifier, supprimer) et dirige la demande vers la bonne fonction.

C'est comme un menu de restaurant : il liste tout ce qu'il est possible de commander.
"""

from fastapi import APIRouter, HTTPException, status

from .dependencies import ServiceDep
from .schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/task", tags=["Task"])


@router.get("/", response_model=TaskRead)
async def get(id: int, service: ServiceDep):
    """
    La demande de consultation (Lire une tâche).

    L'utilisateur donne un numéro de ticket (ID), et on lui renvoie le dossier correspondant.
    Si le dossier n'existe pas, on lui dit qu'on ne l'a pas trouvé (Erreur 404).
    """
    task = await service.get_task(id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return task


@router.post("/", response_model=TaskRead)
async def create(task_create: TaskCreate, service: ServiceDep):
    """
    La demande de création (Nouvelle tâche).

    L'utilisateur envoie un formulaire rempli (titre, description...), et on crée un nouveau dossier.
    On renvoie ensuite le dossier créé avec son nouveau numéro unique.
    """
    return await service.add_task(task_create)


@router.patch("/", response_model=TaskRead)
async def update(id: int, task_update: TaskUpdate, service: ServiceDep):
    """
    La demande de modification (Mise à jour).

    L'utilisateur donne le numéro du dossier et ce qu'il veut changer (par exemple, le statut).
    On met à jour le dossier et on renvoie la version corrigée.
    """
    update_task = task_update.model_dump(exclude_unset=True)
    return await service.update_task(id, update_task)


@router.delete("/")
async def delete(id: int, service: ServiceDep):
    """
    La demande de suppression (Jeter un dossier).

    L'utilisateur donne le numéro du dossier à supprimer.
    On le détruit et on confirme que c'est fait.
    """
    await service.delete_task(id)
    return {"message": f"Task with ID {id} has been deleted successfully"}
