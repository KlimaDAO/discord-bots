import os
import json
from web3 import Web3
import discord
from discord.ext import commands, tasks

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
MOSS_ADDRESS = '0xAa7DbD1598251f856C12f63557A4C4397c253Cea'

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

with open(os.path.join(abi_dir, 'uniswap_pool.json'), 'r') as f:
    uni_abi = json.loads(f.read())

with open(os.path.join(abi_dir, 'carbon_pool.json'), 'r') as f:
    moss_abi = json.loads(f.read())


def lp_contract_info(uni_address, basePrice=1):
    uniLP = web3.eth.contract(
        address=Web3.toChecksumAddress(uni_address),
        abi=uni_abi
    )

    try:
        reserves = uniLP.functions.getReserves().call()
        tokenPrice = reserves[0] * basePrice * 1e12 / reserves[1]

        return tokenPrice
    except Exception:
        return None


def get_moss_supply():
    moss = web3.eth.contract(
        address=Web3.toChecksumAddress(MOSS_ADDRESS),
        abi=moss_abi
    )

    try:
        decimals = moss.functions.decimals().call()
        total_supply = moss.functions.totalSupply().call() / 10**decimals
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
    price = lp_contract_info(uni_address='0x68aB4656736d48bb1DE8661b9A323713104e24cF')
    supply = get_moss_supply()

    if price is not None and supply is not None:
        print(f'${price:,.2f} MCO2')

        for guild in client.guilds:
            guser = guild.get_member(client.user.id)
            try:
                await guser.edit(nick=f'${price:,.2f} MCO2')
            except discord.errors.HTTPException:
                return

        try:
            await client.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f'Supply: {supply/1e3:,.1f}k'
                )
            )
        except discord.errors.HTTPException:
            return


client.run(BOT_TOKEN)
