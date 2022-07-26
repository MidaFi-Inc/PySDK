from algosdk.future.transaction import ApplicationNoOpTxn
from utils import txn, test_app_id, test_com_token, main_com_token

def swap_exact(sender, asset1, asset2, asset1_amt, receiving_amt, lp_id, pool_addr, end_receiver, app_id, params): 

    if app_id == test_app_id: 
        community_token = test_com_token
    else:
        community_token = main_com_token

    foreign_assets = [asset1, asset2, lp_id, community_token]

    txn_1 = txn(asset1, asset1_amt, sender, pool_addr, params)

    accts = [end_receiver, pool_addr]
    call = ApplicationNoOpTxn(
        sender=sender,
        index=app_id,
        app_args=['swapExact', receiving_amt],
        foreign_assets=foreign_assets,
        accounts=accts,
        sp=params
    )
    call.fee = 3000
    return [txn_1, call]