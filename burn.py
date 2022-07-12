from algosdk.future.transaction import ApplicationNoOpTxn
from utils import txn
from MFLogicSig import sig

def burn(sender, lp_id, lp_amt, algod_client,
        asset1=None, asset2=None, min_asset1=0, min_asset2=0,
        fee_tier=None, params=None, pool_addr=None, 
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

    # figure out how to get fee tier  
    if not fee_tier:
        fee_tier = 1
    
    if not end_receiver:
        end_receiver = sender
    
    if not params:
        params = algod_client.suggested_params()

    # slippage should be done better
    slippage1 = min_asset1
    slippage2 = min_asset2
    foreign_assets = [asset1, asset2, lp_id, community_token]

    txn_1 = txn(lp_id, lp_amt, sender, pool_addr, params)

    call = ApplicationNoOpTxn(
        sender=sender,
        index=app_id,
        app_args=['burn', slippage1, slippage2],
        accounts=[end_receiver, pool_addr],
        foreign_assets=foreign_assets,
        sp=params
    )
    call.fee = 3000
    return [txn_1, call]