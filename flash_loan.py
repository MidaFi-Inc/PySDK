from algosdk.future.transaction import ApplicationNoOpTxn
import algosdk.encoding as e
from utils import txn

def make_flash_loan(gtxn, sender, receiver, pool, asset1, amt, asset2, lp_id, algod_client, app_id, params):
    
    if app_id == 98952143: 
        community_token = 123456
    else:
        community_token = 123456

    if not params:
        params = algod_client.suggested_params()

    accounts = [receiver, pool]
    assets = [asset1, asset2, lp_id, community_token]
    borrow_call = ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=app_id,
        foreign_assets=assets,
        accounts=accounts,
        app_args=['loan', asset1, amt],
    )
    borrow_call.fee = 2000

    repay_txn = txn(asset1, int(amt*1.01)+1, sender, pool, params)
    
    repay_call = ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=app_id,
        foreign_assets=assets,
        accounts=accounts,
        app_args=['repay'],
    )

    gtxn.insert(0, borrow_call)
    gtxn.append(repay_txn)
    gtxn.append(repay_call)

    return gtxn
