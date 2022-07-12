from algosdk.future.transaction import ApplicationNoOpTxn
from utils import txn
from MFLogicSig import sig


def mint(sender, asset1, asset2, asset1_amt, asset2_amt, algod_client,
        fee_tier=1, params=None, lp_id=None, pool_addr=None, 
        slippage=1, end_receiver=None, testnet=False):

    # Both tesnet and mainnet ids will change
    if testnet: 
        app_id = 98952143 
        community_token = 123456
    else: 
        app_id = 98952143
        community_token = 123456 

    if not pool_addr:
        pool_addr = sig(asset1, asset2, fee_tier, algod_client)

    # figure out how to get lp_id    
    if not lp_id:
        lp_id = 0
    
    if not end_receiver:
        end_receiver = sender
    
    if not params:
        params = algod_client.suggested_params()

    slippage = int(asset1_amt*(1-slippage/100))
    foreign_assets = [asset1, asset2, lp_id, community_token]

    txn_1 = txn(asset1, asset1_amt, sender, pool_addr, params)
    txn_2 = txn(asset2, asset2_amt, sender, pool_addr, params)

    call = ApplicationNoOpTxn(
        sender=sender,
        index=app_id,
        app_args=['mint', slippage], # how does slippage work on the call?
        foreign_assets=foreign_assets,
        accounts=[end_receiver, pool_addr],
        sp=params
    )
    call.fee = 4000 # may be 1000 too high

    return [txn_1, txn_2, call]