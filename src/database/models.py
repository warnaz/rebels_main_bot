import datetime
import random
import string
import asyncio 

from typing import List, Tuple
from loguru import logger
from sqlalchemy import ForeignKey, TIMESTAMP, select, update, delete
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .config_models import engine

# alembic stamp head
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 run:app


Base = declarative_base()


class Project(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_name: Mapped[str]

    route: Mapped['Route'] = relationship(back_populates="project")


class Route(Base):
    __tablename__ = "route"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_name: Mapped[str]
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))

    project: Mapped["Project"] = relationship(back_populates="route")
    action: Mapped[List["Action"]] = relationship(back_populates="route", uselist=True)


class Action(Base):
    __tablename__ = 'action'

    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("route.id"))
    action_list_id: Mapped[int] = mapped_column(ForeignKey("action_list.id"))
    pair: Mapped[str] = mapped_column(nullable=True)

    action_list: Mapped['ActionList'] = relationship(back_populates="action")
    route: Mapped['Route'] = relationship(back_populates="action")
    action_wallet: Mapped['ActionWallet'] = relationship(back_populates="action")


class ActionList(Base):
    __tablename__ = 'action_list'

    id: Mapped[int] = mapped_column(primary_key=True)
    action_name: Mapped[str]
    code: Mapped[int]

    action: Mapped[List["Action"]] = relationship(back_populates="action_list")


class ActionWallet(Base):
    __tablename__ = 'action_wallet'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str]
    amount: Mapped[float]
    gas: Mapped[int]
    # pair: Mapped[str] = mapped_column(nullable=True)

    action_id: Mapped[int] = mapped_column(ForeignKey('action.id'))
    wallet_id: Mapped[int] = mapped_column(ForeignKey('wallet.id'))

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now)
    estimated_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True)
    completed_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True)

    wallet: Mapped['Wallet'] = relationship(back_populates="action_wallet")
    action: Mapped['Action'] = relationship(back_populates="action_wallet")


class Wallet(Base):
    __tablename__ = 'wallet'

    id: Mapped[int] = mapped_column(primary_key=True)
    
    primary_key: Mapped[str]
    evm_key: Mapped[str]

    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    wallet_name: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now)

    client: Mapped['Client'] = relationship(back_populates="wallet")
    action_wallet: Mapped['ActionWallet'] = relationship(back_populates="wallet")


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_name: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now)
    token: Mapped[str] = mapped_column(nullable=True)

    wallet: Mapped["Wallet"] = relationship(back_populates="client")


class Status(Base):
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now)
    desc: Mapped[str]
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"), nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("route.id"), nullable=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("action.id"), nullable=True)
    # action_wallet_id: Mapped[int] = mapped_column(ForeignKey("action_wallet.id"), nullable=True)

    client: Mapped['Client'] = relationship(backref="status")
    wallet: Mapped['Wallet'] = relationship(backref="status")
    project: Mapped['Project'] = relationship(backref="status")
    route: Mapped['Route'] = relationship(backref="status")
    action: Mapped['Action'] = relationship(backref="status")
    # action_wallet: Mapped['ActionWallet'] = relationship(backref="status")


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now)
    status: Mapped[str]

    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"), nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("route.id"), nullable=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("action.id"), nullable=True)
    action_wallet_id: Mapped[int] = mapped_column(ForeignKey("action_wallet.id"), nullable=True)

    client: Mapped['Client'] = relationship(backref="task")
    wallet: Mapped['Wallet'] = relationship(backref="task")
    project: Mapped['Project'] = relationship(backref="task")
    route: Mapped['Route'] = relationship(backref="task")
    action: Mapped['Action'] = relationship(backref="task")
    action_wallet: Mapped['ActionWallet'] = relationship(backref="task")


