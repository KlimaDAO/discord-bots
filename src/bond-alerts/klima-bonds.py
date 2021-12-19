import os
import db
import json
import datetime
import decimal
from web3 import Web3
import discord
from discord import message
from discord.ext import commands, tasks
from discord.app import Option


BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN_KLIMA_BOND_ALERTS"]

# Initialize Discord client
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(intents=intents, help_command=None)

# Initialize web3
INFURA_TOKEN = os.environ['WEB3_INFURA_TOKEN_3']
infuraURL = f'https://polygon-mainnet.infura.io/v3/{INFURA_TOKEN}'
web3 = Web3(Web3.HTTPProvider(infuraURL))

#init global variables
last_call = datetime.datetime.now() - datetime.timedelta(minutes=10)
klimaPriceUSD, bctPriceUSD, rebase, stakingRewards, bctClosed, bctPrice, bctDisc, bctMax, bctUsdClosed, bctUsdPrice, bctUsdDisc, bctUsdMax, klimaBctClosed, klimaBctPrice, klimaBctDisc, klimaBctMax = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  # noqa: E501


def lp_base_token_price(lp_address, basePrice=1):
    #retrieve price of the base token from the SLP
    try:
        address = Web3.toChecksumAddress(lp_address)
        abi = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"sync","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]')  # noqa: E501
        LP_contract = web3.eth.contract(address=address, abi=abi)
        Reserves = LP_contract.functions.getReserves().call()

        # usdc-bct
        if lp_address == '0x1e67124681b402064cd0abe8ed1b5c79d2e02f64':
            tokenPrice = Reserves[0]*basePrice*1e12/Reserves[1]
        # bct-klima
        else:
            tokenPrice = Reserves[0]*basePrice/(Reserves[1]*1e9)
        return(tokenPrice)

    except Exception as e:
        print(e)


def lp_price(lp_address):
    #retrieve price of the SLP token
    try:
        LP_address = Web3.toChecksumAddress(lp_address)
        LP_abi = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"caller","type":"address"}],"name":"MetaTxnsDisabled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"caller","type":"address"}],"name":"MetaTxnsEnabled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"disableMetaTxns","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"enableMetaTxns","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"forwarder","type":"address"}],"name":"isTrustedForwarder","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"metaTxnsEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"sync","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]')  # noqa: E501
        LP_contract = web3.eth.contract(address=LP_address, abi=LP_abi)

        get_reserves = LP_contract.functions.getReserves().call()
        amount0 = get_reserves[0]/1e18
        amount1 = get_reserves[1]/1e9
        return(decimal.Decimal(amount0/amount1))

    except Exception as e:
        print(e)


