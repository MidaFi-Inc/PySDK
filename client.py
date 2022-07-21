from algosdk import *
from algosdk.v2client import algod
from algosdk.future.transaction import assign_group_id, LogicSigTransaction, wait_for_confirmation
from swap import swap
from swap_exact import swap_exact
from mint import mint
from burn import burn
from utils import sign_group
from MFLogicSig import sig
from create import createPool
from flash_loan import make_flash_loan



class MidaClient:

    # initialize the MidaFi client with
    #   algod: AlgodClient
    #   addr: str, an algorand account address
    #   pk: str, the private key to addr
    #   net: str, defaulted to 'main' for interacting with mainnet, 'test' for testnet
    def __init__(self, algod: algod.AlgodClient, addr=None, pk=None, net='main', ):
        self.algod = algod
        self.addr = addr
        self.pk = pk
        if net == 'test':
            self.app_id = 98952143 # will need to be main one
        else:
            self.app_id = 98952143

    # create a swap transaction
    # returns an unsigned and ungrouped list of the transactions
    #   asset1: int, asset sent to the contract
    #   asset2: int, asset received
    #   asset1_amt: int, amount of asset1 sent in its base units
    #   slippage: int, percent the value of received algos is allowed to drop from the trade
    #   fee_tier: int, coordinated integer value of the fee tier of the pool traded on
    #   end_receiver: str, address of who receives the payment from the swap
    #   lp_id: int, asset id of the lp token of the pool
    #   pool: str, address of the pool
    #   params: algorand transaction parameters
    def swap(self, asset1, asset2, asset1_amt, slippage=1, fee_tier=1, 
             end_receiver=None, lp_id=None, pool=None, params=None): 
        sender = self.addr       
        if not end_receiver:
            end_receiver = sender
        if not params:
            params = self.algod.suggested_params()
        if not pool:
            pool = self.get_pool_addr(asset1, asset2, fee_tier)
        if not lp_id:
            lp_id = self.get_lp_id(pool)
        
        return swap(sender, asset1, asset2, asset1_amt, lp_id, pool,
                    slippage, end_receiver, self.app_id, params)
    
    # create a swap transaction where you receive exactly as much asset2 as requested
    # and get sent the excess asset1 back
    # returns an unsigned and ungrouped list of the transactions
    #   asset1: int, asset sent to the contract
    #   asset2: int, asset received
    #   asset1_amt: int, amount of asset1 sent in its base units
    #   receiving_amt: int, exact amount of asset2 to be received
    def swap_exact(self, asset1, asset2, asset1_amt, receiving_amt, fee_tier=1, 
                   end_receiver=None, lp_id=None, pool=None, params=None):
        sender = self.addr
        if not end_receiver:
            end_receiver = sender
        if not params:
            params = self.algod.suggested_params()
        if not pool:
            pool = self.get_pool_addr(asset1, asset2, fee_tier)
        if not lp_id:
            lp_id = self.get_lp_id(pool)
        
        return swap_exact(sender, asset1, asset2, asset1_amt, receiving_amt, lp_id, pool, end_receiver, self.app_id, params)
    
    # create a mint transaction where you provide liquidity to the pool and receive lp tokens
    # returns an unsigned and ungrouped list of the transactions
    #   asset1: int, asset sent to the contract
    #   asset2: int, asset received
    #   asset1_amt: int, amount of asset1 sent in its base units
    #   asset2_amt: int, amount of asset2 sent in its base units
    #   slippage: int, minimum lp tokens received in base units. 1 MidaFiLP has 6 decimals
    def mint(self, asset1, asset2, asset1_amt, asset2_amt, slippage=0, fee_tier=1, 
             end_receiver=None, lp_id=None, pool=None, params=None):

        sender = self.addr
        if not end_receiver:
            end_receiver = sender
        if not params:
            params = self.algod.suggested_params()
        if not pool:
            pool = self.get_pool_addr(asset1, asset2, fee_tier)
        if not lp_id:
            lp_id = self.get_lp_id(pool)
        
        return mint(sender, asset1, asset2, asset1_amt, asset2_amt, 
                    lp_id, pool, slippage, end_receiver, self.app_id, params)

    # create a burn transaction where you send back lp tokens to receive back provided liquidity
    # returns an unsigned and ungrouped list of the transactions
    #   lp_id: int, asset id of the lp tokens being burned
    #   lp_amt: int, amount of lp tokens sent in base units. 1 MidaFiLP has 6 decimals
    #   asset1_amt: int, amount of asset1 sent in its base units
    #   asset2_amt: int, amount of asset2 sent in its base units
    #   min_asset1: int, minimum amount of asset1 received in base units
    #   min_asset2: int, minimum amount of asset2 received in base units
    def burn(self, lp_id, lp_amt, asset1, asset2, min_asset1=0, min_asset2=0,
            end_receiver=None, pool=None, params=None):

        sender = self.addr
        if not end_receiver:
            end_receiver = self.addr
        if not params:
            params = self.algod.suggested_params()
        if not pool:
            for i in range(1, 7):
                pool = self.get_pool_addr(asset1, asset2, i)
                if self.get_lp_id(pool) == lp_id:
                    break
        return burn(sender, lp_id, lp_amt, asset1, asset2, min_asset1, 
                    min_asset2, pool, end_receiver, self.app_id, params)
    
    # creates and sends transactions to create a new liquidity pool
    #   asset1: int, asset id of the first asset in the pool, 0 if ALGO
    #   asset2: int, asset id of the second asset
    #   fee_tier: int, 1 through 6, fee_tier of the pool which correspond to
    #       1 -> .3%, 2 -> 1%, 3 -> .5%, 4 -> .1%, 5 -> .05%,  6 -> .01%
    def create(self, asset1, asset2, fee_tier=1):
        (logicsig, gtxn) = createPool(self.addr, asset1, asset2, self.algod, fee_tier, self.app_id)
        gtxn = assign_group_id(gtxn)
        stxn1 = gtxn[0].sign(self.pk)
        stxn2 = LogicSigTransaction(gtxn[1],logicsig)
        stxn3 = LogicSigTransaction(gtxn[2],logicsig)
        signed_group = [stxn1, stxn2, stxn3]
        if len(gtxn) == 4:
            signed_group.append(LogicSigTransaction(gtxn[3],logicsig))
        self.algod.send_transactions(signed_group)

    # wraps a gtxn in a flash loan
    # returns a list of the ungrouped and unsigned transactions
    #   asset1: int, asset id of the asset borrowed
    #   asset2: int, asset id of the second asset in pool
    #   amt: int, amount of asset borrowed
    #   pool: str, the pool that the loan will come from
    #   gtxn: list of transactions, group of transactions wrapped in a flash loan
    def borrow_flash_loan(self, asset1, asset2, amt, pool, gtxn, lp_id=None, params=None):
        if not params:
            params = self.algod.suggested_params()
        if not lp_id:
            lp_id = self.get_lp_id(pool)
        return make_flash_loan(gtxn, self.addr, self.addr, pool, asset1, amt, asset2, lp_id, self.algod, self.app_id, params)

    # returns the id of the lp token of a pool
    def get_lp_id(self, pool): # to-do
        assets = self.algod.account_info(pool)['assets']
        lp_id = 0
        for asset in assets:
            if int(asset['asset-id']) > lp_id:
                lp_id = int(asset['asset-id'])
        return lp_id
    
    # returns the address of a pool of a given two assets and fee tier
    def get_pool_addr(self, asset1, asset2, fee_tier):
        if asset1 > asset2:
            return sig(asset1, asset2, fee_tier, self.algod)
        return sig(asset2, asset1, fee_tier, self.algod)
    
    # returns a tuple of the assets in the liquidity pool
    # (asset1, asset2) where the id of asset1 > asset2
    def get_pool_balance(self, pool):
        info = self.algod.account_info(pool)
        assets = info['assets']
        assets.sort(key = lambda a: int(a['asset-id']))
        if len(assets) == 2:
            return (info['amount'], assets[0]['amount'])
        return (assets[0]['amount'], assets[1]['amount'])

    # groups, signs, and sends the group transaction
    # returns a string of the transaction id of the group
    #   gtxn: list of transactions
    #   wait: bool, True to wait for the transaction to be commited into a block,
    #               False to immediately continue executing
    def send_group(self, gtxn, wait=False):
        gtxn = sign_group(gtxn, self.pk)
        tx_id = self.algod.send_transactions(gtxn)
        if wait:
            wait_for_confirmation(self.algod, tx_id)
        return tx_id


