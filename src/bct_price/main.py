import os
import json
from web3 import Web3
import discord
from discord.ext import commands, tasks

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

BCT_ADDRESS = '0x2f800db0fdb5223b3c3f354886d907a671414a7f'

# Initialized Discord client
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(intents=intents, help_command=None, command_prefix='&?')

# Initialize web3
project_id = os.environ['WEB3_INFURA_PROJECT_ID']
polygon_mainnet_endpoint = f'https://polygon-mainnet.infura.io/v3/{project_id}'
web3 = Web3(Web3.HTTPProvider(polygon_mainnet_endpoint))
assert(web3.isConnected())

# Load ABIs
script_dir = os.path.dirname(__file__)
abi_dir = os.path.join(script_dir, 'abis')

with open(os.path.join(abi_dir, 'sushiswap_pool.json'), 'r') as f:
    sushi_abi = json.loads(f.read())

with open(os.path.join(abi_dir, 'carbon_pool.json'), 'r') as f:
    bct_abi = json.loads(f.read())


def lp_contract_info(sushi_address, basePrice=1):
    sushiLP = web3.eth.contract(
        address=Web3.toChecksumAddress(sushi_address),
        abi=sushi_abi
    )

    try:
        reserves = sushiLP.functions.getReserves().call()
        tokenPrice = reserves[0] * basePrice * 1e12 / reserves[1]

        return tokenPrice
    except Exception:
        return None


def get_bct_supply():
    bct = web3.eth.contract(
        address=Web3.toChecksumAddress(BCT_ADDRESS),
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
    price = lp_contract_info(sushi_address='0x1e67124681b402064cd0abe8ed1b5c79d2e02f64')
    supply = get_bct_supply()

    if price is not None and supply is not None:
        print(f'${price:,.2f} BCT')

        for guild in client.guilds:
            guser = guild.get_member(client.user.id)
            try:
                await guser.edit(nick=f'${price:,.2f} BCT')
            except discord.errors.HTTPException:
                return

        try:
            await client.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f'Supply: {supply/1e6:,.1f}M'
                )
            )
        except discord.errors.HTTPException:
            return


client.run(BOT_TOKEN)