def staking_rewards():
    try:
        #retrieve staking rewards and calculate 5 day ROI
        distrib_address = Web3.toChecksumAddress('0x25d28a24Ceb6F81015bB0b2007D795ACAc411b4d')
        distrib_abi = json.loads('[{"inputs":[{"internalType":"address","name":"_KLIMA","type":"address"},{"internalType":"address","name":"_sKLIMA","type":"address"},{"internalType":"uint256","name":"_epochLength","type":"uint256"},{"internalType":"uint256","name":"_firstEpochNumber","type":"uint256"},{"internalType":"uint256","name":"_firstEpochBlock","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPulled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPushed","type":"event"},{"inputs":[],"name":"KLIMA","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_recipient","type":"address"}],"name":"claim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"contractBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"distributor","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"epoch","outputs":[{"internalType":"uint256","name":"length","type":"uint256"},{"internalType":"uint256","name":"number","type":"uint256"},{"internalType":"uint256","name":"endBlock","type":"uint256"},{"internalType":"uint256","name":"distribute","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"forfeit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"giveLockBonus","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"index","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"locker","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"manager","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pullManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner_","type":"address"}],"name":"pushManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"rebase","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"returnLockBonus","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"sKLIMA","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"enum KlimaStaking.CONTRACTS","name":"_contract","type":"uint8"},{"internalType":"address","name":"_address","type":"address"}],"name":"setContract","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_warmupPeriod","type":"uint256"}],"name":"setWarmup","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"address","name":"_recipient","type":"address"}],"name":"stake","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"toggleDepositLock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"totalBonus","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bool","name":"_trigger","type":"bool"}],"name":"unstake","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"warmupContract","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"warmupInfo","outputs":[{"internalType":"uint256","name":"deposit","type":"uint256"},{"internalType":"uint256","name":"gons","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"bool","name":"lock","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"warmupPeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')  # noqa: E501
        distrib = web3.eth.contract(address = distrib_address, abi = distrib_abi)
        distrib_info = distrib.functions.epoch().call()
        rewards = distrib_info[3]

        sKLIMA_address = Web3.toChecksumAddress('0xb0C22d8D350C67420f06F48936654f567C73E8C8')
        sKLIMA_abi = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"epoch","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"rebase","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"index","type":"uint256"}],"name":"LogRebase","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"stakingContract","type":"address"}],"name":"LogStakingContractUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"epoch","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"totalSupply","type":"uint256"}],"name":"LogSupply","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPulled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPushed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"INDEX","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner_","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gons","type":"uint256"}],"name":"balanceForGons","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"who","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"circulatingSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"gonsForBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"index","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"stakingContract_","type":"address"}],"name":"initialize","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"initializer","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"manager","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"pullManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner_","type":"address"}],"name":"pushManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"profit_","type":"uint256"},{"internalType":"uint256","name":"epoch_","type":"uint256"}],"name":"rebase","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"rebases","outputs":[{"internalType":"uint256","name":"epoch","type":"uint256"},{"internalType":"uint256","name":"rebase","type":"uint256"},{"internalType":"uint256","name":"totalStakedBefore","type":"uint256"},{"internalType":"uint256","name":"totalStakedAfter","type":"uint256"},{"internalType":"uint256","name":"amountRebased","type":"uint256"},{"internalType":"uint256","name":"index","type":"uint256"},{"internalType":"uint256","name":"blockNumberOccured","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_INDEX","type":"uint256"}],"name":"setIndex","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"stakingContract","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]')  # noqa: E501
        sKLIMA = web3.eth.contract(address = sKLIMA_address, abi = sKLIMA_abi)
        circ_supply = sKLIMA.functions.circulatingSupply().call()

        print("Staking:")
        print(f'   Next epoch rewards: {(100*rewards/circ_supply):,.2f} %')
        print(f'   5 days ROI: {(100 * (1+rewards/circ_supply)**float(15)-100):,.2f} %')
        print('\n')
        rebase = rewards/circ_supply
        staking_rewards = (1+rewards/circ_supply)**float(15)-1 
        return(rebase, staking_rewards)

    except Exception as e:
        print(e)


