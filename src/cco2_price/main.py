import os
from discord.ext import tasks

from ..constants import CCO2_ADDRESS, KLIMA_CCO2_POOL, KLIMA_DECIMALS
from ..contract_info import uni_v2_pool_price, token_supply, klima_usdc_price
from ..utils import get_polygon_web3, \
    get_discord_client, load_abi, prettify_number, \
    update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()

# Load ABIs
cco2_abi = load_abi('carbon_pool.json')


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    klima_price = klima_usdc_price(web3)
    token_price = uni_v2_pool_price(
        web3, KLIMA_CCO2_POOL,
        KLIMA_DECIMALS
    )
    supply = token_supply(web3, CCO2_ADDRESS, cco2_abi)

    if klima_price is not None and token_price is not None and supply is not None:
        price = klima_price * token_price
        price_text = f'${price:,.3f} CCO2'

        print(price_text)

        success = await update_nickname(client, price_text)
        if not success:
            return

        supply_text = f'Supply: {prettify_number(supply)}'
        success = await update_presence(
            client,
            supply_text
        )
        if not success:
            return

client.run(BOT_TOKEN)
