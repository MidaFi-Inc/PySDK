from pyteal import *
from algosdk.future import transaction
from algosdk.future.transaction import LogicSigAccount, LogicSigTransaction, PaymentTxn, ApplicationNoOpTxn, AssetTransferTxn, ApplicationOptInTxn
from pyteal import *
import base64
import algosdk.encoding as e

def sig(asa0, asa1, feeTier):
    mainAppAddr = Addr("6MGHCXWOHEKHFWLWUYKHBTFRNISOYICFB35ERPKMWA3ZGVLHUMFR5ESWEQ") #Manual tests
    mainApp = Int(98952143) #Manual tests

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


def createPool(sender, sender_private_key, asa0, asa1, algod_client, fee_tier=1, testnet=False):
    
    if testnet:
        mainAppId = 98952143
    else:
        mainAppId = 98952143
    
    logicsig = LogicSigAccount(base64.decodebytes(algod_client.compile(sig(Int(asa0), Int(asa1), Int(fee_tier)))['result'].encode()))
    poolAddr = logicsig.address()
    mainAppAddr = e.encode_address(e.checksum(b'appID'+(mainAppId).to_bytes(8, 'big')))
    
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
        index=mainAppId,
        rekey_to=mainAppAddr,
        app_args=[1],
        foreign_assets=[asa0,asa1]
    )

    if asa1 != 0:
        tx3 = AssetTransferTxn(
            sender=poolAddr,
            sp=params,
            receiver=poolAddr,
            amt=0,
            index=asa1,
        )

        gid = transaction.calculate_group_id([tx1,tx2,tx3,txapp])

        tx1.group = gid
        tx2.group = gid
        tx3.group = gid
        txapp.group = gid

        stxn1 = tx1.sign(sender_private_key)
        stxn2 = LogicSigTransaction(tx2,logicsig)
        stxn3 = LogicSigTransaction(tx3,logicsig)
        stxapp = LogicSigTransaction(txapp,logicsig)
        algod_client.send_transactions([stxn1,stxn2,stxn3,stxapp])
    else:
        gid = transaction.calculate_group_id([tx1,tx2,txapp])

        tx1.group = gid
        tx2.group = gid
        txapp.group = gid

        stxn1 = tx1.sign(sender_private_key)
        stxn2 = LogicSigTransaction(tx2,logicsig)
        stxapp = LogicSigTransaction(txapp,logicsig)
        algod_client.send_transactions([stxn1,stxn2,stxapp])

    return poolAddr