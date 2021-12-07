import brownie
from brownie import *
import pytest

"""
Tests for Upgrading Sett V4 to V4h
There's gonna be a separate suite for V1 to V4h
"""

# bcvxCRV
# https://etherscan.io/address/0x2B5455aac8d64C14786c3a29858E43b5945819C0
# SettV4

# ibBTC LP Curv
# https://etherscan.io/address/0xaE96fF08771a109dc6650a1BdCa62F2d558E40af
# SettV4

# tricryptoTwo
# https://etherscan.io/address/0x27E98fC7d05f54E544d16F58C194C2D7ba71e3B5
# SettV3

# mStable BTC 
# https://etherscan.io/address/0x599D92B453C010b1050d31C364f6ee17E819f193
# SettV4

# mStable mhBTC
# https://etherscan.io/address/0x26B8efa69603537AC8ab55768b6740b67664D518
# SettV4

# bveCVX
# https://etherscan.io/address/0xfd05D3C7fe2924020620A8bE4961bBaA747e6305
# SettV4

# bveCVX CRV LP
# https://etherscan.io/address/0x937B8E917d0F36eDEBBA8E459C5FB16F3b315551
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

SETT_ADDRESSES = [
    "0x2B5455aac8d64C14786c3a29858E43b5945819C0",
    "0xaE96fF08771a109dc6650a1BdCa62F2d558E40af",
    "0x27E98fC7d05f54E544d16F58C194C2D7ba71e3B5",

    "0x599D92B453C010b1050d31C364f6ee17E819f193",
    "0x26B8efa69603537AC8ab55768b6740b67664D518",
    "0xfd05D3C7fe2924020620A8bE4961bBaA747e6305",
    "0x937B8E917d0F36eDEBBA8E459C5FB16F3b315551"
]

@pytest.mark.parametrize(
    "settAddress",
    SETT_ADDRESSES,
)
def test_upgrade_and_harvest(settAddress, proxy_admin, proxy_admin_gov, bve_cvx):
    vault_proxy = SettV4h.at(settAddress)

    bve_gov = accounts.at(bve_cvx.governance(), force=True)
    if(bve_cvx.paused()):
        bve_cvx.unpause({"from": bve_gov})

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

    assert vault_proxy.paused() == True
    ## You can unpause if GAC is paused or unpaused

    vault_proxy.unpause({"from": governance})
    assert vault_proxy.paused() == False

    ## GAC
    ## Verify that system still is paused because of GAC
    with brownie.reverts("Pausable: GAC Paused"):
        vault_proxy.pause({"from": governance}) ## You can't pause if GAC has already paused
        ## Quirkiness of the system
        ## To pause a single GAC needs to be unpaused first

    ## Verify that unpausing allows to earn
    gac = interface.IGac(vault_proxy.GAC())
    gac_gov = accounts.at(gac.DEV_MULTISIG(), force=True)
    gac.unpause({"from": gac_gov})

    vault_proxy.pause({"from": governance}) ## Now you can pause
    vault_proxy.unpause({"from": governance}) ## Let's unpause to test transferFrom

    ## GAC transferFrom
    ## Verify that unpausing doesn't allow transferFrom because transferFrom is blocked by GAC
    with brownie.reverts("transferFrom: GAC transferFromDisabled"):
        vault_proxy.transferFrom(accounts[0], governance, 123, {"from": governance}) ## Even withou allowance it fails with our error

    ## Verfiy that allowing transferFrom while unpaused allows transferFrom
    gac.enableTransferFrom({"from": gac_gov})

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        vault_proxy.transferFrom(accounts[0], governance, 123, {"from": governance}) ## Now it fails because of allowance


    with brownie.reverts():
        vault_proxy.pause({"from": accounts[0]}) ## Not everyone can pause
    
    assert vault_proxy.paused() == False ## Vaults are currently paused

    vault_proxy.pause({"from": guardian})
    assert vault_proxy.paused() == True

    vault_proxy.unpause({"from": governance})
    assert vault_proxy.paused() == False
        


    ## Compare prev balance against new balances
    prev_multi_balance = vault_proxy.balanceOf(vault_proxy.MULTISIG())

    ## Rug the exploiter
    vault_proxy.patchBalances({"from": governance})

    after_balance = vault_proxy.balanceOf(vault_proxy.MULTISIG())

    ## Verify gov has new funds
    assert after_balance > prev_multi_balance  

    ## Verify they have nothing left
    for exploiter in LIST_OF_EXPLOITERS:
        assert vault_proxy.balanceOf(exploiter) == 0


    ## Generic operations
    ## Let's run some operations now that we have funds
    controller = interface.IController(vault_proxy.controller())
    strat = interface.IStrategy(controller.strategies(vault_proxy.token()))
    strat_gov = accounts.at(strat.governance(), force=True)
    
    if strat.paused():
        strat.unpause({"from": strat_gov})

    ## Earn
    vault_proxy.earn({"from": governance})
    assert vault_proxy.balance() == prev_balance

    ## Harvest
    strat.harvest({"from": governance})
    assert vault_proxy.getPricePerFullShare() >= prev_getPricePerFullShare  ## Not super happy about >= but it breaks for emitting

    ## Send funds to test
    multi = accounts.at(vault_proxy.MULTISIG(), force=True)
    ## Gas
    a[0].transfer(to=multi, amount=a[0].balance())
    ## Send the shares to governance for testing
    vault_proxy.transfer(governance, vault_proxy.balanceOf(multi), {"from": multi})

    ## Withdraw
    underlying = ERC20Upgradeable.at(vault_proxy.token())
    prev_balance_of_underlying = underlying.balanceOf(governance)
    vault_proxy.withdraw(1000, {"from": governance})
    assert underlying.balanceOf(governance) > prev_balance_of_underlying 


    ## WithdrawAll
    prev_balance_of_underlying = underlying.balanceOf(governance)
    vault_proxy.withdrawAll({"from": governance})
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






