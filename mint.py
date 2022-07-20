from algosdk.future.transaction import ApplicationNoOpTxn
from utils import txn
from MFLogicSig import sig


def mint(sender, asset1, asset2, asset1_amt, asset2_amt, 
        lp_id, pool_addr, min_received, end_receiver, app_id, params):

    if app_id == 98952143: 
        community_token = 123456
    else:
        community_token = 123456

    foreign_assets = [asset1, asset2, lp_id, community_token]

    txn_1 = txn(asset1, asset1_amt, sender, pool_addr, params)
    txn_2 = txn(asset2, asset2_amt, sender, pool_addr, params)

    call = ApplicationNoOpTxn(
        sender=sender,
        index=app_id,
        app_args=['mint', min_received], # how does slippage work on the call?
        foreign_assets=foreign_assets,
        accounts=[end_receiver, pool_addr],
        sp=params
    )
    call.fee = 4000 # may be 1000 too high

    return [txn_1, txn_2, call]