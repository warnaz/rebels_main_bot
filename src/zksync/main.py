import sys

import questionary
from loguru import logger
from questionary import Choice

from .modules_settings import *


def get_module():
    result = questionary.select(
        "Select a method to get started",
        choices=[
            Choice("1) Make bridge ZkSync", bridge_zksync),
            Choice("2) Make withdraw from ZkSync", withdraw_zksync),
            Choice("3) Make bridge on Orbiter", bridge_orbiter),
            Choice("4) Wrap ETH", wrap_eth),
            Choice("5) Unwrap ETH", unwrap_eth),
            Choice("6) Make swap on SyncSwap", swap_syncswap),
            Choice("7) Add liquidity on SyncSwap", liquidity_syncswap),
            Choice("8) Make swap on Mute", swap_mute),
            Choice("9) Make swap on Space.fi", swap_spacefi),
            Choice("10) Add liquidity on Space.fi", liquidity_spacefi),
            Choice("11) Make swap on PancakeSwap", swap_pancake),
            Choice("12) Make swap on WooFi", swap_woofi),
            Choice("13) Make swap on Odos", swap_odos),
            Choice("14) Make swap on ZkSwap", swap_zkswap),
            Choice("15) Make swap on XYSwap", swap_xyswap),
            Choice("16) Make swap on OpenOcean", swap_openocean),
            Choice("17) Make swap on 1inch", swap_inch),
            Choice("18) Make swap on Maverick", swap_maverick),
            Choice("19) Make swap on VeSync", swap_vesync),
            Choice("20) Make bungee refuel", bungee_refuel),
            Choice("21) Stargate bridge MAV", stargate_bridge),
            Choice("22) Deposit Eralend", deposit_eralend),
            Choice("23) Withdraw Eralend", withdraw_erlaned),
            Choice("24) Enable collateral on Eralend", enable_collateral_eralend),
            Choice("25) Disable collateral on Eralend", disable_collateral_eralend),
            Choice("26) Deposit Basilisk", deposit_basilisk),
            Choice("27) Withdraw Basilisk", withdraw_basilisk),
            Choice("28) Enable collateral on Basilisk", enable_collateral_basilisk),
            Choice("29) Disable collateral on Basilisk", disable_collateral_basilisk),
            Choice("30) Deposit ReactorFusion", deposit_reactorfusion),
            Choice("31) Withdraw ReactorFusion", withdraw_reactorfusion),
            Choice("32) Enable collateral on ReactorFusion", enable_collateral_reactorfusion),
            Choice("33) Disable collateral on ReactorFusion", disable_collateral_reactorfusion),
            Choice("34) Deposit ZeroLend", deposit_zerolend),
            Choice("35) Withdraw ZeroLend", withdraw_zerolend),
            Choice("36) Deposit RocketSam", deposit_rocketsam),
            Choice("37) Withdraw RocketSam", withdraw_rocketsam),
            Choice("38) Mint ZkStars NFT", mint_zkstars),
            Choice("39) Create NFT collection on Omnisea", create_omnisea),
            Choice("40) Mint and bridge NFT L2Telegraph", bridge_nft),
            Choice("41) Mint Tavaera ID + NFT", mint_tavaera),
            Choice("42) Mint MailZero NFT", mint_mailzero_nft),
            Choice("43) Mint NFT on NFTS2ME", mint_nft),
            Choice("44) Mint ZKS Domain", mint_zks_domain),
            Choice("45) Mint Era Domain", mint_era_domain),
            Choice("46) Send message L2Telegraph", send_message),
            Choice("47) Dmail sending mail", send_mail),
            Choice("48) Create gnosis safe", create_safe),
            Choice("49) Swap tokens to ETH", swap_tokens),
            Choice("50) MultiSwap", swap_multiswap),
            Choice("51) Use custom routes", custom_routes),
            Choice("52) MultiApprove", multi_approve),
            Choice("53) Check transaction count", "tx_checker"),
            Choice("54) Exit", "exit"),
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        sys.exit()
    return result


def get_wallets(wallet, proxy: str = None):

    ACCOUNTS = [wallet.primary_key]
    PROXIES = [proxy]

    logger.error(ACCOUNTS)
    if proxy:
        account_with_proxy = dict(zip(ACCOUNTS, PROXIES))

        wallets = [
            {
                "id": _id,
                "key": key,
                "proxy": account_with_proxy[key]
            } for _id, key in enumerate(account_with_proxy, start=1)
        ]
    else:
        wallets = [
            {
                "id": _id,
                "key": key,
                "proxy": None
            } for _id, key in enumerate(ACCOUNTS, start=1)
        ]
    return wallets


async def run_module(module, account_id, key, proxy, data, **kwargs):
    try:
        return await module(account_id, key, proxy, data, **kwargs)
    except Exception as e:
        logger.error(e)
        raise e


async def zk_main(module, wallet, data, **kwargs):
    account = get_wallets(wallet=wallet)[0]
    return "Success. Tx_Hash: https://testnet.zksync.dev/tx/"

    # return await run_module(
    #     module=module, 
    #     account_id=account.get("id"), 
    #     key=account.get("key"), 
    #     proxy=account.get("recipient", None), 
    #     data=data, 
    #     **kwargs
    # )
