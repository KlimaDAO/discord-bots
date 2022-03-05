import os
import json
import datetime
import decimal

import discord
from discord.ext import tasks
from discord.commands import Option
from web3 import Web3

from ..constants import STAKING_ADDRESS, SKLIMA_ADDRESS, BCT_ADDRESS, USDC_ADDRESS, \
    BCT_USDC_POOL, KLIMA_BCT_POOL
from ..utils import get_discord_client, get_polygon_web3, load_abi
from .airtable_utils import alert_db, bond_db, search_alert, activate_alert, deactivate_alert, fetch_bond_md, \
    fetch_bond_info, active_bonds, update_bond_info, add_alert, remove_alert

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Initialized Discord client
client = get_discord_client()

# Initialize web3
web3 = get_polygon_web3()

# Load ABIs
SKLIMA_ABI = load_abi('sklima.json')
BOND_ABI = load_abi('klima_bond.json')
STAKING_ABI = load_abi('klima_staking.json')
TOKEN_ABI = load_abi('erc20_token.json')

# Init global variables
last_call = datetime.datetime.now() - datetime.timedelta(minutes=10)
klima_price_usd, bct_price_usd, rebase, staking_rewards = 0, 0, 0, 0
bond_info = {}


def base_token_price(lp_address, known_address, known_price):
    # Retrieve token price by using the LP token
    try:
        address = Web3.toChecksumAddress(lp_address)
        abi = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"sync","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]')  # noqa: E501
        LP_contract = web3.eth.contract(address=address, abi=abi)
        reserves = LP_contract.functions.getReserves().call()

        address0 = LP_contract.functions.token0().call()
        address1 = LP_contract.functions.token1().call()
        token0 = web3.eth.contract(address=address0, abi=TOKEN_ABI)
        token1 = web3.eth.contract(address=address1, abi=TOKEN_ABI)
        decimals0 = token0.functions.decimals().call()
        decimals1 = token1.functions.decimals().call()

        if Web3.toChecksumAddress(known_address) == address0:
            tokenPrice = known_price * \
                reserves[0] * 10**decimals1 / (reserves[1] * 10**decimals0)
        else:
            tokenPrice = known_price * \
                reserves[1] * 10**decimals0 / (reserves[0] * 10**decimals1)

        return(tokenPrice)

    except Exception as e:
        print('base_token_price error')
        print(e)


def lp_price(lp_address):
    # Retrieve price of the LP token
    try:
        LP_address = Web3.toChecksumAddress(lp_address)
        LP_abi = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"sync","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]')  # noqa: E501
        LP_contract = web3.eth.contract(address=LP_address, abi=LP_abi)

        address0 = LP_contract.functions.token0().call()
        address1 = LP_contract.functions.token1().call()
        token0 = web3.eth.contract(address=address0, abi=TOKEN_ABI)
        token1 = web3.eth.contract(address=address1, abi=TOKEN_ABI)

        get_reserves = LP_contract.functions.getReserves().call()
        amount0 = get_reserves[0] / 10**token0.functions.decimals().call()
        amount1 = get_reserves[1] / 10**token1.functions.decimals().call()
        return(decimal.Decimal(amount0 / amount1))

    except Exception as e:
        print('lp_price error')
        print(e)


def fetch_staking_rewards():
    try:
        # Retrieve staking rewards and calculate 5 day ROI
        distrib = web3.eth.contract(address=STAKING_ADDRESS, abi=STAKING_ABI)
        distrib_info = distrib.functions.epoch().call()
        rewards = distrib_info[3]

        sKLIMA = web3.eth.contract(address=SKLIMA_ADDRESS, abi=SKLIMA_ABI)
        circ_supply = sKLIMA.functions.circulatingSupply().call()

        # print("Staking:")
        # print(f'   Next epoch rewards: {(100 * rewards / circ_supply):,.2f} %')
        # print(
        #     f'   5 days ROI: {(100 * (1 + rewards/circ_supply)**float(15) - 100):,.2f} %')
        # print('\n')
        rebase = rewards / circ_supply
        staking_rewards = (1 + rewards / circ_supply)**float(15) - 1
        return(rebase, 100 * staking_rewards)

    except Exception as e:
        print('fetch_staking_rewards error')
        print(e)
        return None, None


