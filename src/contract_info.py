from .utils import load_abi
from .constants import KLIMA_USDC_POOL, USDC_DECIMALS, KLIMA_DECIMALS

uni_v2_abi = load_abi('uni_v2_pool.json')


def uni_v2_pool_price(web3, pool_address, decimals, base_price=1):
    '''
    Calculate the price of a SushiSwap liquidity pool, using the provided
    pool address, decimals of the first token, and multiplied by
    base_price if provided for computing multiple pool hops.
    '''
    pool_contract = web3.eth.contract(
        address=pool_address,
        abi=uni_v2_abi
    )

    try:
        reserves = pool_contract.functions.getReserves().call()
        token_price = reserves[0] * base_price * 10**decimals / reserves[1]

        return token_price
    except Exception:
        return None


def klima_usdc_price(web3):
    return uni_v2_pool_price(
        web3, KLIMA_USDC_POOL,
        USDC_DECIMALS - KLIMA_DECIMALS
    )


def token_supply(web3, token_address, abi, decimals):
    '''
    Compute the total supply of the specified ERC-20 token at `token_address` with `abi` and the correct `decimals`
    '''
    contract = web3.eth.contract(
        address=token_address,
        abi=abi
    )

    try:
        total_supply = contract.functions.totalSupply().call() / 10**decimals
        return total_supply
    except Exception:
        return None


def balance_of(web3, token_address, abi, decimals, address_to_check):
    '''
    Compute the balance for specific `address_to_check` 
    of the specified ERC-20 token at `token_address` 
    with `abi` and the correct `decimals`
    '''
    contract = web3.eth.contract(
        address=token_address,
        abi=abi
    )

    try:
        balance = contract.functions.balanceOf(
            address_to_check).call() / 10**decimals
        return balance
    except Exception:
        return None
