import os

from discord.ext import tasks

from ..contract_info import uni_v2_pool_price, token_supply
from ..constants import BCT_USDC_POOL, KLIMA_ADDRESS, \
                        KLIMA_BCT_POOL, KLIMA_DECIMALS, USDC_DECIMALS
from ..utils import get_discord_client, \
                    get_polygon_web3, load_abi, update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()

klima_abi = load_abi('erc20_token.json')


def get_info():
    bct_price = uni_v2_pool_price(web3, BCT_USDC_POOL, USDC_DECIMALS)
    klima_price = uni_v2_pool_price(
        web3, KLIMA_BCT_POOL,
        # Multiple by -1 because KLIMA is the denominator
        -1 * KLIMA_DECIMALS, basePrice=bct_price
    )
    supply = token_supply(web3, KLIMA_ADDRESS, klima_abi, KLIMA_DECIMALS)

    return(klima_price, supply)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    price, supply = get_info()

    if price is not None and supply is not None:
        mcap = f'${price*supply/1e6:,.1f}M'
        print(f'{mcap} MCap')

        success = await update_nickname(client, f'MCap: {mcap}')
        if not success:
            return

        success = await update_presence(client, f'KLIMA Price: ${price:,.2f}')
        if not success:
            return


client.run(BOT_TOKEN)
