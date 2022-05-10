import os

from discord.ext import tasks

from subgrounds.subgrounds import Subgrounds

from ..contract_info import token_supply
from ..constants import KLIMA_ADDRESS, KLIMA_DECIMALS
from ..utils import get_discord_client, \
    get_polygon_web3, load_abi, \
    update_nickname, update_presence, \
    get_last_metric

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()

klima_abi = load_abi('erc20_token.json')
staking_abi = load_abi('klima_staking.json')

sg = Subgrounds()


def get_cc():
    last_metric = get_last_metric(sg)

    return sg.query([last_metric.treasuryCarbonCustodied])


def get_info():
    supply = token_supply(web3, KLIMA_ADDRESS, klima_abi, KLIMA_DECIMALS)
    cc = get_cc()

    return(cc, supply)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    cc, supply = get_info()

    if cc is not None and supply is not None:
        supply_fmt = f'{supply/1e6:,.1f}M'
        print(f'{supply_fmt} KLIMA Supply')

        success = await update_nickname(client, f'Supply: {supply_fmt}')
        if not success:
            return

        success = await update_presence(client, f'CC per KLIMA: {cc/supply:,.2f}')
        if not success:
            return


client.run(BOT_TOKEN)
