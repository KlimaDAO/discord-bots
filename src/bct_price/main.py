import os
from discord.ext import tasks

from ..constants import BCT_ADDRESS, BCT_KLIMA_POOL, KLIMA_DECIMALS, BCT_DECIMALS
from ..contract_info import uni_v2_pool_price, token_supply, klima_usdc_price
from ..utils import get_polygon_web3, \
                    get_discord_client, load_abi, update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()

# Load ABIs
bct_abi = load_abi('carbon_pool.json')


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    klima_price = klima_usdc_price(web3)
    price = klima_price / uni_v2_pool_price(
        web3, BCT_KLIMA_POOL,
        KLIMA_DECIMALS - BCT_DECIMALS
    )
    supply = token_supply(web3, BCT_ADDRESS, bct_abi, BCT_DECIMALS)

    if price is not None and supply is not None:
        price_text = f'${price:,.2f} BCT'

        print(price_text)

        success = await update_nickname(client, price_text)
        if not success:
            return

        success = await update_presence(
            client,
            f'Supply: {supply/1e6:,.1f}M'
        )
        if not success:
            return

client.run(BOT_TOKEN)
