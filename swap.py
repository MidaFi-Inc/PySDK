from algosdk.future.transaction import ApplicationNoOpTxn
from utils import txn, test_app_id, test_com_token, main_com_token


def swap(sender, asset1, asset2, asset1_amt, lp_id, pool_addr, 
        slippage, end_receiver, app_id, params):

    if app_id == test_app_id: 
        community_token = test_com_token
    else:
        community_token = main_com_token

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