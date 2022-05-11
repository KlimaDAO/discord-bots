import os
from discord.ext import tasks

from subgrounds.subgrounds import Subgrounds

from ..constants import MCO2_ADDRESS, MCO2_DECIMALS, BCT_ADDRESS, BCT_DECIMALS, \
                        NCT_ADDRESS, NCT_DECIMALS, NBO_ADDRESS, NBO_DECIMALS, UBO_ADDRESS, UBO_DECIMALS
from ..contract_info import token_supply
from ..utils import get_discord_client, \
                    get_polygon_web3, get_eth_web3, load_abi, update_nickname, update_presence, get_last_metric

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialize web3
web3 = get_polygon_web3()
web3_eth = get_eth_web3()

# Load ABI
pool_abi = load_abi('carbon_pool.json')

# Initialized Discord client
client = get_discord_client()

sg = Subgrounds()

def get_info():
     runway = get_runway()
     total_carbon_supply = get_total_carbon_supply()
     return runway, total_carbon_supply

def get_runway():
     last_metric = get_last_metric(sg)
     runway = sg.query([last_metric.runwayCurrent])

     return runway

def get_total_carbon_supply():
    try:
        bct_supply = token_supply(web3, BCT_ADDRESS, pool_abi, BCT_DECIMALS)
        mco2_supply = token_supply(web3_eth, MCO2_ADDRESS, pool_abi, MCO2_DECIMALS)
        ubo_supply = token_supply(web3, UBO_ADDRESS, pool_abi, UBO_DECIMALS)
        nbo_supply = token_supply(web3, NBO_ADDRESS, pool_abi, NBO_DECIMALS)
        nct_supply = token_supply(web3, NCT_ADDRESS, pool_abi, NCT_DECIMALS)

        total_amount = bct_supply + mco2_supply + ubo_supply + nbo_supply + nct_supply
        return total_amount
    except Exception:
        # Exception will occur if any of the supply values are None
        return None

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    runway, total_carbon_supply = get_info()

    if runway is not None and total_carbon_supply is not None:

        runway_rounded = round(runway)
        success = await update_nickname(client, f'Runway: {runway_rounded} days')
        if not success:
            return

        success = await update_presence(client, f'Total carbon supply: {total_carbon_supply/1e6:,.1f}M')
        if not success:
            return

client.run(BOT_TOKEN)