def contract_info(bond_address, payoutTokenPrice, maxReached=False):
    if maxReached is True:
        return(-999, -999, -999)
    else:
        try:
            # Retrieve bond prices and it's current discount
            bond = web3.eth.contract(address=bond_address, abi=BOND_ABI)

            # Bonds are priced in BCTs despide the function is called bondPriceInUSD
            # print('Bonds:')
            BondPriceUSD = bond.functions.bondPriceInUSD().call() / 1e18
            MaxCap = bond.functions.maxPayout().call() / 1e9
            Disc = (decimal.Decimal(payoutTokenPrice) - decimal.Decimal(BondPriceUSD)) / decimal.Decimal(payoutTokenPrice)  # noqa: E501
            # print(f' BondPrice: {BondPriceUSD:,.2f}BCT')
            # print(f' Discount: {100 * Disc:,.2f} %')
            return(payoutTokenPrice, 100 * Disc, MaxCap)

        except Exception as e:
            print('contract_info error')
            print(e)


def max_debt_reached(bond_address):
    try:
        bond = web3.eth.contract(address=bond_address, abi=BOND_ABI)
        currentDebt = bond.functions.currentDebt().call()
        maxDebt = bond.functions.terms().call()
        if currentDebt >= maxDebt[-1]:
            return(True)
        else:
            return(False)

    except Exception as e:
        print(e)


def check_is_worth(staking_rewards, rebase, bondDiscount):
    cutoff_discount = bondDiscount + \
        ((1 + rebase)) * (1 - (1 + rebase)**15) / (1 - (1 + rebase)) / 15 - 1
    if staking_rewards >= cutoff_discount:
        return(':no_entry:', cutoff_discount)
    else:
        return(':white_check_mark:', cutoff_discount)


def get_prices():
    global last_call
    global klima_price_usd, bct_price_usd, rebase, staking_rewards, bond_info
    bond_list = active_bonds(bond_db)

    if datetime.datetime.now() - datetime.timedelta(seconds=120) >= last_call:
        # Retrieve prices
        bct_price_usd = base_token_price(
            lp_address=BCT_USDC_POOL, known_address=USDC_ADDRESS, known_price=1
        )
        klima_price_usd = base_token_price(
            lp_address=KLIMA_BCT_POOL, known_address=BCT_ADDRESS, known_price=bct_price_usd
        )
        klima_price_bct = klima_price_usd / bct_price_usd
        last_call = datetime.datetime.now()

        # Update staking rewards
        rebase, staking_rewards = fetch_staking_rewards()

        # Update bond info
        for b in bond_list:
            address, abi = fetch_bond_md(bond_db, b)
            is_closed = max_debt_reached(
                bond_address=Web3.toChecksumAddress(address))
            price, disc, bond_max = contract_info(bond_address=Web3.toChecksumAddress(address), payoutTokenPrice=klima_price_bct, maxReached=is_closed)  # noqa: E501
            update_bond_info(bond_db, update_bond=b, update_price=price, update_disc=float(disc), update_capacity=bond_max, update_debt=is_closed)  # noqa: E501

    for b in bond_list:
        last_info = fetch_bond_info(bond_db, b)
        bond_info[b] = last_info

    return(klima_price_usd, rebase, staking_rewards, bond_info)


# Create a class for the embed
class PageButton(discord.ui.Button):
    def __init__(self, current, pages):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label=f"Page {current + 1}/{pages + 1}",
            disabled=True, custom_id='page'
        )


class Pagination(discord.ui.View):
    def __init__(self, paginationList):
        super().__init__(timeout=10)
        self.value = 0
        self.pages = len(paginationList) - 1
        self.paginationList = paginationList
        self.add_item(PageButton(current=self.value, pages=self.pages))
        self.message = 0

    async def on_timeout(self):
        for b in self.children:
            b.disabled = True
        await self.message.edit(embed=self.paginationList[self.value], view=self)

    @discord.ui.button(label="Prev Page", style=discord.ButtonStyle.primary)
    async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.value - 1 < 0:
            self.value = self.pages
        else:
            self.value = self.value - 1
        for b in self.children:
            if b.custom_id == 'page':
                self.remove_item(b)
                self.add_item(PageButton(current=self.value, pages=self.pages))
        await interaction.response.edit_message(embed=self.paginationList[self.value], view=self)

    @discord.ui.button(label="Next Page", style=discord.ButtonStyle.primary)
    async def prev_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.value + 1 > self.pages:
            self.value = 0
        else:
            self.value = self.value + 1
        for b in self.children:
            if b.custom_id == 'page':
                self.remove_item(b)
                self.add_item(PageButton(current=self.value, pages=self.pages))
        await interaction.response.edit_message(embed=self.paginationList[self.value], view=self)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not check_discounts.is_running():
        check_discounts.start()


