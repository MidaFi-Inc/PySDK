from algosdk.future.transaction import PaymentTxn, AssetTransferTxn, assign_group_id

# constants

test_app_addr = "DLFFM3JUFZDAILYYGF6PCWIDZE3ALYFVP7J62IGFUOWYMTE5H76PTBKOOE"
test_app_id = 100635609
test_com_token = 100540308

main_app_addr = ""
main_app_id = 0
main_com_token = 0


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