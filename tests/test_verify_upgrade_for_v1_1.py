# import brownie
# from brownie import *
# import pytest

# """
# Tests for Upgrading Sett V1 to V4h
# """


# # bSLP
# # https://etherscan.io/address/0x1862A18181346EBd9EdAf800804f89190DeF24a5
# # SettV1.1

# # wBTC / DIGG
# # https://etherscan.io/address/0x88128580ACdD9c04Ce47AFcE196875747bF2A9f6
# # SettV1.1


# LIST_OF_EXPLOITERS = [
#         "0xa33B95ea28542Ada32117B60E4F5B4cB7D1Fc19B",
#         "0x4fbf7701b3078B5bed6F3e64dF3AE09650eE7DE5",
#         "0x1B1b391D1026A4e3fB7F082ede068B25358a61F2",
#         "0xEcD91D07b1b6B81d24F2a469de8e47E3fe3050fd",
#         "0x691dA2826AC32BBF2a4b5d6f2A07CE07552A9A8E",
#         "0x91d65D67FC573605bCb0b5E39F9ef6E18aFA1586",
#         "0x0B88A083dc7b8aC2A84eBA02E4acb2e5f2d3063C",
#         "0x2eF1b70F195fd0432f9C36fB2eF7C99629B0398c",
#         "0xbbfD8041EbDE22A7f3e19600B4bab4925Cc97f7D",
#         "0xe06eD65924dB2e7b4c83E07079A424C8a36701E5"
#     ]

# SETT_ADDRESSES = [
#     "0x1862A18181346EBd9EdAf800804f89190DeF24a5",
#     "0x88128580ACdD9c04Ce47AFcE196875747bF2A9f6",
# ]

# @pytest.fixture
# def proxy_admin():
#     """
#      Verify by doing web3.eth.getStorageAt("STRAT_ADDRESS", int(
#         0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103
#     )).hex()
#     """
#     return Contract.from_explorer("0x20dce41acca85e8222d6861aa6d23b6c941777bf")


# @pytest.fixture
# def proxy_admin_gov():
#     """
#         Also found at proxy_admin.owner()
#     """
#     return accounts.at("0x21cf9b77f88adf8f8c98d7e33fe601dc57bc0893", force=True)


# @pytest.fixture
# def bve_cvx():
#     """
#         Need to unpause for "advanced" vaults
#     """
#     return SettV4h.at("0xfd05D3C7fe2924020620A8bE4961bBaA747e6305")

# @pytest.mark.parametrize(
#     "settAddress",
#     SETT_ADDRESSES,
# )
# def test_upgrade_and_harvest(settAddress, proxy_admin, proxy_admin_gov, bve_cvx):
#     vault_proxy = SettV4h.at(settAddress)

#     bve_gov = accounts.at(bve_cvx.governance(), force=True)
#     if(bve_cvx.paused()):
#         bve_cvx.unpause({"from": bve_gov})

#     prev_gov = vault_proxy.governance()

#     governance = accounts.at(prev_gov, force=True)
#     ## TODO: Add new code that will revert as it's not there yet
#     with brownie.reverts():
#         vault_proxy.patchBalances({"from": governance}) ## Not yet implemented
#     with brownie.reverts():
#         vault_proxy.MULTISIG() ## Not yet implemented

#     ## Setting all variables, we'll use them later
#     prev_gov = vault_proxy.governance()
#     prev_keeper = vault_proxy.keeper()
#     prev_token = vault_proxy.token()
#     prev_balance = vault_proxy.balance()
#     prev_min = vault_proxy.min()
#     prev_max = vault_proxy.max()
#     prev_getPricePerFullShare = vault_proxy.getPricePerFullShare()
#     prev_available = vault_proxy.available()

#     ## TODO: Add write operations
#     new_vault_logic = SettV4h.deploy({"from": governance})

#     # Deploy new logic
#     proxy_admin.upgrade(vault_proxy, new_vault_logic, {"from": proxy_admin_gov})