def contract_info(bond_address, payoutTokenPrice=0, maxReached=False):
    if maxReached == True:
        return(-999, -999, -999)
    else:
        try:
            #retrieve bond prices and it's current discount
            address = bond_address
            abi = json.loads('[{"inputs":[{"internalType":"address","name":"_KLIMA","type":"address"},{"internalType":"address","name":"_principle","type":"address"},{"internalType":"address","name":"_treasury","type":"address"},{"internalType":"address","name":"_DAO","type":"address"},{"internalType":"address","name":"_bondCalculator","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"deposit","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"payout","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"expires","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"priceInUSD","type":"uint256"}],"name":"BondCreated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"priceInUSD","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"internalPrice","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"debtRatio","type":"uint256"}],"name":"BondPriceChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"recipient","type":"address"},{"indexed":false,"internalType":"uint256","name":"payout","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"remaining","type":"uint256"}],"name":"BondRedeemed","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"initialBCV","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newBCV","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"adjustment","type":"uint256"},{"indexed":false,"internalType":"bool","name":"addition","type":"bool"}],"name":"ControlVariableAdjustment","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPulled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPushed","type":"event"},{"inputs":[],"name":"DAO","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"KLIMA","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"adjustment","outputs":[{"internalType":"bool","name":"add","type":"bool"},{"internalType":"uint256","name":"rate","type":"uint256"},{"internalType":"uint256","name":"target","type":"uint256"},{"internalType":"uint256","name":"buffer","type":"uint256"},{"internalType":"uint256","name":"lastBlock","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bondCalculator","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"bondInfo","outputs":[{"internalType":"uint256","name":"payout","type":"uint256"},{"internalType":"uint256","name":"vesting","type":"uint256"},{"internalType":"uint256","name":"lastBlock","type":"uint256"},{"internalType":"uint256","name":"pricePaid","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bondPrice","outputs":[{"internalType":"uint256","name":"price_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bondPriceInUSD","outputs":[{"internalType":"uint256","name":"price_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"currentDebt","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"debtDecay","outputs":[{"internalType":"uint256","name":"decay_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"debtRatio","outputs":[{"internalType":"uint256","name":"debtRatio_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint256","name":"_maxPrice","type":"uint256"},{"internalType":"address","name":"_depositor","type":"address"}],"name":"deposit","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_controlVariable","type":"uint256"},{"internalType":"uint256","name":"_vestingTerm","type":"uint256"},{"internalType":"uint256","name":"_minimumPrice","type":"uint256"},{"internalType":"uint256","name":"_maxPayout","type":"uint256"},{"internalType":"uint256","name":"_fee","type":"uint256"},{"internalType":"uint256","name":"_maxDebt","type":"uint256"},{"internalType":"uint256","name":"_initialDebt","type":"uint256"}],"name":"initializeBondTerms","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"isLiquidityBond","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastDecay","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxPayout","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_value","type":"uint256"}],"name":"payoutFor","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_depositor","type":"address"}],"name":"pendingPayoutFor","outputs":[{"internalType":"uint256","name":"pendingPayout_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_depositor","type":"address"}],"name":"percentVestedFor","outputs":[{"internalType":"uint256","name":"percentVested_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"policy","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"principle","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pullManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner_","type":"address"}],"name":"pushManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_token","type":"address"}],"name":"recoverLostToken","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_recipient","type":"address"},{"internalType":"bool","name":"_stake","type":"bool"}],"name":"redeem","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_addition","type":"bool"},{"internalType":"uint256","name":"_increment","type":"uint256"},{"internalType":"uint256","name":"_target","type":"uint256"},{"internalType":"uint256","name":"_buffer","type":"uint256"}],"name":"setAdjustment","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"enum KlimaBondDepository.PARAMETER","name":"_parameter","type":"uint8"},{"internalType":"uint256","name":"_input","type":"uint256"}],"name":"setBondTerms","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_staking","type":"address"},{"internalType":"bool","name":"_helper","type":"bool"}],"name":"setStaking","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"staking","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"stakingHelper","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"standardizedDebtRatio","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"terms","outputs":[{"internalType":"uint256","name":"controlVariable","type":"uint256"},{"internalType":"uint256","name":"vestingTerm","type":"uint256"},{"internalType":"uint256","name":"minimumPrice","type":"uint256"},{"internalType":"uint256","name":"maxPayout","type":"uint256"},{"internalType":"uint256","name":"fee","type":"uint256"},{"internalType":"uint256","name":"maxDebt","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalDebt","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"treasury","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"useHelper","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"}]')  # noqa: E501
            bond = web3.eth.contract(address=address, abi=abi)

            #bonds are priced in BCTs despide the function is called bondPriceInUSD
            print('Bonds:')
            BondPriceUSD = bond.functions.bondPriceInUSD().call()/1e18
            MaxCap = float(payoutTokenPrice) * bond.functions.maxPayout().call()/1e9
            Disc = (decimal.Decimal(payoutTokenPrice) - decimal.Decimal(BondPriceUSD)) / decimal.Decimal(payoutTokenPrice)
            print(f' BondPrice: {BondPriceUSD}BCT')
            print(f' Discount: {100 * Disc:,.2f} %')
            return(payoutTokenPrice, Disc, MaxCap)

        except Exception as e:
            print(e)


