from zksync.modules_settings import *
from zksync.modules_settings import swap_syncswap as swap_syncswap_zk
from zksync.modules_settings import send_mail as send_mail_zk
from zksync.modules_settings import mint_nft as mint_nft_zk

from scroll.modules_settings import *
from scroll.modules_settings import swap_syncswap as swap_syncswap_scroll
from scroll.modules_settings import mint_zkstars as mint_zkstars_scroll
from scroll.modules_settings import send_mail as send_mail_scroll
from scroll.modules_settings import bridge_orbiter as bridge_orbiter_scroll


zk_actions = {
    1: swap_syncswap_zk,
    2: swap_mute,
    3: swap_spacefi,
    4: swap_pancake,
    5: swap_woofi,
    6: swap_odos,
    7: swap_zkswap,
    8: swap_xyswap,
    9: swap_openocean,
    10: swap_inch,
    11: swap_maverick,
    12: swap_vesync,
    13: mint_tavaera,
    14: mint_mailzero_nft,
    15: mint_nft_zk,
    16: mint_zks_domain,
    17: mint_era_domain,
    18: send_message,
    19: send_mail_zk
}

scroll_actions = {
    20: swap_skydrome,
    21: swap_zebra,
    22: swap_syncswap_scroll,
    23: mint_zkstars_scroll,
    24: mint_zerius,
    25: send_mail_scroll,
    26: bridge_orbiter_scroll,
    27: bridge_layerswap,
}
