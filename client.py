import imp
from algosdk import *
from algosdk.v2client import algod
from algosdk.future.transaction import assign_group_id, LogicSigTransaction

from swap import swap
from swap_exact import swap_exact
from mint import mint
from burn import burn
from utils import sign_group
from MFLogicSig import sig
from create import createPool
from flash_loan import make_flash_loan



class MidaClient:
    def __init__(self, algod: algod.AlgodClient, net='main', addr=None, pk=None):
        self.algod = algod
        self.addr = addr
        self.pk = pk
        if net == 'test':
            self.app_id = 98952143 # will need to be main one
        else:
            self.app_id = 98952143

    def swap(self, asset1, asset2, asset1_amt, slippage=1, fee_tier=1, sender=None, 
             end_receiver=None, params=None, lp_id=None, pool=None):        
        if not sender:
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
    
    def swap_exact(self, asset1, asset2, asset1_amt, receiving_amt, fee_tier=1, sender=None, 
                   end_receiver=None, params=None, lp_id=None, pool=None):
        if not sender:
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

    def mint(self, asset1, asset2, asset1_amt, asset2_amt, slippage=0, fee_tier=1, 
             sender=None, end_receiver=None, params=None, lp_id=None, pool=None):
        if not sender:
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
    
    def burn(self, lp_id, lp_amt, asset1, asset2, min_asset1=0, min_asset2=0,
             sender=None, end_receiver=None, params=None, pool=None):
        if not sender:
            sender = self.addr
        if not end_receiver:
            end_receiver = self.addr
        if not params:
            params = self.algod.suggested_params()
        if not lp_id:
            assets = self.get_asset_ids(lp_id) # not functioning
        if not pool:
            pool = self.get_pool_from_lp(lp_id) # not functioning

        return burn(sender, lp_id, lp_amt, assets[0], assets[1], min_asset1, 
                    min_asset2, pool, end_receiver, self.app_id, params)
    
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

    def borrow_flash_loan(self, asset, amt, gtxn, params=None,):
        if not params:
            params = self.algod.suggested_params()
            
        return make_flash_loan(gtxn, self.addr, asset, amt, self.algod, self.app_id, params)


    def get_lp_id(self, pool): # to-do
        assets = self.algod.account_info(pool)['assets']
        lp_id = 0
        for asset in assets:
            if int(asset['asset-id']) > lp_id:
                lp_id = int(asset['asset-id'])
        return lp_id
    
    def get_pool_addr(self, asset1, asset2, fee_tier):
        return sig(asset1, asset2, fee_tier, self.algod)
    
    def get_pool_balance(self, pool):
        info = self.algod.account_info(pool)
        assets = info['assets']
        assets.sort(key = lambda a: int(a['asset-id']))
        if len(assets) == 2:
            return (info['amount'], assets[0]['amount'])
        return (assets[0]['amount'], assets[1]['amount'])

    def send_group(self, gtxn):
        gtxn = sign_group(gtxn, self.pk)
        self.algod.send_transactions(gtxn)


