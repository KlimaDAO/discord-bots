import os

from PIL import Image
import qrcode
from web3.auto.infura import w3

from contracts import AKLIMA_CONTRACT_ADDR, ERC20_ABI

STICKER_PATHS = {
    'carbonguzzler': 'carbonguzzler.png',
    'virginchad': 'virginchad.png'
}
STICKER_PATHS = {
    k: os.path.join(os.getcwd(), 'Documents/Code/klimadao/discord_bots/assets', v)
    for k, v in STICKER_PATHS.items()
}

STICKER_OFFSETS = {
    'carbonguzzler': [2150, 200],
    'virginchad': [735, 110]
}

STICKER_RESIZES = {
    'carbonguzzler': 0,
    'virginchad': 1/4
}


def assemble_url(location, address, desired_image):
    return f"https://klimadao.finance?utm_source=guerilla+qr&utm_medium={location}&utm_campaign={address}"


def make_qr_code(location, address, desired_image):
    '''
    Generate unique QR codes using each location and each user's address
    '''
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(assemble_url(location, address, desired_image))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img


def overlay_qr(qr, sticker_id, output_path):
    '''
    Overlay a generated QR code onto the provided sticker image
    '''
    # Convert images to RGBA format for compatibility
    qr = qr.convert("RGBA")

    sticker = Image.open(STICKER_PATHS[sticker_id])
    sticker.convert("RGBA")

    # Calculate placement box based on QR image size and specified offsets for each sticker
    qr_size = qr.size[0]
    x_offset, y_offset = STICKER_OFFSETS[sticker_id]

    # If resize_factor is non-zero, scale down QR code by multiplying size by factor
    resize_factor = STICKER_RESIZES[sticker_id]
    if resize_factor > 0:
        qr_size = int(qr_size * resize_factor)

        qr = qr.resize((qr_size, qr_size))

    box = (
        qr_size + x_offset, qr_size - y_offset,
        2 * qr_size + x_offset, 2 * qr_size - y_offset
    )

    # Resize the QR code and paste onto the image at the proper location
    qr.resize((box[2] - box[0], box[3] - box[1]))
    sticker.paste(qr, box)

    sticker.save(output_path)


def validate_address(address):
    '''
    Use web3 to validate that the provided address is:
    1. A valid ETH address
    2. Has non-zero `aKLIMA` balance

    Eventually, once the DApp launches on Polygon mainnet,
    we'll need to generalize this to check for either
    aKLIMA on ETH mainnet, or KLIMA or sKLIMA on Polygon

    https://web3py.readthedocs.io/en/stable/examples.html#query-account-balances
    '''

    if not w3.isAddress(address):
        return False

    aklima_contract = w3.eth.contract(w3.toChecksumAddress(AKLIMA_CONTRACT_ADDR), abi=ERC20_ABI)
    akl_balance = aklima_contract.functions.balanceOf(address).call()

    if akl_balance > 0:
        return True
    else:
        return False
