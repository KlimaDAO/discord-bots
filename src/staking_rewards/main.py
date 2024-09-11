import os
import math
import traceback

from web3.middleware import ExtraDataToPOAMiddleware
from discord.ext import tasks

from ..constants import SKLIMA_ADDRESS
from ..utils import get_discord_client, get_polygon_web3, load_abi, \
                    update_nickname, update_presence, get_rebases_per_day, \
                    get_staking_params

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
SCAN_API_KEY = os.environ['POLYGONSCAN_API_KEY']

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()
web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# Load ABIs
SKLIMA_ABI = load_abi('sklima.json')


def get_circ_supply():
    sklima_contract = web3.eth.contract(
        address=SKLIMA_ADDRESS,
        abi=SKLIMA_ABI
    )

    try:
        return sklima_contract.functions.circulatingSupply().call()
    except ValueError:
        traceback.print_exc()
        return None


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    staking_reward, epoch_length = get_staking_params(web3)
    circulating_supply = get_circ_supply()

    if epoch_length is not None:
        rebases_per_day = get_rebases_per_day(epoch_length)
    else:
        return

    if staking_reward is not None and circulating_supply is not None and rebases_per_day is not None:
        # ie, reward % in this rebase
        staking_rebase = staking_reward / circulating_supply
        # ie, reward % in the next 5 days
        five_day_rewards = math.pow(1 + staking_rebase, 5 * rebases_per_day) - 1
        # ie, annualized reward %
        staking_akr = math.pow(1 + staking_rebase, 365 * rebases_per_day) - 1
    else:
        return

    yield_text = f'{five_day_rewards*100:,.3f}% 5 Day Rewards'
    print(yield_text)

    success = await update_nickname(client, yield_text)
    if not success:
        return

    success = await update_presence(
        client, f'{staking_akr*100:,.2f}% AKR', 'playing'
    )
    if not success:
        return


client.run(BOT_TOKEN)
