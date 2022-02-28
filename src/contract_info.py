from .utils import load_abi

uni_v2_abi = load_abi('uni_v2_pool.json')


def uni_v2_pool_price(web3, pool_address, decimals, basePrice=1):
    '''
    Calculate the price of a SushiSwap liquidity pool, using the provided
    pool address, decimals of the first token, and multiplied by
    basePrice if provided for computing multiple pool hops.
    '''
    pool_contract = web3.eth.contract(
        address=pool_address,
        abi=uni_v2_abi
    )

    try:
        reserves = pool_contract.functions.getReserves().call()
        token_price = reserves[0] * basePrice * 10**decimals / reserves[1]

        return token_price
    except Exception:
        return None


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
