import os

from discord.ext import tasks

from ..constants import C3_ADDRESS, FRAX_DECIMALS, \
                        C3_DECIMALS, FRAX_C3_POOL
from ..contract_info import token_supply, uni_v2_pool_price
from ..utils import get_discord_client, get_eth_web3, \
                    get_polygon_web3, load_abi, \
                    update_nickname, update_presence, \
                    prettify_number

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()
web3_eth = get_eth_web3()

# Load ABI
c3_abi = load_abi('erc20_token.json')


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    price = uni_v2_pool_price(web3, FRAX_C3_POOL, FRAX_DECIMALS - C3_DECIMALS)
    supply = token_supply(web3, C3_ADDRESS, c3_abi, C3_DECIMALS)

    if price is not None and supply is not None:
        price_text = f'${price:,.6f} C3'

        print(price_text)

        success = await update_nickname(client, price_text)
        if not success:
            return
        supply_text = f'Supply: {prettify_number(supply)}'
        success = await update_presence(client, supply_text)
        if not success:
            return


client.run(BOT_TOKEN)
