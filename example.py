from algosdk import mnemonic
from algosdk.v2client import algod
from client import MidaClient
from utils import txn


algod_token = "" # your purestake token (more needs to be changed for other connections)
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_headers = { "X-API-Key": algod_token }
algod_client = algod.AlgodClient(algod_token, algod_address, algod_headers)

mnemonic_phrase = "" # a testnet funded account
account_private_key = mnemonic.to_private_key(mnemonic_phrase)
account_public_key = mnemonic.to_public_key(mnemonic_phrase)

asset1 = 0 # currently is algos, can be set to any asset
asset2 = -1 # change this to an asset you have in your wallet

midafi_client = MidaClient(algod_client, account_public_key, account_private_key, 'test')

# first create a pool
my_new_pool = midafi_client.create(asset1, asset2, fee_tier=1)
print("New pool address: ", my_new_pool)

# retrieve the lp token id from the new pool
lp_id = midafi_client.get_lp_id(my_new_pool)
print("New lp token id: ", lp_id)

# opt in to the LP token
optin = txn(lp_id, 0, midafi_client.addr, midafi_client.addr, midafi_client.algod.suggested_params())

# create a transaction to mint to the pool
asset1_mint_amt = 11000000 # set to 11 algos
asset2_mint_amt = 11000000 # this may need to change based on the number of this asset held
m = midafi_client.mint(asset1, asset2, asset1_mint_amt, asset2_mint_amt, pool=my_new_pool, lp_id=lp_id)

# create a transaction to swap against the pool asset1 -> asset2
asset1_swap_amt = 100000
s = midafi_client.swap(asset1, asset2, asset1_swap_amt, pool=my_new_pool, lp_id=lp_id, slippage=100)

# create a transaction to burn some of the minted LP tokens
lp_burn_amt = 500000
b = midafi_client.burn(lp_id, lp_burn_amt, asset1, asset2, pool=my_new_pool)

# create one list of transactions
gtxn = [optin] + m + s + b

# send the transaction and wait for it to get confirmed
tx_id = midafi_client.send_group(gtxn)
print("Successful transaction with id: ", tx_id)