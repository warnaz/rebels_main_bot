import os
import time 
import datetime

from typing import List
from loguru import logger
from aiogram import Bot 
from dotenv import load_dotenv

from database.models import Action, ActionList, ActionWallet, CRUD, Client, Tasks, Wallet, Project, Route
from action_list import zk_actions, scroll_actions

from zksync.main import zk_main
from scroll.main import scroll_main


load_dotenv()


def job_listener(event):
    if event.exception:
        logger.error(f"Job failed: {event.exception}. DateTime: {datetime.datetime.now()}")
    else:
        logger.info(f"Job succeeded: {type(event.retval)}. DateTime: {datetime.datetime.now()}")


async def run_actions(
          crud: CRUD, 
          data: dict, 
          client: Client, 
          wallet: Wallet, 
          project: Project, 
          route: Route, 
          action: Action,
          action_wallet: ActionWallet,
          task: Tasks,
          user_id: int
):
    '''Функция, которая запускает действия в маршруте'''

    if project.project_name == "ZKSYNC":
        actions = zk_actions
        main = zk_main
    elif project.project_name == "SCROLL":
        actions = scroll_actions
        main = scroll_main

    # Начинаем запускать каждое действие(item) в маршруте(action_list)
    action_list_obj: ActionList = await crud.get(id=action.action_list_id, obj=ActionList)

    logger.warning(f"ACTION_LIST: {action_list_obj.id, action_list_obj.action_name}")

    try:
        act_code = int(action_list_obj.code)
        module = actions[act_code]
        function_name = module.__name__

        result = await main(
            module=module,
            wallet=wallet,
            data=data
        )

        if result:
            logger.success(f"Успешно выполнена задача. Task id: {task.id}")

            await send_message_to_telegram(
                message=f"Успешно проведена транзакция. {function_name.upper()} - {action.pair}\n{result}",
                user_id=user_id
            )
            await crud.update_status_action_wallet(action_wallet.id, result)
            await crud.update_status_task(task.id, "COMPLETED")
        else:
            raise Exception("Something went wrong")
    except Exception as e:
        await crud.update_status_action_wallet(action_wallet.id, "FAILED")
        await crud.update_status_task(task.id, "FAILED")
        await crud.create_status(
            code=400,
            desc=str(e),
            client=client,
            wallet=wallet,
            project=project,
            route=route,
            action=action
        )
        logger.error(e)
        raise e


async def send_message_to_telegram(message: str, user_id: int):
    tg_token = os.getenv("TG_TOKEN")

    bot = Bot(token=tg_token)
    await bot.send_message(chat_id=user_id, text=message)
