import os
import json
import math
from web3 import Web3
import discord
from discord.ext import commands, tasks

BOT_TOKEN = os.environ["DISCORD_BCT_TREASURY_BOT_TOKEN"]

# Initialized Discord client
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(intents=intents, help_command=None, command_prefix='&?')

# Initialize web3
project_id = os.environ['WEB3_INFURA_PROJECT_ID']
polygon_mainnet_endpoint = f'https://polygon-mainnet.infura.io/v3/{project_id}'
web3 = Web3(Web3.HTTPProvider(polygon_mainnet_endpoint))
assert(web3.isConnected())

BCT_ADDRESS = Web3.toChecksumAddress("0x2f800db0fdb5223b3c3f354886d907a671414a7f")
TREASURY_ADDRESS = Web3.toChecksumAddress("0x7Dd4f0B986F032A44F913BF92c9e8b7c17D77aD7")
BCT_USDC_POOL_ADDRESS = Web3.toChecksumAddress("0x1e67124681b402064cd0abe8ed1b5c79d2e02f64")
KLIMA_BCT_POOL_ADDRESS = Web3.toChecksumAddress("0x9803c7ae526049210a1725f7487af26fe2c24614")

f = open('abis/sushi_pair.json')
SUSHI_PAIR_ABI = json.load(f)
f.close()

f = open('abis/bct.json')
BCT_ABI = json.load(f)
f.close()


def format_from_wei(i):
    return 1.0 * i / 10 ** 18


def get_owned_BCT_from_sushi(address):
    sushi_LP = web3.eth.contract(address=address, abi=SUSHI_PAIR_ABI)
    token1 = sushi_LP.functions.token1().call()
    reserve0, reserve1, _ = sushi_LP.functions.getReserves().call()
    treasury_SLP = sushi_LP.functions.balanceOf(TREASURY_ADDRESS).call()
    total_SLP = sushi_LP.functions.totalSupply().call()

    reserve = reserve0
    if token1.lower() == BCT_ADDRESS.lower():
        reserve = reserve1
    bct_supply = format_from_wei(reserve)
    ownership = treasury_SLP / total_SLP
    bct_owned = math.floor(bct_supply * ownership)
    return bct_owned


def get_treasury_balance():
    BCT_contract = web3.eth.contract(address=BCT_ADDRESS, abi=BCT_ABI)
    raw_BCT = format_from_wei(BCT_contract.functions.balanceOf(TREASURY_ADDRESS).call())
    bct_usdc = get_owned_BCT_from_sushi(BCT_USDC_POOL_ADDRESS)
    bct_klima = get_owned_BCT_from_sushi(KLIMA_BCT_POOL_ADDRESS)
    return raw_BCT + bct_usdc + bct_klima


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    try:
        bct_treasury = get_treasury_balance()
    except ValueError:
        bct_treasury = None

    if bct_treasury is not None:
        print(f'{bct_treasury:,.2f} BCT')

    for guild in client.guilds:
        guser = guild.get_member(client.user.id)
        await guser.edit(nick=f'{bct_treasury:,.2f} BCT')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Toucan Protocol'))  # noqa: E501

client.run(BOT_TOKEN)
