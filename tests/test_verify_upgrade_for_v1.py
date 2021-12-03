# import brownie
# from brownie import *
# import pytest

# """
# Tests for Upgrading Sett V1 to V4h
# COMPLETE TODO HERE
# """

# # sBTC CRV
# # https://etherscan.io/address/0xd04c48A53c111300aD41190D63681ed3dAd998eC
# # SettV1 -> Need to upgrade to SettV4++

# # bSLP
# # https://etherscan.io/address/0x1862A18181346EBd9EdAf800804f89190DeF24a5
# # SettV1.1

# wBTC / DIGG
# https://etherscan.io/address/0x88128580ACdD9c04Ce47AFcE196875747bF2A9f6
# SettV1.1

# renBTC CRV
# https://etherscan.io/address/0x6dEf55d2e18486B9dDfaA075bc4e4EE0B28c1545
# SettV1

# SETT_ADDRESS = "0xfd05D3C7fe2924020620A8bE4961bBaA747e6305"

# STRAT_ADDRESS = "0x3ff634ce65cDb8CC0D569D6d1697c41aa666cEA9"

# @pytest.fixture
# def vault_proxy():
#     return interface.ISett(SETT_ADDRESS)

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


# def test_upgrade_and_harvest(vault_proxy):
    
#     ## TODO: Add new code that will revert as it's not there yet
#     # with brownie.reverts():
#     #     strat_proxy.CVX_EXTRA_REWARDS()
#     # with brownie.reverts():
#     #     strat_proxy.VOTIUM_BRIBE_CLAIMER()
#     # with brownie.reverts():
#     #     strat_proxy.BRIBES_RECEIVER()

#     ## Setting all variables, we'll use them later
#     prev_strategist = strat_proxy.strategist()
#     prev_gov = strat_proxy.governance()
#     prev_guardian = strat_proxy.guardian()
#     prev_keeper = strat_proxy.keeper()
#     prev_perFeeG = strat_proxy.performanceFeeGovernance()
#     prev_perFeeS = strat_proxy.performanceFeeStrategist()
#     prev_reward = strat_proxy.reward()
#     prev_unit = strat_proxy.uniswap()

#     prev_check_withdrawalSafetyCheck = strat_proxy.withdrawalSafetyCheck()
#     prev_check_harvestOnRebalance = strat_proxy.harvestOnRebalance()
#     prev_check_processLocksOnReinvest = strat_proxy.processLocksOnReinvest()
#     prev_check_processLocksOnRebalance = strat_proxy.processLocksOnRebalance()

#     # Deploy new logic
#     proxy_admin.upgrade(strat_proxy, new_strat_logic, {"from": proxy_admin_gov})

#     gov = accounts.at(strat_proxy.governance(), force=True)


#     ## Checking all variables are as expected
#     assert prev_strategist == strat_proxy.strategist()
#     assert prev_gov == strat_proxy.governance()
#     assert prev_guardian == strat_proxy.guardian()
#     assert prev_keeper == strat_proxy.keeper()
#     assert prev_perFeeG == strat_proxy.performanceFeeGovernance()
#     assert prev_perFeeS == strat_proxy.performanceFeeStrategist()
#     assert prev_reward == strat_proxy.reward()
#     assert prev_unit == strat_proxy.uniswap()

#     ## Checking new variables
#     assert prev_check_withdrawalSafetyCheck == strat_proxy.withdrawalSafetyCheck()
#     assert prev_check_harvestOnRebalance == strat_proxy.harvestOnRebalance()
#     assert prev_check_processLocksOnReinvest == strat_proxy.processLocksOnReinvest()
#     assert prev_check_processLocksOnRebalance == strat_proxy.processLocksOnRebalance()

#     ## Verify new Addresses are setup properly
#     assert strat_proxy.LOCKER() == "0xD18140b4B819b895A3dba5442F959fA44994AF50"
#     assert strat_proxy.CVX_EXTRA_REWARDS() == "0x8Ed4bbf39E3080b35DA84a13A0D1A2FDcE1e0602"
#     assert strat_proxy.VOTIUM_BRIBE_CLAIMER() == "0x378Ba9B73309bE80BF4C2c027aAD799766a7ED5A"
#     assert strat_proxy.BRIBES_RECEIVER() == "0x6F76C6A1059093E21D8B1C13C4e20D8335e2909F"


#     ## Also run all ordinary operation just because
#     with brownie.reverts("no op"):
#         ## Tend successfully fails as we hardcoded a revert
#         strat_proxy.tend({"from": gov})
#     with brownie.reverts("You have to wait for unlock or have to manually rebalance out of it"):
#         ## Withdraw All successfully fails as we are locked
#         controller_proxy.withdrawAll(vault_proxy.token(), {"from": accounts.at(controller_proxy.governance(), force=True)})
#     vault_proxy.earn({"from": gov})

#     ## Harvest should work
#     strat_proxy.harvest({"from": gov})
# © 2021 GitHub, Inc.
# Terms
# Privacy


# def test_upgrade_sett_and_verify_integrity():
#   sett = interface.ISett("0x2B5455aac8d64C14786c3a29858E43b5945819C0")

