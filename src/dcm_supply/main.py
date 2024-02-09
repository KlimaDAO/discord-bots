import os
import math

from discord.ext import tasks
from subgrounds.subgrounds import Subgrounds
from web3.middleware import geth_poa_middleware

from ..utils import (
    get_discord_client,
    get_polygon_web3,
    update_nickname,
    update_presence,
    get_last_metric,
    get_last_carbon,
    prettify_number,
    get_rebases_per_day,
    get_staking_params
)

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

sg = Subgrounds()

# Initialize web3
web3 = get_polygon_web3()
web3.middleware_onion.inject(geth_poa_middleware, layer=0)


def get_info():
    last_metric = get_last_metric(sg)
    total_carbon = sg.query([last_metric.treasuryCarbon])

    last_carbon = get_last_carbon(sg)
    current_sma, credit_supply = sg.query(
        [last_carbon.creditSMA, last_carbon.creditSupply]
    )
    return total_carbon, current_sma, credit_supply


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    if not update_info.is_running():
        update_info.start()


@tasks.loop(seconds=300)
async def update_info():
    staking_reward, epoch_length = get_staking_params(web3)
    rebases_per_day = get_rebases_per_day(epoch_length)

    treasury_carbon, carbon_sma, credit_supply = get_info()

    carbon_sma = carbon_sma / 1e18
    credit_supply = credit_supply / 1e18

    print(treasury_carbon)
    print(carbon_sma)
    if (
        treasury_carbon is not None
        and carbon_sma is not None
        and rebases_per_day is not None
    ):
        sma_percent = carbon_sma / credit_supply
        # ie, annualized reward %
        supply_change_annual = math.pow(1 + sma_percent, 365 * rebases_per_day) - 1
    else:
        return

    yield_text = f"{supply_change_annual*100:,.2f}% Δ DCM Supply"
    print(yield_text)

    success = await update_nickname(client, yield_text)
    if not success:
        return

    presence_txt = f'{prettify_number(credit_supply)}t Σ DCM Supply'
    success = await update_presence(
        client,
        presence_txt,
        type='playing'
    )
    if not success:
        return


client.run(BOT_TOKEN)
