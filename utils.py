import algosdk
from algosdk.future.transaction import PaymentTxn, AssetTransferTxn, assign_group_id

def txn(asset, amt, sender, receiver, params):
    if asset == 0:
        txn = PaymentTxn(
            sender=sender,
            receiver=receiver,
            amt=amt,
            sp=params
        )
    else:
        txn = AssetTransferTxn(
            sender=sender,
            receiver=receiver,
            index=asset,
            amt=amt,
            sp=params
        )
    return txn

def sign_group(group, pk):
    group = assign_group_id(group)
    sg = []
    [sg.append(t.sign(pk)) for t in group]
    return sg