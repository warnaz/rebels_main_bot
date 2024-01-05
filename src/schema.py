from pydantic import BaseModel


class TestData(BaseModel):
    init_data: dict


class ProjectScheme(BaseModel):
    project_name: str


class RequestData(BaseModel):
    max_amount: float
    client_id: int
    amount_bridge: float
    route_id: int 
    wallet_id: int 
    min_time: int 
    max_time: int 
    max_gas: int 
    init_data: str | int


class ClientScheme(BaseModel):
    name: str


class WalletSceme(BaseModel):
    key: str
    client: int


class ListWalletScheme(BaseModel):
    client_id: int


class RouteScheme(BaseModel):
    route_name: str
    project_id: int 


class ActionScheme(BaseModel):
    route_id: int 
    action_list_id: int 
    pair: str


class AddAccountScheme(BaseModel):
    evm_key: str 
    starknet_key: str 
    proxy: str 
    wallet_name: str
    client_id: int 
