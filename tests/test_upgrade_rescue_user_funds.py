import brownie
from brownie import *
import pytest

"""
Tests for Upgrading the "Sett" where the assets were transferred by accident to add 
a sweep() function. 

See issue: https://github.com/Badger-Finance/badger-multisig/issues/318
"""

# ibBTC/wBTC bSLP
# https://etherscan.io/address/0x8a8ffec8f4a0c8c9585da95d9d97e8cd6de273de

SETT_ADDRESSES = [
    "0x8a8FFec8f4A0C8c9585Da95D9D97e8Cd6de273DE"
]

@pytest.mark.parametrize(
    "settAddress",
    SETT_ADDRESSES,
)
def test_upgrade_and_harvest(settAddress, proxy_admin, proxy_admin_gov, bve_cvx, bcvx_crv, bSlp_whale, techOps):
    vault_proxy = SettV1_1h.at(settAddress)

    prev_gov = vault_proxy.governance()

    bve_gov = accounts.at(bve_cvx.governance(), force=True)
    if(bve_cvx.paused()):
        bve_cvx.unpause({"from": bve_gov})
    bcvx_gov = accounts.at(bcvx_crv.governance(), force=True)
    if(bcvx_crv.paused()):
        bcvx_crv.unpause({"from": bcvx_gov})

    governance = accounts.at(prev_gov, force=True)
    ## TODO: Add new code that will revert as it's not there yet
    with brownie.reverts():
        vault_proxy.sweep(vault_proxy.address, {"from": governance}) ## Not yet implemented

    ## Setting all variables, we'll use them later
    prev_available = vault_proxy.available()
    prev_gov = vault_proxy.governance()
    prev_keeper = vault_proxy.keeper()
    prev_token = vault_proxy.token()
    prev_controller = vault_proxy.controller()
    prev_balance = vault_proxy.balance()
    prev_min = vault_proxy.min()
    prev_max = vault_proxy.max()
    prev_getPricePerFullShare = vault_proxy.getPricePerFullShare()

    ## TODO: Add write operations
    new_vault_logic = SettV1_1h.deploy({"from": governance})

    # Deploy new logic
    proxy_admin.upgrade(vault_proxy, new_vault_logic, {"from": proxy_admin_gov})

    ## Checking all variables are as expected
    assert prev_available == vault_proxy.available()
    assert prev_gov == vault_proxy.governance()
    assert prev_keeper == vault_proxy.keeper()
    assert prev_token == vault_proxy.token()
    assert prev_controller == vault_proxy.controller()
    assert prev_balance == vault_proxy.balance()
    assert prev_min == vault_proxy.min()
    assert prev_max == vault_proxy.max()
    assert prev_getPricePerFullShare == vault_proxy.getPricePerFullShare()

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

    ## Gac pausing and disabling transferFrom
    gac = interface.IGac(vault_proxy.GAC())
    gac_gov = accounts.at(gac.DEV_MULTISIG(), force=True)
    gac.pause({"from": gac_gov})
    gac.disableTransferFrom({"from": gac_gov})

    ## GAC
    ## Verify that system still is paused because of GAC
    with brownie.reverts("Pausable: GAC Paused"):
        vault_proxy.earn({"from": governance}) ## You earn if GAC is paused
        ## Quirkiness of the system
        ## To pause a single GAC needs to be unpaused first

    ## Verify that unpausing allows to earn
    gac.unpause({"from": gac_gov})


    ## GAC transferFrom
    ## Verify that unpausing doesn't allow transferFrom because transferFrom is blocked by GAC
    with brownie.reverts("transferFrom: GAC transferFromDisabled"):
        vault_proxy.transferFrom(accounts[0], governance, 123, {"from": governance}) ## Even withou allowance it fails with our error

    ## Verfiy that allowing transferFrom while unpaused allows transferFrom
    gac.enableTransferFrom({"from": gac_gov})

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        vault_proxy.transferFrom(accounts[0], governance, 123, {"from": governance}) ## Now it fails because of allowance

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
    strat.harvest({"from": strat_gov})
    assert vault_proxy.getPricePerFullShare() >= prev_getPricePerFullShare  ## Not super happy about >= but it breaks for emitting

    ## Send funds to test
    ## Gas
    a[0].transfer(to=bSlp_whale, amount=a[0].balance())
    ## Send the shares to governance for testing
    vault_proxy.transfer(governance, vault_proxy.balanceOf(bSlp_whale), {"from": bSlp_whale})

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

    ## Transfer From
    rando = accounts[1]
    amount = vault_proxy.balanceOf(governance)/4
    vault_proxy.approve(rando, vault_proxy.balanceOf(governance), {"from": governance})
    vault_proxy.transferFrom(
        governance.address, 
        rando.address, 
        amount, 
        {"from": rando}
    )
    assert vault_proxy.balanceOf(rando.address) == amount

    # Globally disable transferFrom
    gac.disableTransferFrom({"from": gac_gov})
    with brownie.reverts("transferFrom: GAC transferFromDisabled"):
        vault_proxy.transferFrom(
            governance.address, 
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



    ## Tests new sweep function (Test will only pass until these actions are executed)
    vault_proxy.setStrategist(techOps.address, {"from": governance})
    assert vault_proxy.strategist() == techOps.address

    prev_balance_governance = vault_proxy.balanceOf(governance.address)
    prev_balance_vault = vault_proxy.balanceOf(vault_proxy.address)

    print("Vault's stuck balance: ", prev_balance_vault)
    assert prev_balance_vault == 5267941640682 # Equals to stuck amount

    vault_proxy.sweep(vault_proxy.address, {"from": techOps})

    after_balance_governance = vault_proxy.balanceOf(governance.address)
    after_balance_vault = vault_proxy.balanceOf(vault_proxy.address)

    assert(
        prev_balance_vault - after_balance_vault == after_balance_governance - prev_balance_governance
    )
    assert after_balance_vault == 0  # Sweeps full amount

    # Can't sweep want
    with brownie.reverts("WANT_TOKEN"):
        vault_proxy.sweep(vault_proxy.token(), {"from": governance})



    ## Test change to contract access control

    # rando can't call approveContractAccess
    with brownie.reverts("onlyGovernanceOrStrategist"):
        vault_proxy.approveContractAccess(rando.address, {"from": rando})

    # TechOps can approve and revoke contract access
    vault_proxy.approveContractAccess(accounts[2].address, {"from": techOps})
    assert vault_proxy.approved(accounts[2].address)

    vault_proxy.revokeContractAccess(accounts[2].address, {"from": techOps})
    assert vault_proxy.approved(accounts[2].address) == False

