from brownie import accounts, network, config

LOCAL_BLOCKCHAIN_ENVIR = ["development", "ganache-local", "mainnet-fork"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIR:
        return accounts[0]

    return accounts.add(config["wallets"][network.show_active()]["private_address"])
