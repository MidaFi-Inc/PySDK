from algosdk.future.transaction import ApplicationNoOpTxn
from utils import txn
from MFLogicSig import sig

def burn(sender, lp_id, lp_amt, asset1, asset2, min_asset1, min_asset2, pool_addr, end_receiver, app_id, params):

    if app_id == 98952143: 
        community_token = 123456
    else:
        community_token = 123456

    foreign_assets = [asset1, asset2, lp_id, community_token]

    txn_1 = txn(lp_id, lp_amt, sender, pool_addr, params)

    call = ApplicationNoOpTxn(
        sender=sender,
        index=app_id,
        app_args=['burn', min_asset1, min_asset2],
        accounts=[end_receiver, pool_addr],
        foreign_assets=foreign_assets,
        sp=params
    )
    call.fee = 3000
    return [txn_1, call]