def maxDebtReached(bond_address):
    try:
        abi = json.loads('[{"inputs":[{"internalType":"address","name":"_KLIMA","type":"address"},{"internalType":"address","name":"_principle","type":"address"},{"internalType":"address","name":"_treasury","type":"address"},{"internalType":"address","name":"_DAO","type":"address"},{"internalType":"address","name":"_bondCalculator","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"deposit","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"payout","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"expires","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"priceInUSD","type":"uint256"}],"name":"BondCreated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"priceInUSD","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"internalPrice","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"debtRatio","type":"uint256"}],"name":"BondPriceChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"recipient","type":"address"},{"indexed":false,"internalType":"uint256","name":"payout","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"remaining","type":"uint256"}],"name":"BondRedeemed","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"initialBCV","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newBCV","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"adjustment","type":"uint256"},{"indexed":false,"internalType":"bool","name":"addition","type":"bool"}],"name":"ControlVariableAdjustment","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPulled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipPushed","type":"event"},{"inputs":[],"name":"DAO","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"KLIMA","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"adjustment","outputs":[{"internalType":"bool","name":"add","type":"bool"},{"internalType":"uint256","name":"rate","type":"uint256"},{"internalType":"uint256","name":"target","type":"uint256"},{"internalType":"uint256","name":"buffer","type":"uint256"},{"internalType":"uint256","name":"lastBlock","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bondCalculator","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"bondInfo","outputs":[{"internalType":"uint256","name":"payout","type":"uint256"},{"internalType":"uint256","name":"vesting","type":"uint256"},{"internalType":"uint256","name":"lastBlock","type":"uint256"},{"internalType":"uint256","name":"pricePaid","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bondPrice","outputs":[{"internalType":"uint256","name":"price_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bondPriceInUSD","outputs":[{"internalType":"uint256","name":"price_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"currentDebt","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"debtDecay","outputs":[{"internalType":"uint256","name":"decay_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"debtRatio","outputs":[{"internalType":"uint256","name":"debtRatio_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint256","name":"_maxPrice","type":"uint256"},{"internalType":"address","name":"_depositor","type":"address"}],"name":"deposit","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_controlVariable","type":"uint256"},{"internalType":"uint256","name":"_vestingTerm","type":"uint256"},{"internalType":"uint256","name":"_minimumPrice","type":"uint256"},{"internalType":"uint256","name":"_maxPayout","type":"uint256"},{"internalType":"uint256","name":"_fee","type":"uint256"},{"internalType":"uint256","name":"_maxDebt","type":"uint256"},{"internalType":"uint256","name":"_initialDebt","type":"uint256"}],"name":"initializeBondTerms","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"isLiquidityBond","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastDecay","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxPayout","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_value","type":"uint256"}],"name":"payoutFor","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_depositor","type":"address"}],"name":"pendingPayoutFor","outputs":[{"internalType":"uint256","name":"pendingPayout_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_depositor","type":"address"}],"name":"percentVestedFor","outputs":[{"internalType":"uint256","name":"percentVested_","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"policy","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"principle","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pullManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner_","type":"address"}],"name":"pushManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_token","type":"address"}],"name":"recoverLostToken","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_recipient","type":"address"},{"internalType":"bool","name":"_stake","type":"bool"}],"name":"redeem","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceManagement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_addition","type":"bool"},{"internalType":"uint256","name":"_increment","type":"uint256"},{"internalType":"uint256","name":"_target","type":"uint256"},{"internalType":"uint256","name":"_buffer","type":"uint256"}],"name":"setAdjustment","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"enum KlimaBondDepository.PARAMETER","name":"_parameter","type":"uint8"},{"internalType":"uint256","name":"_input","type":"uint256"}],"name":"setBondTerms","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_staking","type":"address"},{"internalType":"bool","name":"_helper","type":"bool"}],"name":"setStaking","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"staking","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"stakingHelper","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"standardizedDebtRatio","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"terms","outputs":[{"internalType":"uint256","name":"controlVariable","type":"uint256"},{"internalType":"uint256","name":"vestingTerm","type":"uint256"},{"internalType":"uint256","name":"minimumPrice","type":"uint256"},{"internalType":"uint256","name":"maxPayout","type":"uint256"},{"internalType":"uint256","name":"fee","type":"uint256"},{"internalType":"uint256","name":"maxDebt","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalDebt","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"treasury","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"useHelper","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"}]')  # noqa: E501
        bond = web3.eth.contract(address=bond_address, abi=abi)
        currentDebt = bond.functions.currentDebt().call()
        maxDebt = bond.functions.terms().call()
        if currentDebt >= maxDebt[-1]:
            return(True)
        else:
            return(False)

    except Exception as e:
        print(e)


def check_is_worth(stakingRewards, rebase, bondDiscount):
    if stakingRewards >= bondDiscount + decimal.Decimal(((1+rebase))*(1-(1+rebase)**15)/(1-(1+rebase)))/15 - 1:
        return(':no_entry:', bondDiscount + decimal.Decimal(((1+rebase))*(1-(1+rebase)**15)/(1-(1+rebase)))/15 - 1)
    else:
        return(':white_check_mark:', bondDiscount + decimal.Decimal(((1+rebase))*(1-(1+rebase)**15)/(1-(1+rebase)))/15 - 1)


