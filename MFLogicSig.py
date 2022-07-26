import base64
import os
from pyteal import *
from algosdk.future.transaction import LogicSigAccount

def sig(asa0, asa1, feeTier, algod_client):
    asa0 = Int(asa0)
    asa1 = Int(asa1)
    feeTier = Int(feeTier)
    mainAppAddr = Addr("DLFFM3JUFZDAILYYGF6PCWIDZE3ALYFVP7J62IGFUOWYMTE5H76PTBKOOE")
    mainApp = Int(100635609)

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

    compiled = compileTeal(program, mode=Mode.Signature, version=6)

    logicsig = LogicSigAccount(base64.decodebytes(algod_client.compile(compiled)['result'].encode()))
    poolAddr = logicsig.address()

    return poolAddr