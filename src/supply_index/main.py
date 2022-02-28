import os

from discord.ext import tasks

from ..contract_info import token_supply
from ..constants import KLIMA_ADDRESS, KLIMA_DECIMALS, STAKING_ADDRESS
from ..utils import get_discord_client, \
                    get_polygon_web3, load_abi, update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()

klima_abi = load_abi('erc20_token.json')
staking_abi = load_abi('klima_staking.json')


def get_index():
    contract_instance = web3.eth.contract(address=STAKING_ADDRESS, abi=staking_abi)
    try:
        index = contract_instance.functions.index().call() / 10**KLIMA_DECIMALS
    except ValueError:
        index = None

    return index


def get_info():
    supply = token_supply(web3, KLIMA_ADDRESS, klima_abi, KLIMA_DECIMALS)
    index = get_index()

    return(index, supply)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    index, supply = get_info()

    if index is not None and supply is not None:
        supply = f'{supply/1e6:,.1f}M'
        print(f'{supply} KLIMA Supply')

        success = await update_nickname(client, f'Supply: {supply}')
        if not success:
            return

        success = await update_presence(client, f'Current Index: {index:,.2f}')
        if not success:
            return


client.run(BOT_TOKEN)
