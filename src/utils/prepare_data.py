from typing import List
from database.models import CRUD, Route, Project, ActionList, Client, Wallet


async def get_client_wallet(crud: CRUD, client_id, wallet_id) -> tuple:
    client = await crud.get(client_id, Client)
    wallet = await crud.get(wallet_id, Wallet)

    return client, wallet


async def get_data(crud: CRUD, data: dict) -> tuple:
    max_amount  = data.get('max_amount')
    gas         = data.get('max_gas')
    route_id    = data.get('route_id')
    client_id   = data.get("client_id")
    wallet_id   = data.get("wallet_id")
    min_time    = data.get("min_time")
    max_time    = data.get("max_time")
    init_data   = data.get("init_data")

    if min_time > max_time:
        min_time, max_time = max_time, min_time

    client, wallet = await get_client_wallet(crud, client_id, wallet_id)

    route: Route = await crud.get(route_id, obj=Route)
    project: Project = await crud.get(route.project_id, obj=Project)
    action_list: List[ActionList] = await crud.get_actions(route.id)

    return route, project, action_list, client, wallet, min_time, max_time, max_amount, gas, init_data
