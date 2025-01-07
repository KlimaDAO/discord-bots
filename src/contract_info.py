from .aerodrome_price import AerodromePrice
from .utils import load_abi
from .constants import KLIMA_USDC_POOL, USDC_DECIMALS, BASE_USDC_DECIMALS, KLIMA_DECIMALS, \
                       KLIMA_BASE_ADDRESS, USDC_BASE_ADDRESS, \
                       AERO_KLIMA_WETH_POOL_ADDRESS, AERO_WETH_USDC_POOL_ADDRESS

uni_v2_abi = load_abi('uni_v2_pool.json')
uni_v3_abi = load_abi('uni_v3_pool.json')


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


def uni_v3_pool_price(web3, pool_address, decimals0=18, decimals1=18, base_price=1):
    '''
    Calculate the price of a UniV3 liquidity pool, using the provided
    pool address, decimals of the first token, and multiplied by
    base_price if provided for computing multiple pool hops.
    '''
    pool_contract = web3.eth.contract(
        address=pool_address,
        abi=uni_v3_abi
    )

    try:
        # Get slot0 data
        slot0_data = pool_contract.functions.slot0().call()
        sqrt_price_x96 = slot0_data[0]

        # Calculate price from sqrtPriceX96
        # Price = (sqrtPriceX96 / 2^96) ^ 2
        price_1_0 = (sqrt_price_x96 / (2**96)) ** 2

        # Adjust for decimals
        token_price = price_1_0 * (10 ** decimals0) / (10 ** decimals1)

        return token_price * base_price

    except Exception as e:
        print(e)
        return None


def klima_usdc_price(web3):
    return uni_v2_pool_price(
        web3, KLIMA_USDC_POOL,
        USDC_DECIMALS - KLIMA_DECIMALS
    )


def aero_weth_usdc_price():
    # Initialize with Base RPC URL
    aero_price = AerodromePrice()

    return aero_price.get_spot_price(
        USDC_BASE_ADDRESS,
        AERO_WETH_USDC_POOL_ADDRESS,
        token_in_decimals=BASE_USDC_DECIMALS
    )


def aero_klima_usdc_price(web3):
    # Initialize with Base RPC URL
    aero_price = AerodromePrice()

    klima_weth_price = aero_price.get_spot_price(
        KLIMA_BASE_ADDRESS,
        AERO_KLIMA_WETH_POOL_ADDRESS,
        token_in_decimals=KLIMA_DECIMALS
    )
    weth_usdc_price = aero_price.get_spot_price(
        USDC_BASE_ADDRESS,
        AERO_WETH_USDC_POOL_ADDRESS,
        token_in_decimals=BASE_USDC_DECIMALS
    )

    return klima_weth_price / weth_usdc_price


def token_supply(web3, token_address, abi, decimals=None):
    '''
    Compute the total supply of the specified ERC-20 token at `token_address` with `abi` and the correct `decimals`
    '''
    contract = web3.eth.contract(
        address=token_address,
        abi=abi
    )

    try:
        if decimals is None:
            decimals = contract.functions.decimals().call()
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
