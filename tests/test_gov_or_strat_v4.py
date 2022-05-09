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

BADGER = "0x3472A5A71965499acd81997a54BBA8D852C6E53d"
BADGER_WHALE = "0x34e2741a3F8483dBe5231F61C005110ff4B9F50A"

BVECVX = "0xfd05D3C7fe2924020620A8bE4961bBaA747e6305"
BIBTC_SBTC = "0xaE96fF08771a109dc6650a1BdCa62F2d558E40af"
BBADGER_WBTC_CRV = "0xeC1c717A3b02582A4Aa2275260C583095536b613"
BBVECVX_CVX = "0x937B8E917d0F36eDEBBA8E459C5FB16F3b315551"
BCVXCRV = "0x2B5455aac8d64C14786c3a29858E43b5945819C0"
TRICRYPTO2 = "0x27E98fC7d05f54E544d16F58C194C2D7ba71e3B5"

BVECVX_WHALE = "0x48D93dabF29Aa5d86424A90eE60F419f1837649F"
BIBTC_SBTC_WHALE = "0x3BD517f6d564aC5793d0cb2358d1a03054c00fc8"
BBADGER_WBTC_CRV_WHALE = "0x855c4dCa95adB9cE63f09B9899882C50aD9cfc8F"
BBVECVX_CVX_WHALE = "0x6Db65261a4Fc3F88E60B7470e9b38Db0B22E785C"
BCVXCRV_WHALE = "0xa58AEf2608a4C1d687F2E85a8C45d8fd5C720e37"
TRICRYPTO2_WHALE = "0xaAF5feaa9e5694B2b293e67558e2dA8EA4B1FB13"

TECH_OPS = "0x86cbD0ce0c087b482782c181dA8d191De18C8275"

SETT_ADDRESSES = [
    BVECVX,
    BIBTC_SBTC,
    BBADGER_WBTC_CRV,
    BBVECVX_CVX,
    BCVXCRV,
    TRICRYPTO2,
]

WHALE_ADDRESSES = [
    BVECVX_WHALE,
    BIBTC_SBTC_WHALE,
    BBADGER_WBTC_CRV_WHALE,
    BBVECVX_CVX_WHALE,
    BCVXCRV_WHALE,
    TRICRYPTO2_WHALE,
]