def get_prices():
    global last_call
    global klimaPriceUSD, bctPriceUSD, rebase, stakingRewards, bctClosed, bctPrice, bctDisc, bctMax, bctUsdClosed, bctUsdPrice, bctUsdDisc, bctUsdMax, klimaBctClosed, klimaBctPrice, klimaBctDisc, klimaBctMax  # noqa: E501

    if datetime.datetime.now() - datetime.timedelta(seconds=90) >= last_call:
        #retrieve prices
        print('here')
        bctPriceUSD = lp_base_token_price(lp_address='0x1e67124681b402064cd0abe8ed1b5c79d2e02f64')
        klimaPriceUSD = lp_base_token_price(lp_address='0x9803c7ae526049210a1725f7487af26fe2c24614', basePrice=bctPriceUSD)
        klimaBctPrice = lp_price(lp_address='0x9803c7aE526049210a1725F7487AF26fE2c24614')
        bctUsdPrice = lp_price(lp_address='0x1E67124681b402064CD0ABE8ed1B5c79D2e02f64')
        last_call = datetime.datetime.now()
    klimaPriceBCT = klimaPriceUSD/bctPriceUSD

    #Staking rewards
    rebase, stakingRewards = staking_rewards()

    #BCT
    bctClosed = maxDebtReached(bond_address='0x7De627C56D26529145a5f9D85948ecBeAF9a4b34')
    bctPrice, bctDisc, bctMax = contract_info(bond_address='0x7De627C56D26529145a5f9D85948ecBeAF9a4b34', payoutTokenPrice=klimaPriceBCT, maxReached=bctClosed)  # noqa: E501 

    #KLIMA-BCT
    klimaBctClosed = maxDebtReached(bond_address='0x1E0Dd93C81aC7Af2974cdB326c85B87Dd879389B')
    klimaBctPrice, klimaBctDisc, klimaBctMax = contract_info(bond_address='0x1E0Dd93C81aC7Af2974cdB326c85B87Dd879389B', payoutTokenPrice=klimaPriceBCT, maxReached=klimaBctClosed)  # noqa: E501

    #BCT-USDC
    bctUsdClosed = maxDebtReached(bond_address='0xBF2A35efcd85e790f02458Db4A3e2f29818521c5')
    bctUsdPrice, bctUsdDisc, bctUsdMax = contract_info(bond_address='0xBF2A35efcd85e790f02458Db4A3e2f29818521c5', payoutTokenPrice=klimaPriceBCT, maxReached=bctUsdClosed)  # noqa: E501

    return(klimaPriceUSD, rebase, stakingRewards, bctClosed, bctPrice, bctDisc, bctMax, bctUsdClosed, bctUsdPrice, bctUsdDisc, bctUsdMax, klimaBctClosed, klimaBctPrice, klimaBctDisc, klimaBctMax)  # noqa: E501


#create a class for the embed
class PageButton(discord.ui.Button):
    def __init__(self, current, pages):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Page {current+1}/{pages+1}", disabled=True, custom_id='page')

class Pagination(discord.ui.View):
    def __init__(self, paginationList):
        super().__init__(timeout=10)
        self.value = 0
        self.pages = len(paginationList)-1
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
            self.value -= 1
        for b in self.children:
            if b.custom_id=='page':
                self.remove_item(b)
                self.add_item(PageButton(current=self.value, pages=self.pages))
        await interaction.response.edit_message(embed=self.paginationList[self.value], view=self)

    @discord.ui.button(label="Next Page", style=discord.ButtonStyle.primary)
    async def prev_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.value + 1 > self.pages:
            self.value = 0
        else:
            self.value += 1
        for b in self.children:
            if b.custom_id=='page':
                self.remove_item(b)
                self.add_item(PageButton(current=self.value, pages=self.pages))
        await interaction.response.edit_message(embed=self.paginationList[self.value], view=self)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    if not check_discounts.is_running():
        check_discounts.start()


