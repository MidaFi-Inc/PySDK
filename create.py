import base64
from pyteal import *
from algosdk.future.transaction import LogicSigAccount, PaymentTxn, AssetTransferTxn, ApplicationOptInTxn
from pyteal import *
from utils import main_app_addr, test_app_id, test_app_addr
from MFLogicSig import sig


def createPool(sender, asa0, asa1, algod_client, fee_tier, app_id):
    if asa0 < asa1:
        t = asa0
        asa0 = asa1
        asa1 = t
    if app_id == test_app_id:
        app_addr = test_app_addr
    else:
        app_addr = main_app_addr
    
    compiled_sig = sig(asa0, asa1, fee_tier, app_id)
    logicsig = LogicSigAccount(base64.decodebytes(algod_client.compile(compiled_sig)['result'].encode()))
    poolAddr = logicsig.address()
    
    params = algod_client.suggested_params()
    appsp = algod_client.suggested_params()
    appsp.flat_fee=True
    params.flat_fee=True
    params.fee = 1000
    appsp.fee = 2000
    
    tx1 = PaymentTxn(
        sender=sender,
        sp=params,
        receiver=poolAddr,  
        amt=1003000
    )

    tx2 = AssetTransferTxn(
        sender=poolAddr,
        sp=params,
        receiver=poolAddr,
        amt=0,
        index=asa0,
    )

    txapp = ApplicationOptInTxn(
        sender=poolAddr,
        sp=appsp,
        index=app_id,
        rekey_to=app_addr,
        app_args=[fee_tier],
        foreign_assets=[asa0,asa1]
    )
    gtxn = [tx1, tx2, txapp]

    if asa1 != 0:
        tx3 = AssetTransferTxn(
            sender=poolAddr,
            sp=params,
            receiver=poolAddr,
            amt=0,
            index=asa1,
        )
        gtxn.insert(2, tx3)

    return (logicsig, gtxn)