@pytest.mark.parametrize(
    "sett_address,whale_address",
    [(sett, whale) for sett, whale in zip(SETT_ADDRESSES, WHALE_ADDRESSES)],
)
def test_upgrade_and_approve_access(
    sett_address,
    whale_address,
    proxy_admin,
    proxy_admin_gov,
    bve_cvx,
    bcvx_crv,
    tech_ops,
):
    vault_proxy = SettV4h.at(sett_address)

    prev_gov = vault_proxy.governance()
    prev_guardian = vault_proxy.guardian()

    governance = accounts.at(prev_gov, force=True)
    guardian = accounts.at(prev_guardian, force=True)
    whale = accounts.at(whale_address, force=True)

    vault_proxy.setStrategist(TECH_OPS, {"from": governance})
    prev_strategist = vault_proxy.strategist()
    strategist = accounts.at(prev_strategist, force=True)

    with brownie.reverts():
        ## Still onlyGovernance, should revert from strategist
        vault_proxy.approveContractAccess(prev_gov, {"from": strategist})

    ## Setting rest of variables, we'll use them later
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
    assert vault_proxy.version() == "1.4h - Hack Amended"  ## It is different
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
    assert TECH_OPS == vault_proxy.strategist()

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

    ## Verify that unpausing allows to earn
    gac = interface.IGac(vault_proxy.GAC())
    gac_gov = accounts.at(gac.DEV_MULTISIG(), force=True)

    vault_proxy.pause({"from": governance})  ## Now you can pause
    vault_proxy.unpause({"from": governance})  ## Let's unpause to test transferFrom

    with brownie.reverts():
        vault_proxy.pause({"from": accounts[0]})  ## Not everyone can pause

    assert vault_proxy.paused() == False  ## Vaults are currently unpaused

    vault_proxy.pause({"from": guardian})
    assert vault_proxy.paused() == True

    vault_proxy.unpause({"from": governance})
    assert vault_proxy.paused() == False

    ## Generic operations
    ## Let's run some operations now that we have funds
    controller = interface.IController(vault_proxy.controller())
    strat = interface.IStrategy(controller.strategies(vault_proxy.token()))
    strat_gov = accounts.at(strat.governance(), force=True)

    if strat.paused():
        strat.unpause({"from": strat_gov})

    ## Harvest
    strat.harvest({"from": governance})
    assert (
        vault_proxy.getPricePerFullShare() >= prev_getPricePerFullShare
    )  ## Not super happy about >= but it breaks for emitting

    ## Send funds to test
    ## Gas
    a[0].transfer(to=whale, amount=a[0].balance())
    ## Send the shares to governance for testing
    vault_proxy.transfer(governance, vault_proxy.balanceOf(whale), {"from": whale})

    ## Withdraw
    underlying = ERC20Upgradeable.at(vault_proxy.token())
    prev_balance_of_underlying = underlying.balanceOf(governance)
    vault_proxy.withdraw(10000, {"from": governance})
    assert underlying.balanceOf(governance) > prev_balance_of_underlying

    ## NOTE: I've deleted withdrawAll as it was reverting for bveCVX
    ## NOTE: withdrawAll is just balanceOf() -> _withdraw so there shouldn't be any different security profile in it

    ## Deposit
    prev_shares = vault_proxy.balanceOf(governance)
    prev_balance_of_underlying = underlying.balanceOf(governance)
    underlying.approve(
        vault_proxy, underlying.balanceOf(governance), {"from": governance}
    )
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
    amount = vault_proxy.balanceOf(governance) / 4
    vault_proxy.approve(rando, vault_proxy.balanceOf(governance), {"from": governance})
    vault_proxy.transferFrom(governance.address, rando.address, amount, {"from": rando})
    assert vault_proxy.balanceOf(rando.address) == amount

    # Globally disable transferFrom
    gac.disableTransferFrom({"from": gac_gov})
    with brownie.reverts("transferFrom: GAC transferFromDisabled"):
        vault_proxy.transferFrom(
            governance.address, rando.address, amount, {"from": rando}
        )

    # Transfer
    vault_proxy.transfer(accounts[2], amount, {"from": rando})
    assert vault_proxy.balanceOf(accounts[2]) == amount

    # Approve contract from strategist
    vault_proxy.approveContractAccess(accounts[2], {"from": strategist})
    assert vault_proxy.approved(accounts[2])

    # Revoke contract from strategist
    vault_proxy.revokeContractAccess(accounts[2], {"from": strategist})
    assert not vault_proxy.approved(accounts[2])

    # Sweep
    badger = ERC20Upgradeable.at(BADGER)
    badger_whale = accounts.at(BADGER_WHALE, force=True)
    badger.transfer(vault_proxy, 1000, {"from": badger_whale})
    vault_bal_before = badger.balanceOf(vault_proxy)
    vault_proxy.sweep(BADGER, {"from": governance})
    assert badger.balanceOf(vault_proxy) < vault_bal_before
    assert badger.balanceOf(vault_proxy) == 0

    # again from techops
    badger.transfer(vault_proxy, 1000, {"from": badger_whale})
    vault_bal_before = badger.balanceOf(vault_proxy)
    vault_proxy.sweep(BADGER, {"from": tech_ops})
    assert badger.balanceOf(vault_proxy) < vault_bal_before
    assert badger.balanceOf(vault_proxy) == 0

    # unhappy paths
    with brownie.reverts("onlyGovernanceOrStrategist"):
        vault_proxy.sweep(BADGER, {"from": accounts[0]})

    with brownie.reverts("WANT_TOKEN"):
        vault_proxy.sweep(vault_proxy.token(), {"from": governance})