@tasks.loop(seconds = 30)
async def check_discounts():
    klimaPriceUSD, rebase, stakingRewards, bctClosed, bctPrice, bctDisc, bctMax, bctUsdClosed, bctUsdPrice, bctUsdDisc, bctUsdMax, klimaBctClosed, klimaBctPrice, klimaBctDisc, klimaBctMax = get_prices()  # noqa: E501

    #check if any alerts where triggered 
    urows = db.records("SELECT DISTINCT UserID FROM bond_alerts")
    if len(urows) > 0:
        for (user_id,) in urows:
            fields = []
            user_discount = False
            print(user_id)
            rows = db.records("SELECT DISTINCT Bond, Discount, Active FROM bond_alerts WHERE UserID = ?", int(user_id))
            for (bond, discount, is_active) in rows:
                    if bond == 'BCT':
                        if is_active == 0 and bctClosed == False and discount <= 100 * bctDisc:
                            user_discount = True
                            is_worth, maxBondDisc = check_is_worth(stakingRewards, rebase, bctDisc)  
                            fields = fields + [(f'Bond Type:', f' {bond}', True), ('Discount:', f' {100*bctDisc:,.2f}%', True), ('\u200b', '\u200b', True),
                            ('Could be profitable?:', is_worth, True), ('Compound Discount:', f' {100*maxBondDisc:,.2f}%', True), ("Max payout USD:", f'${bctMax:,.2f}', True)]  # noqa: E501
                            db.execute("UPDATE bond_alerts SET Active = 1 WHERE UserID = ? AND Bond = ? AND Discount = ?", user_id, bond, discount)
                            db.save()
                            print(f'Alert sent to {user_id} for {bond} at more than {discount}% discount')
                            print(fields)
                        elif is_active == 1 and discount > 100 * bctDisc:
                            db.execute("UPDATE bond_alerts SET Active = 0 WHERE UserID = ? AND Bond = ? AND Discount = ?", user_id, bond, discount)
                            db.save()
                            print(f'Alert reseted for {bond} at more than {discount}% discount')

                    if bond == 'KLIMA-BCT':
                        if is_active == 0 and klimaBctClosed == False and discount <= 100 * klimaBctDisc:
                            user_discount = True
                            is_worth, maxBondDisc = check_is_worth(stakingRewards, rebase, klimaBctDisc)  
                            fields = fields + [(f'Bond Type:', f' {bond}', True), ('Discount:', f' {100*klimaBctDisc:,.2f}%', True), ('\u200b', '\u200b', True),
                            ('Could be profitable?:', is_worth, True), ('Compound Discount:', f' {100*maxBondDisc:,.2f}%', True), ("Max payout USD:", f'${klimaBctMax:,.2f}', True)]  # noqa: E501
                            db.execute("UPDATE bond_alerts SET Active = 1 WHERE UserID = ? AND Bond = ? AND Discount = ?", user_id, bond, discount)
                            db.save()
                            print(f'Alert sent to {user_id} for {bond} at more than {discount}% discount')
                            print(fields)
                        elif is_active == 1 and discount > 100 * klimaBctDisc:
                            db.execute("UPDATE bond_alerts SET Active = 0 WHERE UserID = ? AND Bond = ? AND Discount = ?", user_id, bond, discount)
                            db.save()
                            print(f'Alert reseted for {bond} at more than {discount}% discount')

                    elif bond == 'BCT-USDC':
                        if is_active == 0 and bctUsdClosed == False and discount <= 100 * bctUsdDisc:
                            user_discount = True
                            is_worth, maxBondDisc = check_is_worth(stakingRewards, rebase, bctUsdDisc)  
                            fields = fields + [(f'Bond Type:', f' {bond}', True), ('Discount:', f' {100*bctUsdDisc:,.2f}%', True), ('\u200b', '\u200b', True),
                            ('Could be profitable?:', is_worth, True), ('Compound Discount:', f' {100*maxBondDisc:,.2f}%', True),  ("Max payout USD:", f'${bctUsdMax:,.2f}', True)]  # noqa: E501
                            db.execute("UPDATE bond_alerts SET Active = 1 WHERE UserID = ? AND Bond = ? AND Discount = ?", user_id, bond, discount)
                            db.save()
                            print(f'Alert sent to {user_id} for {bond} at more than {discount}% discount')
                            print(fields)
                        elif is_active == 1 and discount > 100 * bctUsdDisc:
                            db.execute("UPDATE bond_alerts SET Active = 0 WHERE UserID = ? AND Bond = ? AND Discount = ?", user_id, bond, discount)
                            db.save()
                            print(f'Alert reseted for {bond} at more than {discount}% discount')

            if user_discount == True:
                embed = discord.Embed(title = f'Big Bond Discount!', description = f':small_blue_diamond: 5 day ROI for **staking** sits at **{100 * stakingRewards:,.2f}%** \n :small_blue_diamond: Current **KLIMA** price is **${klimaPriceUSD:,.2f}** \n :small_blue_diamond: Some of your alert thresholds have been reached by current bond discounts', colour=0x17d988)  # noqa: E501
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                user = client.get_user(user_id)
                embed.set_footer(text = 'This alert is courtesy of your klimate @0xRusowsky')
                await user.send(embed=embed)
            else:
                print('No alerts to report')
                pass


