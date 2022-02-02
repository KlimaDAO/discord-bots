import os
from discord.ext import tasks

from ..constants import BCT_ADDRESS, BCT_USDC_POOL, USDC_DECIMALS, BCT_DECIMALS
from ..contract_info import uni_v2_pool_price, token_supply
from ..utils import get_polygon_web3, \
                    get_discord_client, load_abi, update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()

# Load ABIs
bct_abi = load_abi('carbon_pool.json')


def get_bct_supply():
    bct = web3.eth.contract(
        address=BCT_ADDRESS,
        abi=bct_abi
    )

    try:
        decimals = bct.functions.decimals().call()
        total_supply = bct.functions.totalSupply().call() / 10**decimals
        return total_supply
    except Exception:
        return None


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    price = uni_v2_pool_price(
        web3, BCT_USDC_POOL,
        USDC_DECIMALS
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
