from algosdk.future.transaction import ApplicationNoOpTxn
from utils import txn
from MFLogicSig import sig

def swap(sender, asset1, asset2, asset1_amt, algod_client, 
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
        if asset1 < asset2:
            pool_addr = sig(asset2, asset1, fee_tier, algod_client)
        else:
            pool_addr = sig(asset1, asset2, fee_tier, algod_client)

    # figure out how to get lp_id    
    if not lp_id:
        lp_id = 0
    
    if not end_receiver:
        end_receiver = sender
    
    if not params:
        params = algod_client.suggested_params()
    
    slippage = int(asset1_amt*(1-slippage/100)) # slippage is input as a parameter as a percent
    foreign_assets = [asset1, asset2, lp_id, community_token]

    txn_1 = txn(asset1, asset1_amt, sender, pool_addr, params)

    accts = [end_receiver, pool_addr]
    call = ApplicationNoOpTxn(
        sender=sender,
        index=app_id,
        app_args=['swap', slippage],
        foreign_assets=foreign_assets,
        accounts=accts,
        sp=params
    )
    call.fee = 2000
    return [txn_1, call]