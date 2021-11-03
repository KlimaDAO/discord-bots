import os
import json
import math

from web3 import Web3
import discord
from discord.ext import commands, tasks

BOT_TOKEN = os.environ["DISCORD_STAKING_REWARD_BOT_TOKEN"]

# Initialized Discord client
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(intents=intents, help_command=None, command_prefix='&?')

# Initialize web3
project_id = os.environ['WEB3_INFURA_PROJECT_ID']
polygon_mainnet_endpoint = f'https://polygon-mainnet.infura.io/v3/{project_id}'
web3 = Web3(Web3.HTTPProvider(polygon_mainnet_endpoint))
assert (web3.isConnected())

DISTRIBUTOR_ADDRESS = Web3.toChecksumAddress("0x4cC7584C3f8FAABf734374ef129dF17c3517e9cB")  # noqa: E501
SKLIMA_ADDRESS = Web3.toChecksumAddress("0xb0C22d8D350C67420f06F48936654f567C73E8C8")  # noqa: E501

f = open('abis/distributor.json')
DISTRIBUTOR_ABI = json.load(f)
f.close()

f = open('abis/sklima.json')
SKLIMA_ABI = json.load(f)
f.close()


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=60)
async def update_info():
    distributor_contract = web3.eth.contract(
        address=DISTRIBUTOR_ADDRESS,
        abi=DISTRIBUTOR_ABI
    )
    sklima_contract = web3.eth.contract(
        address=SKLIMA_ADDRESS,
        abi=SKLIMA_ABI
    )

    staking_reward = distributor_contract.functions.nextRewardAt(5000).call()
    circulating_supply = sklima_contract.functions.circulatingSupply().call()
    # ie, ROI % in this rebase
    staking_rebase = staking_reward / circulating_supply
    # ie, ROI % in the next 5 days
    _ = math.pow(1 + staking_rebase, 5 * 3) - 1
    # ie, yearly APY
    staking_apy = math.pow(1 + staking_rebase, 365 * 3)

    print(f'APY: {staking_apy*100:,.2f}%')

    for guild in client.guilds:
        guser = guild.get_member(client.user.id)
        await guser.edit(nick=f'{staking_apy*100:,.2f}% APY')

        await client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name='Current APY'
            )
        )


client.run(BOT_TOKEN)
