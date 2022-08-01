import base64
from pyteal import *
from utils import test_app_addr, main_app_addr, main_app_id


def sig(asa0, asa1, feeTier, app_id):
    asa0 = Int(asa0)
    asa1 = Int(asa1)
    feeTier = Int(feeTier)
    if app_id == main_app_id:
        mainAppAddr = Addr(main_app_addr) 
        mainApp = Int(app_id) 
    else:
        mainAppAddr = Addr(test_app_addr) 
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
            Gtxn[2].type_enum() == TxnType.AssetTransfer,
            Gtxn[2].asset_amount() == Int(0),
            Gtxn[2].xfer_asset() == asa1,

            Gtxn[3].type_enum() == TxnType.ApplicationCall,
            Gtxn[3].sender() == Gtxn[0].receiver(),
            Gtxn[3].application_id() == mainApp,
            Gtxn[3].on_completion() == OnComplete.OptIn,
            Gtxn[3].application_args[0] == Itob(feeTier),
            Gtxn[3].rekey_to() == mainAppAddr,
        ))
    )

    return compileTeal(program, mode=Mode.Signature, version=6)