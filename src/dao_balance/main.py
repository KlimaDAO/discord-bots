import os
from discord.ext import tasks

from ..constants import KLIMA_ADDRESS, DAO_WALLET_ADDRESS, \
    KLIMA_DECIMALS
from ..contract_info import balance_of
from ..utils import get_discord_client, \
    get_polygon_web3, load_abi, prettify_number, \
    update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialize web3
web3 = get_polygon_web3()

# Load ABI
erc_20_abi = load_abi('erc20_token.json')

# Initialized Discord client
client = get_discord_client()


def get_info():
    dao_balance = get_dao_balance()
    return dao_balance


def get_dao_balance():
    dao_balance = balance_of(
        web3, KLIMA_ADDRESS, erc_20_abi, KLIMA_DECIMALS, DAO_WALLET_ADDRESS)
    return dao_balance


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    dao_balance = get_info()

    if dao_balance is not None:

        balance_text = f'DAO: {prettify_number(dao_balance)} KLIMA'
        success = await update_nickname(client, balance_text)
        if not success:
            return

        presence_text = "DAO wallet balance"
        success = await update_presence(
            client,
            presence_text,
            type='playing'
        )
        if not success:
            return

client.run(BOT_TOKEN)
