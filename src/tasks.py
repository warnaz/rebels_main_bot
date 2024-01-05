import asyncio
import datetime 
import random
from typing import List
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from database.models import ActionWallet, CRUD, Client, Tasks, Wallet, Project, Route, Action
from start_actions import run_actions


async def get_data_task(crud, tasks_list: List[Tasks]) -> list:
    data = []

    for task in tasks_list:
        client = await crud.get(task.client_id, Client)
        wallet = await crud.get(task.wallet_id, Wallet)
        project = await crud.get(task.project_id, Project)
        route = await crud.get(task.route_id, Route)
        action = await crud.get(task.action_id, Action)
        action_wallet = await crud.get(task.action_wallet_id, ActionWallet)

        data.append({
            "client": client,
            "wallet": wallet,
            "project": project,
            "route": route,
            "action": action,
            "action_wallet": action_wallet
        })
 
    return data


async def run_action_tasks(scheduler: AsyncIOScheduler):
    # Выполнение оставшихся действий, до перезагрузки бота

    crud = CRUD()
    tasks_list: List[Tasks] = await crud.get_all_active_tasks()

    if not tasks_list:
        logger.info("No active tasks")
        return

    data: list = await get_data_task(crud, tasks_list)

    for task in data:
        action_wallet = task.get("action_wallet")
        route_id = task.get("route").id

        scheduler.add_job(run_actions, 'date', run_date=action_wallet.estimated_time, kwargs=task, misfire_grace_time=10000)    


total = 0


async def add_starknet_action_task(scheduler: AsyncIOScheduler, **kwargs):
    global total
    total += 1

    action_wallet: ActionWallet = kwargs.get("action_wallet")
    scheduler.add_job(run_actions, 'date', run_date=action_wallet.estimated_time, kwargs=kwargs, misfire_grace_time=10000)
