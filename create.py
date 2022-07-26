from pyteal import *
from algosdk.future.transaction import LogicSigAccount, LogicSigTransaction, PaymentTxn, ApplicationNoOpTxn, AssetTransferTxn, ApplicationOptInTxn
from pyteal import *
import base64
from utils import main_app_addr, test_app_id, test_app_addr

def sig(asa0, asa1, feeTier, app_id, app_addr):
    mainAppAddr = Addr(app_addr)
    mainApp = Int(app_id)

    program = And(
        asa0 > asa1,
        asa0 == Gtxn[Global.group_size() - Int(1)].assets[0],
        asa1 == Gtxn[Global.group_size() - Int(1)].assets[1],
        Txn.close_remainder_to() == Global.zero_address(),

        Gtxn[0].rekey_to() == Global.zero_address(),
        Gtxn[1].rekey_to() == Global.zero_address(),

        Gtxn[0].sender() != Gtxn[0].receiver(),
        Gtxn[1].sender() == Gtxn[0].receiver(),
        Gtxn[2].sender() == Gtxn[0].receiver(),

        Gtxn[0].type_enum() == TxnType.Payment,
        Gtxn[0].amount() >= Int(1003000),
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(0),
        Gtxn[1].xfer_asset() == asa0,

        If(asa1 == Int(0))
        .Then(And(
            Gtxn[2].type_enum() == TxnType.ApplicationCall,
            Gtxn[2].application_id() == mainApp,
            Gtxn[2].on_completion() == OnComplete.OptIn,
            Gtxn[2].application_args[0] == Itob(feeTier),
            Gtxn[2].rekey_to() == mainAppAddr,
        )).Else(And(
            Gtxn[2].rekey_to() == Global.zero_address(),
            Gtxn[3].sender() == Gtxn[0].receiver(),
            Gtxn[2].type_enum() == TxnType.AssetTransfer,
            Gtxn[3].type_enum() == TxnType.ApplicationCall,
            Gtxn[2].asset_amount() == Int(0),
            Gtxn[2].xfer_asset() == asa1,
            Gtxn[3].application_id() == mainApp,
            Gtxn[3].on_completion() == OnComplete.OptIn,
            Gtxn[3].application_args[0] == Itob(feeTier),
            Gtxn[3].rekey_to() == mainAppAddr,
        ))
    )

    return compileTeal(program, mode=Mode.Signature, version=6)


def createPool(sender, asa0, asa1, algod_client, fee_tier, app_id):
    if asa0 < asa1:
        t = asa0
        asa0 = asa1
        asa1 = t
    if app_id == test_app_id:
        app_addr = test_app_addr
    else:
        app_addr = main_app_addr
    
    logicsig = LogicSigAccount(base64.decodebytes(algod_client.compile(sig(Int(asa0), Int(asa1), Int(fee_tier), app_id, app_addr))['result'].encode()))
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

