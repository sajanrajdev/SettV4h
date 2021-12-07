from brownie import *
import pytest

@pytest.fixture
def proxy_admin():
    """
     Verify by doing web3.eth.getStorageAt("STRAT_ADDRESS", int(
        0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103
    )).hex()
    """
    return interface.IProxyAdmin("0x20dce41acca85e8222d6861aa6d23b6c941777bf")


@pytest.fixture
def proxy_admin_gov():
    """
        Also found at proxy_admin.owner()
    """
    return accounts.at("0x21cf9b77f88adf8f8c98d7e33fe601dc57bc0893", force=True)


@pytest.fixture
def bve_cvx():
    """
        Need to unpause for "advanced" vaults
    """
    return SettV4h.at("0xfd05D3C7fe2924020620A8bE4961bBaA747e6305")

@pytest.fixture
def bcvx_crv():
    """
        Need to unpause for "advanced" vaults
    """
    return SettV4h.at("0x2B5455aac8d64C14786c3a29858E43b5945819C0")

## Forces reset before each test
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass