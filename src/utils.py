import os

import discord
from discord.ext import commands
import json
from web3 import Web3

INFURA_PROJ_ID = os.environ['WEB3_INFURA_PROJECT_ID']


def get_polygon_web3():
    polygon_mainnet_endpoint = f'https://polygon-mainnet.infura.io/v3/{INFURA_PROJ_ID}'

    web3 = Web3(Web3.HTTPProvider(polygon_mainnet_endpoint))

    assert(web3.isConnected())

    return web3


def get_eth_web3():
    ethereum_mainnet_endpoint = f'https://mainnet.infura.io/v3/{INFURA_PROJ_ID}'

    web3_eth = Web3(Web3.HTTPProvider(ethereum_mainnet_endpoint))

    assert(web3_eth.isConnected())

    return web3_eth


def get_discord_client(members_intent=False, presences_intent=False):
    intents = discord.Intents.default()
    intents.members = members_intent
    intents.presences = presences_intent

    client = commands.Bot(intents=intents, help_command=None, command_prefix='&?')

    return client


def load_abi(filename):
    '''Load a single ABI from the `abis` folder under `src`'''
    script_dir = os.path.dirname(__file__)
    abi_dir = os.path.join(script_dir, 'abis')

    with open(os.path.join(abi_dir, filename), 'r') as f:
        abi = json.loads(f.read())

    return abi


async def update_nickname(client, nickname_text):
    for guild in client.guilds:
        guser = guild.get_member(client.user.id)
        try:
            await guser.edit(nick=nickname_text)
        except discord.errors.HTTPException:
            return False

    return True


async def update_presence(client, text, type='watching'):
    if type == 'watching':
        type = discord.ActivityType.watching
    elif type == 'playing':
        type = discord.ActivityType.playing
    else:
        raise ValueError(
            'Invalid value for type passed to update_presence! '
            'Must be either "watching" or "playing"'
        )

    try:
        await client.change_presence(
            activity=discord.Activity(
                type=type,
                name=text
            )
        )
        return True
    except discord.errors.HTTPException:
        return False