@client.slash_command(description="Check live information for every bond type issued by KlimaDAO.") #, guild_ids=[864398537403400242])
async def bonds(ctx):
    global klimaPriceUSD, rebase, stakingRewards, bctClosed, bctPrice, bctDisc, bctMax, bctUsdClosed, bctUsdPrice, bctUsdDisc, bctUsdMax, klimaBctClosed, klimaBctPrice, klimaBctDisc, klimaBctMax  # noqa: E501

    await ctx.defer(ephemeral=True)
    info =  sorted(
            [('BCT', check_is_worth(stakingRewards, rebase, bctDisc), 100*bctDisc, bctMax, bctClosed)
            ,('KLIMA-BCT', check_is_worth(stakingRewards, rebase, klimaBctDisc), 100*klimaBctDisc, klimaBctMax, klimaBctClosed)
            ,('BCT-USDC', check_is_worth(stakingRewards, rebase, bctUsdDisc), 100*bctUsdDisc, bctUsdMax, bctUsdClosed)
            ], key=lambda x: x[2], reverse=True)

    fields = []
    for i in info:
        if i[4] == False:
            fields = fields + [(('Bond Type:',i[0]), ('Discount:',f'{i[2]:,.2f}%'), ('Could be profitable?:', i[1][0]), ('Compound Discount:', f' {100*i[1][1]:,.2f}%'), ('Max payout USD:',f'${i[3]:,.2f}'))]  # noqa: E501
        else:
            fields = fields + [(('Bond Type:',i[0]), ('Sold Out  :no_entry:',"Max Debt Reached"))]

    lfields = [fields[i * 4:(i + 1) * 4] for i in range((len(fields) + 4 - 1) // 4 )]
    paginationList = []
    page = 0
    for lf in lfields:
        page = page + 1
        embed = discord.Embed(title = "Current KlimaDAO Bond Discounts", description = f":small_blue_diamond: 5 day ROI for **staking** sits at **{100 * stakingRewards:,.2f}%** \n :small_blue_diamond: Current **KLIMA** price is **${klimaPriceUSD:,.2f}**", colour=0xFFFFFF)  # noqa: E501
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
                embed.add_field(name=f[1][0], value=f[1][1], inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=True)
        paginationList.append(embed)

    if len(paginationList) == 1:
        await ctx.followup.send(embed=paginationList[0])
    else:
        view = Pagination(paginationList=paginationList)
        await ctx.respond(embed=paginationList[view.value], view=view)
        view.message = await ctx.interaction.original_message()


@client.slash_command(description="Check the available bond types that KlimaDAO offers and that this bot supports.") #, guild_ids=[864398537403400242])
async def info_bonds(ctx):
    if not check_discounts.is_running():
        check_discounts.start()

    bonds = [('BCT', f'[Link](https://polygonscan.com/address/0x7De627C56D26529145a5f9D85948ecBeAF9a4b34)'), ('KLIMA-BCT', f'[Link](https://polygonscan.com/address/0x1E0Dd93C81aC7Af2974cdB326c85B87Dd879389B)'), ('BCT-USDC', f'[Link](https://polygonscan.com/address/0xBF2A35efcd85e790f02458Db4A3e2f29818521c5)')]  # noqa: E501
    fields = []
    b = 0
    for b in bonds:
        fields += [('Bond Type:', b[0], True), ('\u200b', '\u200b', True), ('Contract:', b[1], True)]

    embed = discord.Embed(title = "KlimaDAO Bond Types", description = f"KlimaDAO currently offers {len(bonds)} bond types.", colour=0xFFFFFF)
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    await ctx.respond(embed=embed)


@client.slash_command(description='Create alerts that will be triggered according to bond discount.') #, guild_ids=[864398537403400242])
async def create_alert(ctx,
    bond_type: Option(str, "Input the desired bond (use the /info_bonds command to see all the bond types)."),
    min_discount: Option(float, "Input the min_discount threshold (must be a number, without '%' sign)."),
):
    bond_list = ['BCT', 'KLIMA-BCT', 'BCT-USDC']
    bond_str = ""
    for b in bond_list:
        bond_str += " \n :black_small_square: "+ b
    bond = bond_type.upper()

    if bond not in bond_list:
        embed = discord.Embed(title = "Configuration Error", description = f"Incorrect bond type: **{bond}**. \n  The input value for a bond must be within the following: **{bond_str}** ", colour=0xd14d4d)  # noqa: E501
        await ctx.respond(embed=embed)
    else:
        alert_id = db.record("SELECT AlertID FROM bond_alerts WHERE UserID = ? AND Bond = ? AND Discount=?", ctx.author.id, bond, min_discount)
        if alert_id is None:
            if len(db.records("SELECT * FROM bond_alerts WHERE UserID = ?", ctx.author.id)) == 5:
                embed = discord.Embed(title = "Configuration Error", description = f"{ctx.author.mention} already had 5 alerts configured. Don't be greedy ser!", colour=0xd14d4d)
                await ctx.respond(embed=embed)
            else:
                db.execute("INSERT INTO bond_alerts VALUES (?,?,?,?,0)", str(ctx.author.id) + bond + str(min_discount), ctx.author.id, bond, min_discount)
                db.save()
                embed = discord.Embed(title = "New Bond Alert Configured", description = f'{ctx.author.mention} has created a new alert for discounts over {min_discount}% on {bond} bonds!', colour=0x17d988)  # noqa: E501
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title = "Bond Alert Already Configured", description = f'{ctx.author.mention} already had an alert for discounts over {min_discount}% on {bond} bonds.', colour=0xd14d4d)  # noqa: E501
            await ctx.respond(embed=embed)


@client.slash_command(description='Delete an existing bond alert') #, guild_ids=[864398537403400242])
async def delete_alert(ctx,
    bond_type: Option(str, "Input the desired bond (use the /info_bonds command to see all the bond types)."),
    min_discount: Option(float, "Input the min_discount threshold (must be a number, without '%' sign)."),
):
    bond = bond_type.upper()
    alert_id = db.record("SELECT AlertID FROM bond_alerts WHERE UserID = ? AND Bond = ? AND Discount=?", ctx.author.id, bond, min_discount)
    print(alert_id)
    if alert_id is not None:
        db.execute("DELETE FROM bond_alerts WHERE AlertID = ?", str(ctx.author.id) + bond + str(min_discount))
        db.save()
        embed = discord.Embed(title = "Bond Alert Deleted", description = f'{ctx.author.mention} has deleted an alert for discounts over {min_discount}% on {bond} bonds!', colour=0x17d988)  # noqa: E501
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title = "Alert Doesn't Exist", description = f'{ctx.author.mention} does not have any alerts for discounts over {min_discount}% on {bond} bonds.', colour=0xFFFFFF)  # noqa: E501
        await ctx.respond(embed=embed)


