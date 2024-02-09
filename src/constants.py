from web3 import Web3

# Hard-coded since Polygon block times have stabilized
AVG_BLOCK_SECS = 2.21

# Token Decimals
BCT_DECIMALS = 18
C3_DECIMALS = 18
FRAX_DECIMALS = 18
KLIMA_DECIMALS = 9
MCO2_DECIMALS = 18
MOSS_DECIMALS = 18
NBO_DECIMALS = 18
UBO_DECIMALS = 18
NCT_DECIMALS = 18
USDC_DECIMALS = 12

# Token Addresses
BCT_ADDRESS = Web3.to_checksum_address('0x2f800db0fdb5223b3c3f354886d907a671414a7f')
C3_ADDRESS = Web3.to_checksum_address('0xad01DFfe604CDc172D8237566eE3a3ab6524d4C6')
FRAX_ADDRESS = Web3.to_checksum_address('0x45c32fA6DF82ead1e2EF74d17b76547EDdFaFF89')
KLIMA_ADDRESS = Web3.to_checksum_address('0x4e78011Ce80ee02d2c3e649Fb657E45898257815')
MCO2_ADDRESS = Web3.to_checksum_address('0xfc98e825a2264d890f9a1e68ed50e1526abccacd')
MOSS_ADDRESS = Web3.to_checksum_address('0x03e3369af9390493cb7cc599cd5233d50e674da4')
NBO_ADDRESS = Web3.to_checksum_address('0x6BCa3B77C1909Ce1a4Ba1A20d1103bDe8d222E48')
NCT_ADDRESS = Web3.to_checksum_address('0xD838290e877E0188a4A44700463419ED96c16107')
UBO_ADDRESS = Web3.to_checksum_address('0x2B3eCb0991AF0498ECE9135bcD04013d7993110c')
USDC_ADDRESS = Web3.to_checksum_address('0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')
CCO2_ADDRESS = Web3.to_checksum_address('0x82B37070e43C1BA0EA9e2283285b674eF7f1D4E2')

# LP Pool Addresses
BCT_KLIMA_POOL = Web3.to_checksum_address('0x9803c7ae526049210a1725f7487af26fe2c24614')
FRAX_C3_POOL = Web3.to_checksum_address('0xb5600746f947c25c0cbc36429f87e6c88f9d6a88')
KLIMA_MCO2_POOL = Web3.to_checksum_address('0x64a3b8ca5a7e406a78e660ae10c7563d9153a739')
KLIMA_NBO_POOL = Web3.to_checksum_address('0x251cA6A70cbd93Ccd7039B6b708D4cb9683c266C')
KLIMA_USDC_POOL = Web3.to_checksum_address('0x5786b267d35F9D011c4750e0B0bA584E1fDbeAD1')
MOSS_USDC_POOL = Web3.to_checksum_address('0x75a7360e330c338007CF482e2CDf0A06573763A1')
UBO_KLIMA_POOL = Web3.to_checksum_address('0x5400A05B8B45EaF9105315B4F2e31F806AB706dE')
USDC_NCT_POOL = Web3.to_checksum_address('0xdb995f975f1bfc3b2157495c47e4efb31196b2ca')
KLIMA_CCO2_POOL = Web3.to_checksum_address('0x4D2263FF85e334C1f1d04C6262F6c2580335a93C')

# Klima Protocol Contracts
STAKING_ADDRESS = Web3.to_checksum_address('0x25d28a24Ceb6F81015bB0b2007D795ACAc411b4d')
DISTRIBUTOR_ADDRESS = Web3.to_checksum_address('0x4cC7584C3f8FAABf734374ef129dF17c3517e9cB')
SKLIMA_ADDRESS = Web3.to_checksum_address('0xb0C22d8D350C67420f06F48936654f567C73E8C8')
DAO_WALLET_ADDRESS = Web3.to_checksum_address('0x65a5076c0ba74e5f3e069995dc3dab9d197d995c')

# Subgraphs
KLIMA_PROTOCOL_SUBGRAPH = 'https://api.thegraph.com/subgraphs/name/klimadao/klimadao-protocol-metrics'
KLIMA_CARBON_SUBGRAPH = 'https://api.thegraph.com/subgraphs/name/klimadao/polygon-bridged-carbon'
KLIMA_BONDS_SUBGRAPH = 'https://api.thegraph.com/subgraphs/name/klimadao/klimadao-bonds'
POLYGON_DIGITAL_CARBON_SUBGRAPH = 'https://api.thegraph.com/subgraphs/name/klimadao/polygon-digital-carbon'
