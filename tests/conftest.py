import pytest
from brownie import config, Wei, Contract

# Snapshots the chain before each test and reverts after test completion.
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# Define relevant tokens and contracts in this section


@pytest.fixture(scope="module")
def token():
    # crvEURT this should be the address of the ERC-20 used by the strategy/vault.
    token_address = "0xFD5dB7463a3aB53fD211b4af195c5BCCC1A03890"
    yield Contract(token_address)


@pytest.fixture(scope="module")
def crv():
    yield Contract("0xD533a949740bb3306d119CC777fa900bA034cd52")


@pytest.fixture(scope="module")
def cvx():
    yield Contract("0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B")


@pytest.fixture(scope="module")
def cvxsETHDeposit():
    yield Contract("0xAF1d4C576bF55f6aE493AEebAcC3a227675e5B98")


@pytest.fixture(scope="module")
def dai():
    yield Contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def rewardsContract():  # this is the sETH pool rewards contract
    yield Contract("0xD814BFC091111E1417a669672144aFFAA081c3CE")


@pytest.fixture(scope="module")
def voter():
    # this is yearn's veCRV voter, where we send all CRV to vote-lock
    yield Contract("0xF147b8125d2ef93FB6965Db97D6746952a133934")


# Define any accounts in this section
@pytest.fixture(scope="module")
def gov(accounts):
    # yearn multisig
    yield accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)


@pytest.fixture(scope="module")
def dudesahn(accounts):
    yield accounts.at("0x8Ef63b525fceF7f8662D98F77f5C9A86ae7dFE09", force=True)


@pytest.fixture(scope="module")
def strategist_ms(accounts):
    # like governance, but better
    yield accounts.at("0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7", force=True)


@pytest.fixture(scope="module")
def new_address(accounts):
    # new account for voter and proxy tests
    yield accounts.at("0xb5DC07e23308ec663E743B1196F5a5569E4E0555", force=True)


@pytest.fixture(scope="module")
def keeper(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def rewards(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def guardian(accounts):
    yield accounts[2]


@pytest.fixture(scope="module")
def management(accounts):
    yield accounts[3]


@pytest.fixture(scope="module")
def strategist(accounts):
    yield accounts.at("0x8Ef63b525fceF7f8662D98F77f5C9A86ae7dFE09", force=True)


@pytest.fixture(scope="module")
def strategist_ms(accounts):
    # like governance, but better
    yield accounts.at("0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7", force=True)


@pytest.fixture(scope="module")
def whale(accounts,token):
    whale = accounts[7]
    gauge = accounts.at("0xe8060Ad8971450E624d5289A10017dD30F5dA85F", force=True)
    token.transfer(whale, 2_000_000e18, {'from':gauge})
    yield whale


@pytest.fixture(scope="module")
def convexWhale(accounts):
    convexWhale = accounts.at("0xC55c7d2816C3a1BCD452493aA99EF11213b0cD3a", force=True)
    yield convexWhale


# this is the live strategy for sETH voter proxy
@pytest.fixture(scope="module")
def curveVoterProxyStrategy():
    yield Contract("0xdD498eB680B0CE6Cac17F7dab0C35Beb6E481a6d")


@pytest.fixture
def vault(pm, token, gov, rewards, guardian):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(token, gov, rewards, "", "", guardian)
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagement(gov, {"from": gov})
    yield vault


@pytest.fixture(scope="function")
def strategy(strategist, keeper, vault, StrategyConvexsETH, gov, curveVoterProxyStrategy, guardian):
    # parameters for this are: strategy, vault, max deposit, minTimePerInvest, slippage protection (10000 = 100% slippage allowed),
    strategy = guardian.deploy(StrategyConvexsETH, vault)
    strategy.setKeeper(keeper, {"from": gov})
    # set management fee to zero so we don't need to worry about this messing up pps
    vault.setManagementFee(0, {"from": gov})
    vault.addStrategy(strategy, 10_000, 0, 2 ** 256 - 1, 1000, {"from": gov})
    strategy.setStrategist(strategist, {"from": gov})
    # we harvest to deploy all funds to this strategy
    strategy.harvest({"from": gov})
    yield strategy
