import brownie
from brownie import SettV4h, interface, accounts, ERC20Upgradeable
import pytest
from badger_utils.token_utils.distribute_from_whales_realtime import distribute_from_whales_realtime_percentage

"""
Tests for Upgrading Sett V4 to V4h
There's gonna be a separate suite for V1 to V4h
"""

# Remaining Setts

# bcrvHBTC
# https://etherscan.io/address/0x8c76970747afd5398e958bdfada4cf0b9fca16c4
# SettV3

# bcrvPBTC
# https://etherscan.io/address/0x55912d0cf83b75c492e761932abc4db4a5cb1b17
# SettV3

# bcrvOBTC
# https://etherscan.io/address/0xf349c0faa80fc1870306ac093f75934078e28991
# SettV3

# bcrvBBTC
# https://etherscan.io/address/0x5dce29e92b1b939f8e8c60dcf15bde82a85be4a9
# SettV3

# bcrvTricrypto
# https://etherscan.io/address/0xBE08Ef12e4a553666291E9fFC24fCCFd354F2Dd2
# SettV3

# bCVX
# https://etherscan.io/address/0x53c8e199eb2cb7c01543c137078a038937a68e40
# SettV4


LIST_OF_EXPLOITERS = [
    "0xa33B95ea28542Ada32117B60E4F5B4cB7D1Fc19B",
    "0x4fbf7701b3078B5bed6F3e64dF3AE09650eE7DE5",
    "0x1B1b391D1026A4e3fB7F082ede068B25358a61F2",
    "0xEcD91D07b1b6B81d24F2a469de8e47E3fe3050fd",
    "0x691dA2826AC32BBF2a4b5d6f2A07CE07552A9A8E",
    "0x91d65D67FC573605bCb0b5E39F9ef6E18aFA1586",
    "0x0B88A083dc7b8aC2A84eBA02E4acb2e5f2d3063C",
    "0x2eF1b70F195fd0432f9C36fB2eF7C99629B0398c",
    "0xbbfD8041EbDE22A7f3e19600B4bab4925Cc97f7D",
    "0xe06eD65924dB2e7b4c83E07079A424C8a36701E5"
]


SETT_REMAINING = [
    "0x8c76970747afd5398e958bdfada4cf0b9fca16c4",
    "0x55912d0cf83b75c492e761932abc4db4a5cb1b17",
    "0xf349c0faa80fc1870306ac093f75934078e28991",
    "0x5dce29e92b1b939f8e8c60dcf15bde82a85be4a9",
    "0xBE08Ef12e4a553666291E9fFC24fCCFd354F2Dd2",
    "0x53c8e199eb2cb7c01543c137078a038937a68e40",
]

