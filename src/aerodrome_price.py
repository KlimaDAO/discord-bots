from decimal import Decimal

from .utils import get_base_web3, load_abi


POOL_ABI = load_abi('aero_pool.json')


class AerodromePrice:
    def __init__(self):
        self.w3 = get_base_web3()

    def get_spot_price(
        self,
        token_in,
        pool_address,
        token_in_decimals: int = 18,
        token_out_decimals: int = 18
    ) -> float:
        """
        Query the spot price for a token pair on Aerodrome

        Args:
            token_in: Address of input token
            pool_address: Address of pool
            token_in_decimals: Decimals of input token
            token_out_decimals: Decimals of output token

        Returns:
            Spot price of token_out in terms of token_in
        """
        try:
            # Create pool contract instance
            pool = self.w3.eth.contract(
                address=pool_address,
                abi=POOL_ABI
            )

            # Use 1 unit of token_in for spot price
            amount_in = 10 ** token_in_decimals

            # Get amount out
            amount_out = pool.functions.getAmountOut(
                amount_in,
                token_in
            ).call()

            # Calculate spot price
            spot_price = (
                Decimal(amount_out) / Decimal(10 ** token_out_decimals)
            )

            return float(spot_price)

        except Exception as e:
            raise Exception(f"Error querying Aerodrome spot price: {str(e)}")
