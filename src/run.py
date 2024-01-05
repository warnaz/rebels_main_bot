import asyncio
import json
import random
import urllib.parse

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from schema import (
    ListWalletScheme, 
    ProjectScheme, 
    RequestData, 
    AddAccountScheme,
)
from utils.prepare_data import get_data
from database.models import CRUD, Action, ActionWallet, Client, Project, Route, Tasks, Wallet
from tasks import run_action_tasks, add_starknet_action_task


# Запускаем планировщик задач
scheduler = AsyncIOScheduler()

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.on_event("startup")
# async def run_task_scheduler():
#     await run_action_tasks(scheduler)


@app.post("/route/")
async def route(request_data: ProjectScheme):    
    data = request_data.dict()
    project_name = data.get("project_name")

    route_dict = {} 

    crud = CRUD()
    project: Project = await crud.get_project(project_name)
    route_list: List[Route] = await crud.get_route_list(project_id=project.id)

    for route in route_list:
        action_list: List[Action] = await crud.get_route_actions(route_id=route.id)
        route_dict[route.route_name] = action_list
        route_dict[route.route_name].append(route.id)

    return route_dict


@app.post('/wallet/')
async def wallet(request_data: ListWalletScheme):
    data = request_data.dict()
    crud = CRUD()

    client_id = data.get("client_id")
    wallet_list: List[dict[Wallet]] = await crud.get_client_wallet(client_id)

    return wallet_list


@app.post('/add_account/')
async def add_account(request_data: AddAccountScheme):
    client = None 
    wallet = None 

    try:
        data = request_data.dict()
        crud = CRUD()
        
        client_id = data.get("client_id")
        starknet_key = data.get("starknet_key")
        evm_key = data.get("evm_key")
        wallet_name = data.get("wallet_name")

        client = await crud.get(client_id, Client)
        wallet = await crud.create_wallet(starknet_key, evm_key, wallet_name, client.id)
    except Exception as e:
        await crud.create_status(
            code=400,
            desc="ADD_ACCOUNT_ERROR: " + str(e),
            client=client,
            wallet=wallet
        )


async def get_user_id(init_data):
    if isinstance(init_data, int):
        return init_data
    
    params = init_data.split('&')

    data = {}
    
    for param in params:
        key, value = param.split('=')
        data[key] = urllib.parse.unquote(value)

    user_data = data['user']
    user_data = json.loads(user_data)
    user_id = user_data['id']

    return user_id


@app.post('/run_bot/')
async def run_bot(request_data: RequestData):
    data = request_data.dict()
    crud = CRUD()
    route, project, action_list, client, wallet, min_time, max_time, max_amount, gas, init_data = await get_data(crud, data)

    user_id = await get_user_id(init_data)
    logger.success(route.id)

    transaction_time = datetime.now()
    amount_for_action = max_amount / len(action_list)

    # if amount_for_action <= gas:
    #     raise Exception(f"Not enough balance. Gas = {gas}")

    act_wallet_list = []

    for item in action_list:
        number = random.randint(min_time, max_time)
        logger.info(f"Wait {number} minutes")
        transaction_time = transaction_time + timedelta(minutes=number)
        action: Action = await crud.get_single_action(route_id=route.id, act_list_id=item.id)

        # Создаем действия в базе
        action_wallet = await crud.create_action_wallet(
            status="WAIT",
            amount=amount_for_action,
            gas=gas,
            wallet_id=wallet.id,
            action_id=action.id,
            estimated_time=transaction_time
        )

        act_wallet_list.append(action_wallet.id)

    tasks_list = []

    for action_wallet in act_wallet_list:
        action_wallet_obj = await crud.get(action_wallet, ActionWallet)
        action = await crud.get(action_wallet_obj.action_id, Action)

        # Создаем задачи для каждого действия в базе
        task = await crud.create_tasks(
            status="WAIT",
            client=client.id, 
            wallet=wallet.id, 
            project=project.id, 
            route=route.id, 
            action=action.id,
            action_wallet=action_wallet_obj.id          
        )

        tasks_list.append(task.id) 

    index = 0
    for action_wallet in act_wallet_list:
        task = tasks_list[index]
        index += 1
        if index == 2:
            break

        task = await crud.get(task, Tasks)
        action_wallet_obj = await crud.get(action_wallet, ActionWallet)
        action = await crud.get(action_wallet_obj.action_id, Action)

        # Запускаем задачи для каждого действия в планировщике
        await add_starknet_action_task(
            scheduler=scheduler,
            crud=crud,
            data=data,
            client=client,
            wallet=wallet, 
            project=project, 
            route=route, 
            action=action,
            action_wallet=action_wallet_obj,
            task=task,
            user_id=user_id
        )

    if not scheduler.running:
        scheduler.start()

    scheduler.print_jobs()

    while True:
        await asyncio.sleep(1)