@client.slash_command(description='Delete all the previously configured bond alerts.') #, guild_ids=[864398537403400242])
async def delete_all(ctx):
    alert_id = db.record("SELECT AlertID FROM bond_alerts WHERE UserID = ?", ctx.author.id)
    print(alert_id)
    if alert_id is not None:
        db.execute("DELETE FROM bond_alerts WHERE UserID = ?", ctx.author.id)
        db.save()
        embed = discord.Embed(title = "All Bond Alerts Deleted", description = f'{ctx.author.mention} has deleted all bond alerts!', colour=0x17d988)  # noqa: E501
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title = "No Alerts Configured", description = f'{ctx.author.mention} does not have any configured alerts.', colour=0xFFFFFF)  # noqa: E501
        await ctx.respond(embed=embed)


@client.slash_command(description='Check all the already existing alerts.') #, guild_ids=[864398537403400242])
async def my_alerts(ctx):
    alert_id = db.record("SELECT AlertID FROM bond_alerts WHERE UserID = ?", ctx.author.id)
    print(alert_id)
    if alert_id is None:
        embed = discord.Embed(title = "No Alerts", description = f'{ctx.author.mention} has not configured any alerts yet. \n To create new alerts use the  **/create_alert**  command and follow the instructions.', colour=0xFFFFFF)  # noqa: E501
        await ctx.respond(embed=embed)
    else:
        rows = db.records("SELECT Bond, Discount FROM bond_alerts WHERE UserID = ?", ctx.author.id)
        embed = discord.Embed(title = f'Configured Alerts for {ctx.author}', description='You will receive an alert when a bond discount matches any the following criteria.', colour=0xFFFFFF)  # noqa: E501
        for (bond, discount) in rows:
            embed.add_field(name=f'Bond Type:', value=f'{bond}', inline=True)
            embed.add_field(name=f'Discount:', value=f'{discount}%', inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=True)

        await ctx.respond(embed=embed)


@client.slash_command(description="Check all the commands and a brief explanation on how to use them.") #, guild_ids=[864398537403400242])
async def help_bonds(ctx):
    embed = discord.Embed(title = f'Help Panel', description='Here you can see a list with all the KlimaDAO Alerts commands and a brief explanation on how to use them.', colour=0xFFFFFF)  # noqa: E501
    embed.add_field(name=f':small_blue_diamond: /info_bonds', value='Returns a list with the names of the partners, the bond types and the payout tokens that KlimaDAO offers.', inline=False)  # noqa: E501
    embed.add_field(name=f':small_blue_diamond: /bonds', value='Returns all the live information for every bond type issues by KlimaDAO.', inline=False)  # noqa: E501
    embed.add_field(name=f':small_blue_diamond: /my_alerts', value='Returns a list with all the alerts that the user has.', inline=False)  # noqa: E501
    embed.add_field(name=f':small_orange_diamond: /create_alert', value='Creates a new alert that will be triggered when bond discounts are greater than *min_discount*. \n :black_small_square: **bond_type:**  must belong to the ones listed under  **/info_bonds**  \n :black_small_square: **min_discount:**  XX.XX (number expressed in %)', inline=False)  # noqa: E501
    embed.add_field(name=f':small_orange_diamond: /delete_all', value='Deletes all the alerts that the user previously configured.', inline=False)  # noqa: E501
    embed.add_field(name=f':small_orange_diamond: /delete_alert', value='Deletes an existing bond alert. \n :black_small_square: **bond_type:**  must belong to  the ones listed under  **/info_bonds** \n :black_small_square: **min_discount:**  XX.XX (number expressed in %) \n ', inline=False)  # noqa: E501

    embed.set_footer(text = 'If you have any ideas or improvement suggestions please DM your klimate @0xRusowsky')
    await ctx.respond(embed=embed)


client.run(BOT_TOKEN)