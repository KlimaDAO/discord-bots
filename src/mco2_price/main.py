import os

from discord.ext import tasks

from ..constants import MCO2_ADDRESS, MCO2_DECIMALS, KLIMA_DECIMALS, KLIMA_MCO2_POOL
from ..contract_info import token_supply, uni_v2_pool_price, klima_usdc_price
from ..utils import get_discord_client, get_eth_web3, \
                    get_polygon_web3, load_abi, \
                    update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()
web3_eth = get_eth_web3()

# Load ABI
mco2_abi = load_abi('carbon_pool.json')


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    klima_price = klima_usdc_price(web3)
    price = klima_price * uni_v2_pool_price(web3, KLIMA_MCO2_POOL, KLIMA_DECIMALS)
    supply = token_supply(web3_eth, MCO2_ADDRESS, mco2_abi, MCO2_DECIMALS)

    if price is not None and supply is not None:
        price_text = f'${price:,.2f} MCO2'

        print(price_text)

        success = await update_nickname(client, price_text)
        if not success:
            return

        success = await update_presence(client, f'Supply: {supply/1e6:,.2f}M')
        if not success:
            return


client.run(BOT_TOKEN)