@pytest.mark.parametrize(
    "settAddress",
    SETT_REMAINING,
)
def test_upgrade_and_harvest(settAddress, proxy_admin, proxy_admin_gov, bve_cvx, bcvx_crv):
    vault_proxy = SettV4h.at(settAddress)

    if(bve_cvx.paused() and not settAddress == bve_cvx.address):
        bve_gov = accounts.at(bve_cvx.governance(), force=True)
        bve_cvx.unpause({"from": bve_gov})
    
    if(bcvx_crv.paused() and not settAddress == bcvx_crv.address):
        bcvx_crv_gov = accounts.at(bcvx_crv.governance(), force=True)
        bcvx_crv.unpause({"from": bcvx_crv_gov})

    prev_gov = vault_proxy.governance()
    prev_guardian = vault_proxy.guardian()

    governance = accounts.at(prev_gov, force=True)
    guardian = accounts.at(prev_guardian, force=True)
    ## TODO: Add new code that will revert as it's not there yet
    with brownie.reverts():
        vault_proxy.patchBalances({"from": governance}) ## Not yet implemented
    with brownie.reverts():
        vault_proxy.MULTISIG() ## Not yet implemented

    ## Setting all variables, we'll use them later
    prev_gov = vault_proxy.governance()
    prev_keeper = vault_proxy.keeper()
    prev_token = vault_proxy.token()
    prev_balance = vault_proxy.balance()
    prev_min = vault_proxy.min()
    prev_max = vault_proxy.max()
    prev_guestList = vault_proxy.guestList()
    prev_getPricePerFullShare = vault_proxy.getPricePerFullShare()
    prev_available = vault_proxy.available()
    prev_controller = vault_proxy.controller()

    prev_paused = vault_proxy.paused()


    ## TODO: Add write operations
    new_vault_logic = SettV4h.deploy({"from": governance})

    # Deploy new logic
    proxy_admin.upgrade(vault_proxy, new_vault_logic, {"from": proxy_admin_gov})


    ## Checking all variables are as expected
    assert vault_proxy.version() == '1.4h - Hack Amended' ## It is different
    assert prev_gov == vault_proxy.governance()
    assert prev_guardian == vault_proxy.guardian()
    assert prev_controller == vault_proxy.controller()
    assert prev_keeper == vault_proxy.keeper()
    assert prev_token == vault_proxy.token()
    assert prev_balance == vault_proxy.balance()
    assert prev_min == vault_proxy.min()
    assert prev_max == vault_proxy.max()
    assert prev_guestList == vault_proxy.guestList()
    assert prev_getPricePerFullShare == vault_proxy.getPricePerFullShare()
    assert prev_available == vault_proxy.available()
    assert prev_paused == vault_proxy.paused()



    ## Verify new Addresses are setup properly
    assert vault_proxy.MULTISIG() == "0x9faA327AAF1b564B569Cb0Bc0FDAA87052e8d92c"

    # ## Also run all ordinary operation just because
    ## deposit
    ## depositAll
    ## depositFor
    ## withdraw
    ## withdrawAll
    ## transfer
    ## transferFrom
    ## harvest
    ## earn
    ## pause
    ## unpause
    ## We re-pause as some Setts are not paused

    if vault_proxy.paused() == True:
    ## You can unpause if GAC is paused or unpaused
        vault_proxy.unpause({"from": governance})
        assert vault_proxy.paused() == False

    ## Verify that unpausing allows to earn
    gac = interface.IGac(vault_proxy.GAC())
    gac_gov = accounts.at(gac.DEV_MULTISIG(), force=True)
    if gac.paused() == True:
        gac.unpause({"from": gac_gov})

    if gac.transferFromDisabled() == True:
        gac.enableTransferFrom({"from": gac_gov})

    vault_proxy.pause({"from": governance}) ## Now you can pause
    vault_proxy.unpause({"from": governance}) ## Let's unpause to test transferFrom

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        vault_proxy.transferFrom(accounts[0], governance, 123, {"from": governance}) ## Now it fails because of allowance

    with brownie.reverts():
        vault_proxy.pause({"from": accounts[0]}) ## Not everyone can pause
    
    assert vault_proxy.paused() == False ## Vaults are currently unpaused

    vault_proxy.pause({"from": guardian})
    assert vault_proxy.paused() == True

    vault_proxy.unpause({"from": governance})
    assert vault_proxy.paused() == False
        

    ## Compare prev balance against new balances
    prev_multi_balance = vault_proxy.balanceOf(vault_proxy.MULTISIG())

    ## Get total stolen sett balances
    stolen_balance = 0
    for exploiter in LIST_OF_EXPLOITERS:
        stolen_balance += vault_proxy.balanceOf(exploiter)
    assert stolen_balance == 0

    vault_proxy.patchBalances({"from": governance})

    after_balance = vault_proxy.balanceOf(vault_proxy.MULTISIG())

    # No balance for these Setts on Exploiters wallets
    assert after_balance == prev_multi_balance


    ## Generic operations
    controller = interface.IController(vault_proxy.controller())
    strat = interface.IStrategy(controller.strategies(vault_proxy.token()))
    strat_gov = accounts.at(strat.governance(), force=True)
    
    if strat.paused():
        strat.unpause({"from": strat_gov})

    ## Harvest
    strat.harvest({"from": governance})
    assert vault_proxy.getPricePerFullShare() >= prev_getPricePerFullShare  ## Not super happy about >= but it breaks for emitting

    ## Send funds to test
    multi = accounts.at(vault_proxy.MULTISIG(), force=True)
    ## Gas
    accounts[0].transfer(to=multi, amount=accounts[0].balance())
    ## Send distribute tokens to governance for testing
    distribute_from_whales_realtime_percentage(governance, 0.8, [vault_proxy.address])

    ## Withdraw
    underlying = ERC20Upgradeable.at(vault_proxy.token())
    prev_balance_of_underlying = underlying.balanceOf(governance)
    vault_proxy.withdraw(1000, {"from": governance})
    assert underlying.balanceOf(governance) > prev_balance_of_underlying 

    ## Deposit
    prev_shares = vault_proxy.balanceOf(governance)
    prev_balance_of_underlying = underlying.balanceOf(governance)
    underlying.approve(vault_proxy, underlying.balanceOf(governance), {"from": governance})
    vault_proxy.deposit(1000, {"from": governance})
    assert underlying.balanceOf(governance) < prev_balance_of_underlying 
    assert vault_proxy.balanceOf(governance) > prev_shares

    ## DepositAll
    prev_shares = vault_proxy.balanceOf(governance)
    prev_balance_of_underlying = underlying.balanceOf(governance)
    vault_proxy.depositAll({"from": governance})
    assert underlying.balanceOf(governance) < prev_balance_of_underlying 
    assert vault_proxy.balanceOf(governance) > prev_shares

    ## Earn
    prev_balance = vault_proxy.balance()
    vault_proxy.earn({"from": governance})
    assert vault_proxy.balance() == prev_balance

    ## Transfer From
    rando = accounts[1]
    amount = vault_proxy.balanceOf(multi)/4
    vault_proxy.approve(rando, vault_proxy.balanceOf(multi), {"from": multi})
    vault_proxy.transferFrom(
        multi.address, 
        rando.address, 
        amount, 
        {"from": rando}
    )
    assert vault_proxy.balanceOf(rando.address) == amount

    # Globally disable transferFrom
    gac.disableTransferFrom({"from": gac_gov})
    with brownie.reverts("transferFrom: GAC transferFromDisabled"):
        vault_proxy.transferFrom(
            multi.address, 
            rando.address, 
            amount, 
            {"from": rando}
        )

    # Transfer
    vault_proxy.transfer(
        accounts[2],
        amount, 
        {"from": rando}
    )
    assert vault_proxy.balanceOf(accounts[2]) == amount