@tasks.loop(seconds=30)
async def check_discounts():
    klima_price_usd, rebase, staking_rewards, bond_info = get_prices()

    if klima_price_usd is None or rebase is None or staking_rewards is None or bond_info is None:
        return

    for bond, values in bond_info.items():
        if values.debt_reached is False:
            # Reactivate alerts if discounts have diminished enough
            reactivate = search_alert(alert_db, search_bond=bond, search_discount=values.discount, search_type='reactivate')  # noqa: E501
            for alert in reactivate:
                activate_alert(alert_db, search_bond=bond,
                               search_discount=alert.discount, search_user=alert.user)
                print(
                    f'Alert reset for {bond} at more than {values.discount}% discount')

            # Send alerts if discounts are big enough
            triggered = search_alert(alert_db, search_bond=bond, search_discount=values.discount, search_type='triggered')  # noqa: E501
            for alert in triggered:
                deactivate_alert(alert_db, search_bond=bond,
                                 search_discount=alert.discount, search_user=alert.user)
                is_worth, max_bond_disc = check_is_worth(
                    staking_rewards, rebase, values.discount)

                embed = discord.Embed(title='Big Bond Discount!', description=f':small_blue_diamond: 5 day ROI for **staking** sits at **{staking_rewards:,.2f}%** \n :small_blue_diamond: Current **KLIMA** price is **${klima_price_usd:,.2f}** \n :small_blue_diamond: Some of your alert thresholds have been reached by current bond discounts', colour=0x17d988)  # noqa: E501
                embed.add_field(name='Bond Type',
                                value=values.bond, inline=True)
                embed.add_field(name='Discount',
                                value=f' {values.discount:,.2f}%', inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                embed.add_field(name='Could beat staking',
                                value=is_worth, inline=True)
                embed.add_field(name='Compound Discount',
                                value=f' {max_bond_disc:,.2f}%', inline=True)
                embed.add_field(
                    name='Max payout', value=f'{values.max_purchase:,.2f} KLIMA', inline=True)
                embed.set_footer(
                    text='This alert is courtesy of your Klimate @0xRusowsky')

                user = client.get_user(int(alert.user))
                await user.send(embed=embed)


@client.slash_command(description="Check live information for every bond type issued by KlimaDAO.")
async def bonds(ctx):
    global klima_price_usd, rebase, staking_rewards, bond_info

    info = []
    await ctx.defer(ephemeral=True)
    for bond, values in bond_info.items():
        info.append((bond, check_is_worth(staking_rewards, rebase, values.discount), values.discount, values.max_purchase, values.debt_reached))  # noqa: E501
    info = sorted(info, key=lambda x: x[2], reverse=True)

    fields = []
    for i in info:
        if i[4] is False:
            fields = fields + [(('Bond Type', i[0]), ('Discount', f'{i[2]:,.2f}%'), ('Could be profitable?', i[1][0]), ('Compound Discount', f' {i[1][1]:,.2f}%'), ('Max payout', f'{i[3]:,.2f} KLIMA'))]  # noqa: E501
        else:
            fields = fields + \
                [(('Bond Type', i[0]), ('Sold Out  :no_entry:', "Max Debt Reached"))]

    lfields = [fields[i * 4:(i + 1) * 4]
               for i in range((len(fields) + 4 - 1) // 4)]
    paginationList = []
    page = 0
    for lf in lfields:
        page = page + 1
        embed = discord.Embed(title="Current KlimaDAO Bond Discounts", description=f":small_blue_diamond: 5 day ROI for **staking** sits at **{staking_rewards:,.2f}%** \n :small_blue_diamond: Current **KLIMA** price is **${klima_price_usd:,.2f}**", colour=0xFFFFFF)  # noqa: E501
        for f in lf:
            if len(f) > 2:
                embed.add_field(name=f[0][0], value=f[0][1], inline=True)
                embed.add_field(name=f[1][0], value=f[1][1], inline=True)
                embed.add_field(name=f[2][0], value=f[2][1], inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                embed.add_field(name=f[3][0], value=f[3][1], inline=True)
                embed.add_field(name=f[4][0], value=f[4][1], inline=True)
            else:
                embed.add_field(name=f[0][0], value=f[0][1], inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
                embed.add_field(name=f[1][0], value=f[1][1], inline=True)
        paginationList.append(embed)

    if len(paginationList) == 1:
        await ctx.followup.send(embed=paginationList[0])
    else:
        view = Pagination(paginationList=paginationList)
        await ctx.respond(embed=paginationList[view.value], view=view)
        view.message = await ctx.interaction.original_message()


@client.slash_command(description="Check the available bond types that KlimaDAO offers and that this bot supports.")
async def info_bonds(ctx):
    if not check_discounts.is_running():
        check_discounts.start()

    bond_list = active_bonds(bond_db)
    embed = discord.Embed(title="KlimaDAO Bond Types", description=f"KlimaDAO currently offers {len(bond_list)} bond types.", colour=0xFFFFFF)  # noqa: E501
    for b in bond_list:
        address, abi = fetch_bond_md(bond_db, b)
        embed.add_field(name='Bond Type', value=b, inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        embed.add_field(
            name='Contract', value=f'[Link](https://polygonscan.com/address/{address})', inline=True)

    await ctx.respond(embed=embed)


@client.slash_command(description='Create alerts that will be triggered according to bond discount.')
async def create_alert(
    ctx,
    bond_type: Option(str, "Input the desired bond. Use the /info_bonds command to see all the bond types."),  # noqa: F722,E501
    min_discount: Option(float, "Input the min_discount threshold. Must be a number, without '%' sign."),  # noqa: F722,E501
):
    bond_list = active_bonds(bond_db)
    bond_str = ""
    for b in bond_list:
        bond_str = bond_str + " \n :black_small_square: " + b
    bond = bond_type.upper()

    code = add_alert(alert_db, add_bond=bond_type,
                     add_discount=min_discount, add_user=str(ctx.author.id))
    if code == 1:
        embed = discord.Embed(title="New Bond Alert Configured", description=f'{ctx.author.mention} has created a new alert for discounts over {min_discount}% on {bond} bonds!', colour=0x17d988)  # noqa: E501
        await ctx.respond(embed=embed)
    elif code == 0:
        embed = discord.Embed(title="Bond Alert Already Configured", description=f'{ctx.author.mention} already had an alert for discounts over {min_discount}% on {bond} bonds.', colour=0xd14d4d)  # noqa: E501
        await ctx.respond(embed=embed)
    elif code == -1:
        embed = discord.Embed(title="Configuration Error", description=f"{ctx.author.mention} already had 5 alerts configured. Don't be greedy ser!", colour=0xd14d4d)  # noqa: E501
        await ctx.respond(embed=embed)
    elif code == -2:
        embed = discord.Embed(title="Configuration Error", description=f"Incorrect bond type: **{bond}**. \n  The input value for a bond must be within the following: **{bond_str}** ", colour=0xd14d4d)  # noqa: E501
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title="Configuration Error", description="Unexpected error. Please try again. If the error persists, contact @0xRusowsky", colour=0xd14d4d)  # noqa: E501
        await ctx.respond(embed=embed)


@client.slash_command(description='Delete an existing bond alert')
async def delete_alert(
    ctx,
    bond_type: Option(str, "Input the desired bond (use the /info_bonds command to see all the bond types)."),  # noqa: F722,E501
    min_discount: Option(float, "Input the min_discount threshold (must be a number, without '%' sign)."),  # noqa: F722,E501
):
    bond = bond_type.upper()

    code = remove_alert(alert_db, delete_bond=bond_type,
                        delete_discount=min_discount, delete_user=ctx.author.id)
    if code == 1:
        embed = discord.Embed(title="Bond Alert Deleted", description=f'{ctx.author.mention} has deleted an alert for discounts over {min_discount}% on {bond} bonds!', colour=0x17d988)  # noqa: E501
        await ctx.respond(embed=embed)
    elif code == 0:
        embed = discord.Embed(title="Alert Doesn't Exist", description=f'{ctx.author.mention} does not have any alerts for discounts over {min_discount}% on {bond} bonds.', colour=0xFFFFFF)  # noqa: E501
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title="Configuration Error", description="Unexpected error. Please try again. If the error persists, contact @0xRusowsky", colour=0xd14d4d)  # noqa: E501
        await ctx.respond(embed=embed)


@client.slash_command(description='Delete all the previously configured bond alerts.')
async def delete_all(ctx):
    alert_list = search_alert(alert_db, search_user=str(ctx.author.id))
    if len(alert_list) > 0:
        check = 0
        for a in alert_list:
            code = remove_alert(alert_db, delete_bond=a.bond,
                                delete_discount=a.discount, delete_user=a.user)
            check += code
        if check == len(alert_list):
            embed = discord.Embed(title="All Bond Alerts Deleted", description=f'{ctx.author.mention} has deleted all bond alerts!', colour=0x17d988)  # noqa: E501
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="Configuration Error", description="Unexpected error. Please try again. If the error persists, contact @0xRusowsky", colour=0xd14d4d)  # noqa: E501
            await ctx.respond(embed=embed)

    else:
        embed = discord.Embed(title="No Alerts Configured", description=f'{ctx.author.mention} does not have any configured alerts.', colour=0xFFFFFF)  # noqa: E501
        await ctx.respond(embed=embed)


@client.slash_command(description='Check all the already existing alerts.')
async def my_alerts(ctx):
    alert_list = search_alert(alert_db, search_user=str(ctx.author.id))
    if len(alert_list) > 0:
        embed = discord.Embed(title="Configured Alerts", description=f'{ctx.author.mention} currently has the following alerts configured.', colour=0xFFFFFF)  # noqa: E501
        for a in alert_list:
            embed.add_field(name='Bond Type', value=a.bond, inline=True)
            embed.add_field(name='Discount',
                            value=f'{a.discount}%', inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=True)
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title="No Alerts", description=f'{ctx.author.mention} has not configured any alerts yet. \n To create new alerts use the  **/create_alert**  command and follow the instructions.', colour=0xFFFFFF)  # noqa: E501
        await ctx.respond(embed=embed)


@client.slash_command(description="Check all the commands and a brief explanation on how to use them.")
async def help_bonds(ctx):
    embed = discord.Embed(title='Help Panel', description='Here you can see a list with all the KlimaDAO Alerts commands and a brief explanation on how to use them.', colour=0xFFFFFF)  # noqa: E501
    embed.add_field(name=':small_blue_diamond: /info_bonds', value='Returns a list with the names of the partners, the bond types and the payout tokens that KlimaDAO offers.', inline=False)  # noqa: E501
    embed.add_field(name=':small_blue_diamond: /bonds', value='Returns all the live information for every bond type issued by KlimaDAO.', inline=False)  # noqa: E501
    embed.add_field(name=':small_blue_diamond: /my_alerts', value='Returns a list with all the alerts that the user has configured.', inline=False)  # noqa: E501
    embed.add_field(name=':small_orange_diamond: /create_alert', value='Creates a new alert that will be triggered when bond discounts are greater than *min_discount*. \n :black_small_square: **bond_type:**  must belong to the ones listed under  **/info_bonds**  \n :black_small_square: **min_discount:**  XX.XX (number expressed in %)', inline=False)  # noqa: E501
    embed.add_field(name=':small_orange_diamond: /delete_all', value='Deletes all the alerts that the user previously configured.', inline=False)  # noqa: E501
    embed.add_field(name=':small_orange_diamond: /delete_alert', value='Deletes an existing bond alert. \n :black_small_square: **bond_type:**  must belong to  the ones listed under  **/info_bonds** \n :black_small_square: **min_discount:**  XX.XX (number expressed in %) \n ', inline=False)  # noqa: E501

    embed.set_footer(
        text='If you have any ideas or improvement suggestions please DM your klimate @0xRusowsky')
    await ctx.respond(embed=embed)


client.run(BOT_TOKEN)
