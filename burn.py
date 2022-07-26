from algosdk.future.transaction import ApplicationNoOpTxn
from utils import txn, test_app_id, test_com_token, main_com_token

def burn(sender, lp_id, lp_amt, asset1, asset2, min_asset1, min_asset2, pool_addr, end_receiver, app_id, params):

    if app_id == test_app_id: 
        community_token = test_com_token
    else:
        community_token = main_com_token

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