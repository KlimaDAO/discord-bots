from datetime import datetime, timedelta
import os
import json
import math

import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
import discord
from discord.ext import commands, tasks

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
SCAN_API_KEY = os.environ['POLYGONSCAN_API_KEY']

# Initialized Discord client
intents = discord.Intents.default()
intents.presences = True
intents.members = False
client = commands.Bot(intents=intents, help_command=None, command_prefix='&?')

# Initialize web3
project_id = os.environ['WEB3_INFURA_PROJECT_ID']
polygon_mainnet_endpoint = f'https://polygon-mainnet.infura.io/v3/{project_id}'
web3 = Web3(Web3.HTTPProvider(polygon_mainnet_endpoint))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)
assert (web3.isConnected())

DISTRIBUTOR_ADDRESS = Web3.toChecksumAddress("0x4cC7584C3f8FAABf734374ef129dF17c3517e9cB")  # noqa: E501
SKLIMA_ADDRESS = Web3.toChecksumAddress("0xb0C22d8D350C67420f06F48936654f567C73E8C8")  # noqa: E501

# Load ABIs
script_dir = os.path.dirname(__file__)
abi_dir = os.path.join(script_dir, 'abis')

with open(os.path.join(abi_dir, 'distributor.json'), 'r') as f:
    DISTRIBUTOR_ABI = json.load(f)


with open(os.path.join(abi_dir, 'sklima.json'), 'r') as f:
    SKLIMA_ABI = json.load(f)


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
        return None


def get_circ_supply():
    sklima_contract = web3.eth.contract(
        address=SKLIMA_ADDRESS,
        abi=SKLIMA_ABI
    )

    try:
        return sklima_contract.functions.circulatingSupply().call()
    except ValueError:
        return None


def get_block_30_days_ago():
    '''Fetch the block number that was closest to 30 days ago from PolygonScan'''
    days_ago = datetime.today() - timedelta(days=30)
    timestamp = int(days_ago.timestamp())

    resp = requests.get(
        f'https://api.polygonscan.com/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={SCAN_API_KEY}'  # noqa: E501
    )

    print(resp.content)

    try:
        block_num = int(
            json.loads(resp.content)['result']
        )
    except (TypeError, json.decoder.JSONDecodeError):
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

    print(f'5 Day Yield: {five_day_roi*100:,.2f}%')

    for guild in client.guilds:
        guser = guild.get_member(client.user.id)
        try:
            await guser.edit(nick=f'{five_day_roi*100:,.2f}% 5 Day Yield')
        except discord.errors.HTTPException:
            return

    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f'{staking_apy*100:,.2f}% APY'
        )
    )


client.run(BOT_TOKEN)
