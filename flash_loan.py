from algosdk.future.transaction import ApplicationNoOpTxn
import algosdk.encoding as e
from utils import txn

def make_flash_loan(gtxn, sender, asset, amt, algod_client, app_id, params):
    
    mainAppAddr = e.encode_address(e.checksum(b'appID'+(app_id).to_bytes(8, 'big')))

    if not params:
        params = algod_client.suggested_params()

    borrow_call = ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=app_id,
        foreign_assets=[asset],
        app_args=['loan', asset, amt],
    )

    repay_txn = txn(asset, int(amt*1.01), sender, mainAppAddr, params)

    repay_call = ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=app_id,
        foreign_assets=[asset],
        app_args=['repay'],
    )

    gtxn.insert(0, borrow_call)
    gtxn.append(repay_txn)
    gtxn.append(repay_call)

    return gtxn
