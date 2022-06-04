from web3 import Web3
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIR, get_account
from brownie import config, network, interface
from scripts.get_weth import get_weth


def main():
    borrow()


def borrow():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    # if network.show_active() in LOCAL_BLOCKCHAIN_ENVIR:
    #     get_weth()

    get_weth()
    lending_pool = get_lending_pool()
    print(f"The lending pool address is {lending_pool.address}")

    # Aprrove our erc20 before sending / depositing
    approve_erc20(
        Web3.toWei(0.1, "ether"), lending_pool.address, erc20_address, account
    )

    tx = lending_pool.deposit(
        erc20_address, Web3.toWei(0.1, "ether"), account.address, 0, {"from": account}
    )
    tx.wait(1)

    (total_collateral_ETH, total_debt_ETH, available_Borrows_ETH) = get_account_data(
        lending_pool, account
    )

    print("lets borrow")

    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )

    amount_dai_to_borrow = (available_Borrows_ETH * 0.95) / dai_eth_price

    print(f"The amount of Dai we can borrow = {amount_dai_to_borrow} Dai")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrwo_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrwo_tx.wait(1)
    print("you have borrowed some dai")

    (total_collateral_ETH, total_debt_ETH, available_Borrows_ETH) = get_account_data(
        lending_pool, account
    )

    repay_all(Web3.toWei(amount_dai_to_borrow, "ether"), lending_pool, account)

    (total_collateral_ETH, total_debt_ETH, available_Borrows_ETH) = get_account_data(
        lending_pool, account
    )


def repay_all(amount, lending_pool, account):
    dai_address = config["networks"][network.show_active()]["dai_token"]
    approve_erc20(amount, lending_pool.address, dai_address, account)
    repay_tx = lending_pool.repay(
        dai_address, amount, 1, account.address, {"from": account}
    )
    repay_tx.wait(1)
    print("everything is repaid")


def get_asset_price(price_feed_address):
    print("getting price")
    price_feed = interface.IAggregator(price_feed_address)
    price = price_feed.latestRoundData()[1]

    return float(Web3.fromWei(price, "ether"))


def get_lending_pool():
    addess_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_address_provider"]
    )
    lending_pool = interface.ILendingPool(addess_provider.getLendingPool())
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    print("approving ERC20...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved")
    return tx


def get_account_data(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account.address)

    total_collateral_ETH = Web3.fromWei(totalCollateralETH, "ether")
    total_debt_ETH = Web3.fromWei(totalDebtETH, "ether")
    available_Borrows_ETH = Web3.fromWei(availableBorrowsETH, "ether")
    print(f"collateral eth = {total_collateral_ETH} eth")
    print(f"debt eth = {total_debt_ETH} eth")
    print(f"available borrows eth = {available_Borrows_ETH} eth")

    return (
        float(total_collateral_ETH),
        float(total_debt_ETH),
        float(available_Borrows_ETH),
    )