class CRUD():
    def __init__(self, session = None) -> None:
        if not session:
            self.session = async_sessionmaker(engine, expire_on_commit=False)
        else:
            self.session = session

    async def create_table(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_table(self):
        x = input('Вы уверены, что хотите удалить все таблицы бд? (y/n): ')

        if x == 'y':
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)

    async def insert_data(self, obj, **kwargs):
        async with self.session() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)

            return obj
    
    async def flust_data(self, obj):
        async with self.session() as session:
            session.add(obj)
            await session.flush()
    
    async def commit_data(self):
        async with self.session() as session:
           await  session.commit()

    async def insert_data_many(self, *obj, **kwargs) -> tuple:
        async with self.session() as session:
            session.add_all(obj)
            await session.commit()

            return obj
        
    async def create_tasks(
            self,
            status: str,
            client: Client = None,
            wallet: Wallet = None,
            project: Project = None,
            route: Route = None,
            action: Action = None,
            action_wallet: ActionWallet = None
        ) -> Tasks:

        new_task = Tasks(
            status=status,
            client_id=client,
            wallet_id=wallet,
            project_id=project,
            route_id=route,
            action_id=action,
            action_wallet_id=action_wallet
        )
        result = await self.insert_data(obj=new_task)

        return result

    async def create_project(self, project_name: str) -> Project:
        project = Project(project_name=project_name)
        result = await self.insert_data(obj=project)
        
        return result

    async def create_route(self, route_name: str, project_id: int) -> Route:
        route = Route(route_name=route_name, project_id=project_id)
        result = await self.insert_data(obj=route)
        
        return result

    async def create_client(self, name: str) -> Client:
        client = Client(client_name=name)
        result = await self.insert_data(obj=client)
        
        return result 

    def generate_token(length):
        """Generate a random token of specified length"""
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for _ in range(length))
        return token

    async def create_wallet(self, private_key: str, evm_key: str, wallet_name: str, client: Client | int) -> Wallet:
        if isinstance(client, Client):
            wallet = Wallet(primary_key=private_key, evm_key=evm_key, client=client, wallet_name=wallet_name)
        else:
            wallet = Wallet(primary_key=private_key, evm_key=evm_key, client_id=client, wallet_name=wallet_name)
        
        result = await self.insert_data(obj=wallet)

        return result

    async def create_action(self, route_id: int, action_list_id: int, pair: str) -> Action:
        action = Action(route_id=route_id, action_list_id=action_list_id, pair=pair)
        result = await self.insert_data(obj=action)

        return result

    async def create_action_wallet(
            self, 
            status: str,
            amount: int,
            gas: int,
            wallet_id: int, 
            action_id: int, 
            estimated_time: datetime.datetime = None
        ) -> ActionWallet:

        action_wallet = ActionWallet(
            status=status, 
            amount=amount,
            gas=gas,
            action_id=action_id, 
            wallet_id=wallet_id, 
            estimated_time=estimated_time
        )
        result = await self.insert_data(obj=action_wallet)

        return action_wallet
    

    async def create_client_wallet(self, client_name, private_key) -> Tuple[Client, Wallet]:
        client = await self.create_client(client_name)
        wallet = await self.create_wallet(private_key, client)

        return client, wallet

    async def create_status(
            self,
            code: int, 
            desc: str,
            client: Client = None,
            wallet: Wallet = None,
            project: Project = None,
            route: Route = None,
            action: Action = None,
            data: datetime = None    
        ) -> Status:

        status = Status(
            code=code, 
            desc=desc, 
            created_at=data,
            client=client,
            wallet=wallet,
            project=project,
            route=route,
            action=action
        )
        result = await self.insert_data(obj=status)

        return result

    async def get_actions(self, route_id) -> List[ActionList]:
        async with self.session() as session:
            actions_list = []
            raw_sql = select(Route).options(selectinload(Route.action)).where(Route.id == route_id)
            route = await session.scalars(raw_sql)
            route = route.first()
            logger.error(route.action)

            for item in route.action:
                raw_action = select(ActionList).where(ActionList.id == item.action_list_id)
                action = await session.scalars(raw_action)
                action = action.first()
                actions_list.append(action)

            return actions_list
    
    async def get_single_action(self, route_id, act_list_id) -> Action:
        async with self.session() as session:
            raw_sql = select(Action).where(Action.route_id == route_id, Action.action_list_id == act_list_id)
            action = await session.scalars(raw_sql)
            action = action.first()

            return action

    async def get(self, id, obj):
        async with self.session() as session:
            raw_sql = select(obj).where(obj.id == id)
            obj = await session.scalars(raw_sql)
            obj = obj.first()

            return obj

    async def get_client_wallet(self, client_id) -> List[dict[Wallet]]:
        async with self.session() as session:
            raw_sql = select(Wallet.id, Wallet.wallet_name).where(Wallet.client_id == client_id)
            result = await session.execute(raw_sql)
            result = result.all()
            wallet = [{"id": row[0], "wallet_name": row[1]} for row in result]

            return wallet

    async def get_project(self, project_name) -> Project: 
        async with self.session() as session:
            raw_sql = select(Project).where(Project.project_name == project_name)
            project = await session.scalars(raw_sql)
            project = project.first()

            return project
        
    async def get_route_list(self, project_id) -> List[Route]: 
        async with self.session() as session:
            raw_sql = select(Route).where(Route.project_id == project_id)
            route_list = await session.scalars(raw_sql)
            route_list = route_list.all()

            return route_list

    async def get_route_actions(self, route_id) -> List[Action]:
        async with self.session() as session:
            raw_sql = select(Action).where(Action.route_id == route_id)
            action_list = await session.scalars(raw_sql)
            action_list = action_list.all()

            return action_list

    async def get_all_active_tasks(self) -> List[Tasks]:
        async with self.session() as session:
            raw_sql = select(Tasks).where(Tasks.status == "WAIT")
            tasks_list = await session.scalars(raw_sql)
            tasks_list = tasks_list.all()

            return tasks_list

    async def update_status_action_wallet(self, id, status):
        async with self.session() as session:
            stmt = (
                update(ActionWallet).
                where(ActionWallet.id == id).
                values(status=status, completed_at=datetime.datetime.now())
            )
            await session.execute(stmt)
            await session.commit()
    
    async def update_status_task(self, id, status):
        async with self.session() as session:
            stmt = (
                update(Tasks).
                where(Tasks.id == id).
                values(status=status)
            )
            await session.execute(stmt)
            await session.commit()

    async def update(self, id, obj, **kwargs):
        async with self.session() as session:
            stmt = (
                update(obj).
                where(obj.id == id).
                values(**kwargs)
            )
            await session.execute(stmt)
            await session.commit()

    async def delete(self, obj, **kwargs):
        res = input(f'Удалить данные из {obj}? (y/n): ')
        if res != 'y':
            return
        
        async with self.session() as session:
            stmt = (
                delete(obj).
                where(**kwargs)
            )
            await session.execute(stmt)
            await session.commit()

    async def create_test_data(self):
        client_one = Client(client_name="Magomed", token="892817995")
        client_two = Client(client_name="Marat", token="ch82348c299")
        client_three = Client(client_name="Rasul", token="dew9cj923j932c")

        wallet_one = Wallet(primary_key="wallet_one", client=client_one, evm_key="xxxxx", wallet_name="Wallet1")
        wallet_two = Wallet(primary_key="wallet_two", client=client_two, evm_key="xxxxx", wallet_name="Wallet2")
        wallet_three = Wallet(primary_key="wallet_three", client=client_three, evm_key="xxxxx", wallet_name="Wallet3")
        wallet_four = Wallet(primary_key="wallet_four", client=client_three, evm_key="xxxxx", wallet_name="Wallet4")
        wallet_five = Wallet(primary_key="wallet_five", client=client_two, evm_key="xxxxx", wallet_name="Wallet5")
        wallet_six = Wallet(primary_key="wallet_six", client=client_one, evm_key="xxxxx", wallet_name="Wallet6")

        project_two = Project(project_name="ZKSYNC")

        route_one = Route(route_name="route_one", project=project_two)
        route_two = Route(route_name="route_two", project=project_two)
        route_three = Route(route_name="route_three", project=project_two)

        action_list_one = ActionList(action_name="swap_syncswap", code=1)
        action_list_two = ActionList(action_name="swap_mute", code=2)
        action_list_three = ActionList(action_name="swap_spacefi", code=3)
        action_list_four = ActionList(action_name="swap_pancake", code=4)
        action_list_five = ActionList(action_name="swap_woofi", code=5)
        action_list_six = ActionList(action_name="swap_odos", code=6)
        action_list_seven = ActionList(action_name="swap_zkswap", code=7)
        action_list_eight = ActionList(action_name="swap_xyswap", code=8)
        action_list_nine = ActionList(action_name="swap_openocean", code=9)
        action_list_ten = ActionList(action_name="swap_inch", code=10)
        action_list_eleven = ActionList(action_name="swap_maverick", code=11)
        action_list_twelve = ActionList(action_name="swap_vesync", code=12)

        one = Action(route=route_one, action_list=action_list_one, pair="ETH/DAT")
        two = Action(route=route_one, action_list=action_list_one, pair="USDT/USDC")
        three = Action(route=route_one, action_list=action_list_one, pair="USDC/ETH")
        # Jediswap
        five = Action(route=route_one, action_list=action_list_two, pair="ETH/USDC")
        six = Action(route=route_one, action_list=action_list_two, pair="USDC/ETH")
        seven = Action(route=route_one, action_list=action_list_two, pair="ETH/USDC")
        eight = Action(route=route_one, action_list=action_list_two, pair="USDC/ETH")
        
        # Avnu
        nine = Action(route=route_one, action_list=action_list_three, pair="ETH/USDC")
        ten = Action(route=route_one, action_list=action_list_three, pair="USDT/USDC")
        eleven = Action(route=route_one, action_list=action_list_three, pair="USDC/DAI")

        # 10kswap
        twl = Action(route=route_one, action_list=action_list_four, pair="ETH/USDC")
        thrd = Action(route=route_one, action_list=action_list_four, pair="USDC/USDT")

        # Protoss
        prot_one = Action(route=route_one, action_list=action_list_five, pair="DAI/USDC")
        prot_two = Action(route=route_one, action_list=action_list_five, pair="USDC/ETH")

        # SithSwap
        sith_one = Action(route=route_one, action_list=action_list_six, pair="DAI/ETH")
        sith_two = Action(route=route_one, action_list=action_list_six, pair="ETH/ETH")

        # # Action for action_list_seven
        action_seven = Action(route=route_one, action_list=action_list_seven, pair="ETH/USDT")

        # # Action for action_list_eight
        action_eight = Action(route=route_one, action_list=action_list_eight, pair="ETH/DAI")

        
        ma = Action(route=route_two, action_list=action_list_one, pair="ETH/DAT")
        mb = Action(route=route_two, action_list=action_list_one, pair="USDT/USDC")
        mc = Action(route=route_two, action_list=action_list_one, pair="USDC/ETH")

        # Jediswap
        md = Action(route=route_two, action_list=action_list_two, pair="ETH/USDC")
        me = Action(route=route_two, action_list=action_list_two, pair="USDC/ETH")
        mf = Action(route=route_two, action_list=action_list_two, pair="ETH/USDC")
        mg = Action(route=route_two, action_list=action_list_two, pair="USDC/ETH")
        
        # Avnu
        mh = Action(route=route_two, action_list=action_list_three, pair="ETH/USDC")
        mi = Action(route=route_two, action_list=action_list_three, pair="USDT/USDC")
        mj = Action(route=route_two, action_list=action_list_three, pair="USDC/DAI")

        # 10kswap
        mk = Action(route=route_two, action_list=action_list_four, pair="ETH/USDC")
        ml = Action(route=route_two, action_list=action_list_four, pair="USDC/USDT")

        # Protoss
        mm = Action(route=route_two, action_list=action_list_five, pair="DAI/USDC")
        mn = Action(route=route_two, action_list=action_list_five, pair="USDC/ETH")

        # SithSwap
        mo = Action(route=route_two, action_list=action_list_six, pair="DAI/ETH")
        mp = Action(route=route_two, action_list=action_list_six, pair="ETH/ETH")

        # # Action for action_list_seven
        mq = Action(route=route_two, action_list=action_list_seven, pair="ETH/USDT")

        # # Action for action_list_eight
        mr = Action(route=route_two, action_list=action_list_eight, pair="ETH/DAI")

        aa = Action(route=route_two, action_list=action_list_one, pair="ETH/DAT")
        bb = Action(route=route_two, action_list=action_list_one, pair="USDT/USDC")
        cc = Action(route=route_two, action_list=action_list_one, pair="USDC/ETH")

        # Jediswap
        dd = Action(route=route_three, action_list=action_list_two, pair="ETH/USDC")
        ee = Action(route=route_three, action_list=action_list_two, pair="USDC/ETH")
        ff = Action(route=route_three, action_list=action_list_two, pair="ETH/USDC")
        gg = Action(route=route_three, action_list=action_list_two, pair="USDC/ETH")
        
        # Avnu
        hh = Action(route=route_three, action_list=action_list_three, pair="ETH/USDC")
        ii = Action(route=route_three, action_list=action_list_three, pair="USDT/USDC")
        jj = Action(route=route_three, action_list=action_list_three, pair="USDC/DAI")

        # 10kswap
        kk = Action(route=route_three, action_list=action_list_four, pair="ETH/USDC")
        ll = Action(route=route_three, action_list=action_list_four, pair="USDC/USDT")

        # Protoss
        mm = Action(route=route_three, action_list=action_list_five, pair="DAI/USDC")
        nn = Action(route=route_three, action_list=action_list_five, pair="USDC/ETH")

        # SithSwap
        oo = Action(route=route_three, action_list=action_list_six, pair="DAI/ETH")
        pp = Action(route=route_three, action_list=action_list_six, pair="ETH/ETH")

        # # Action for action_list_seven
        qq = Action(route=route_three, action_list=action_list_seven, pair="ETH/USDT")

        # # Action for action_list_eight
        rr = Action(route=route_three, action_list=action_list_eight, pair="ETH/DAI")


        await self.insert_data_many(
            client_one, client_two, client_three, 
            wallet_one, wallet_two, wallet_three, wallet_four, wallet_five, wallet_six, 
            project_two, route_one, route_two, route_three,
            action_list_one, action_list_two, action_list_three, action_list_four, action_list_five, action_list_six, action_list_seven, action_list_eight, action_list_nine, action_list_ten, action_list_eleven, action_list_twelve,
            one, two, three, five, six, seven, eight, nine, ten, eleven,
            aa, bb, cc, dd, ee, ff, gg, hh, ii, jj,
            kk, ll, mm, nn, oo, pp, qq, rr
        )


# crud = CRUD()
# asyncio.run(crud.drop_table())
# asyncio.run(crud.create_table())
# asyncio.run(crud.create_test_data())
# asyncio.run(crud.create_test_data())
