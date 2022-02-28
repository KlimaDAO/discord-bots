from datetime import datetime, timedelta
import os
import json
import math
import traceback

import requests
from web3.middleware import geth_poa_middleware
from discord.ext import tasks

from ..constants import DISTRIBUTOR_ADDRESS, SKLIMA_ADDRESS
from ..utils import get_discord_client, get_polygon_web3, load_abi, update_nickname, update_presence

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
SCAN_API_KEY = os.environ['POLYGONSCAN_API_KEY']

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load ABIs
DISTRIBUTOR_ABI = load_abi('distributor.json')
SKLIMA_ABI = load_abi('sklima.json')


def get_staking_params():
    distributor_contract = web3.eth.contract(
        address=DISTRIBUTOR_ADDRESS,
        abi=DISTRIBUTOR_ABI
    )

    try:
        epoch_length = distributor_contract.functions.epochLength().call()

        info = distributor_contract.functions.info(0).call()
        reward_rate = info[0]
        staking_reward = distributor_contract.functions.nextRewardAt(reward_rate).call()

        return staking_reward, epoch_length
    except ValueError:
        traceback.print_exc()
        return None


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


def get_block_30_days_ago():
    '''Fetch the block number that was closest to 30 days ago from PolygonScan'''
    days_ago = datetime.today() - timedelta(days=30)
    timestamp = int(days_ago.timestamp())

    resp = requests.get(
        f'https://api.polygonscan.com/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={SCAN_API_KEY}'  # noqa: E501
    )

    try:
        block_num = int(
            json.loads(resp.content)['result']
        )
    except (TypeError, json.decoder.JSONDecodeError, ValueError):
        traceback.print_exc()
        block_num = None

    return block_num


def get_rebases_per_day(blocks_per_rebase):
    '''
    Calculates the average number of rebases per day based on the average
    block production time for the previous 1 million blocks
    '''
    block_30_days_ago = get_block_30_days_ago()

    if block_30_days_ago is None:
        return None

    try:
        latest_block = web3.eth.get_block('latest')
        latest_block_num = latest_block['number']
        latest_block_time = latest_block['timestamp']

        prev_block_time = web3.eth.get_block(block_30_days_ago)['timestamp']
    except ValueError:
        traceback.print_exc()
        return None

    block_diff = latest_block_num - block_30_days_ago
    avg_block_secs = (latest_block_time - prev_block_time) / block_diff

    secs_per_rebase = blocks_per_rebase * avg_block_secs

    return 24 / (secs_per_rebase / 60 / 60)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    staking_reward, epoch_length = get_staking_params()
    circulating_supply = get_circ_supply()

    if epoch_length is not None:
        rebases_per_day = get_rebases_per_day(epoch_length)
    else:
        return

    if staking_reward is not None and circulating_supply is not None and rebases_per_day is not None:
        # ie, ROI % in this rebase
        staking_rebase = staking_reward / circulating_supply
        # ie, ROI % in the next 5 days
        five_day_roi = math.pow(1 + staking_rebase, 5 * rebases_per_day) - 1
        # ie, yearly APY
        staking_apy = math.pow(1 + staking_rebase, 365 * rebases_per_day)
    else:
        return

    yield_text = f'{five_day_roi*100:,.2f}% 5 Day Yield'
    print(yield_text)

    success = await update_nickname(client, yield_text)
    if not success:
        return

    success = await update_presence(
        client, f'{staking_apy*100:,.2f}% APY', 'playing'
    )
    if not success:
        return


client.run(BOT_TOKEN)