#     ## Checking all variables are as expected
#     assert vault_proxy.version() == '1.4h - Hack Amended' ## It is different
#     assert prev_gov == vault_proxy.governance()
#     assert prev_keeper == vault_proxy.keeper()
#     assert prev_token == vault_proxy.token()
#     assert prev_balance == vault_proxy.balance()
#     assert prev_min == vault_proxy.min()
#     assert prev_max == vault_proxy.max()
#     assert prev_getPricePerFullShare == vault_proxy.getPricePerFullShare()
#     assert prev_available == vault_proxy.available()



#     ## Verify new Addresses are setup properly
#     assert vault_proxy.MULTISIG() == "0xB65cef03b9B89f99517643226d76e286ee999e77"

#     # ## Also run all ordinary operation just because
#     ## deposit
#     ## depositAll
#     ## depositFor
#     ## withdraw
#     ## withdrawAll
#     ## transfer
#     ## transferFrom
#     ## harvest
#     ## earn
#     ## pause
#     ## unpause

#     with brownie.reverts():
#         vault_proxy.pause({"from": accounts[0]}) ## Not everyone can pause
    
#     assert vault_proxy.paused() == True ## Vaults are currently paused

#     vault_proxy.unpause({"from": governance})
#     assert vault_proxy.paused() == False

#     vault_proxy.unpause({"from": governance})
#     assert vault_proxy.paused() == False


#     ## Compare prev balance against new balances
#     prev_multi_balance = vault_proxy.balanceOf(vault_proxy.MULTISIG())

#     ## Harvest should work
#     vault_proxy.patchBalances({"from": governance})

#     after_balance = vault_proxy.balanceOf(vault_proxy.MULTISIG())

#     assert after_balance > prev_multi_balance  

#     for exploiter in LIST_OF_EXPLOITERS:
#         assert vault_proxy.balanceOf(exploiter) == 0

    

#     ## Let's run some operations now that we have funds
#     controller = interface.IController(vault_proxy.controller())
#     strat = interface.IStrategy(controller.strategies(vault_proxy.token()))
#     strat_gov = accounts.at(strat.governance(), force=True)
    
#     if strat.paused():
#         strat.unpause({"from": strat_gov})

#     ## Earn
#     vault_proxy.earn({"from": governance})
#     assert vault_proxy.balance() == prev_balance

#     ## Harvest
#     strat.harvest({"from": governance})
#     assert vault_proxy.getPricePerFullShare() >= prev_getPricePerFullShare  ## Not super happy about >= but it breaks for emitting

#     ## Withdraw
#     underlying = ERC20Upgradeable.at(vault_proxy.token())
#     prev_balance_of_underlying = underlying.balanceOf(governance)
#     vault_proxy.withdraw(1000, {"from": governance})
#     assert underlying.balanceOf(governance) > prev_balance_of_underlying 


#     ## WithdrawAll
#     prev_balance_of_underlying = underlying.balanceOf(governance)
#     vault_proxy.withdrawAll({"from": governance})
#     assert underlying.balanceOf(governance) > prev_balance_of_underlying 


    
#     ## Deposit
#     prev_shares = vault_proxy.balanceOf(governance)
#     prev_balance_of_underlying = underlying.balanceOf(governance)
#     underlying.approve(vault_proxy, underlying.balanceOf(governance), {"from": governance})
#     vault_proxy.deposit(1000, {"from": governance})
#     assert underlying.balanceOf(governance) < prev_balance_of_underlying 
#     assert vault_proxy.balanceOf(governance) > prev_shares

#     ## DepositAll
#     prev_shares = vault_proxy.balanceOf(governance)
#     prev_balance_of_underlying = underlying.balanceOf(governance)
#     vault_proxy.depositAll({"from": governance})
#     assert underlying.balanceOf(governance) < prev_balance_of_underlying 
#     assert vault_proxy.balanceOf(governance) > prev_shares






