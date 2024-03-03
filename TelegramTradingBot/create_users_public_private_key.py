from solana.rpc.api import Client, Keypair
import base58
from caesarcipher import CaesarCipher

client2 = Client("https://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961")


def create_trading_wallet():  # used when the user first subscribes ( or when they wish to change their wallets)
    # Check if the client is connected to the cluster
    if client2:
        print("Connected to Solana cluster.")
    else:
        print("Unable to connect to Solana cluster.")
    new_account = Keypair()
    wallet_address = new_account.pubkey()
    private_key_bytes = new_account.secret()
    public_key_bytes = bytes(new_account.pubkey())
    encoded_keypair2 = private_key_bytes + public_key_bytes
    private_key = base58.b58encode(encoded_keypair2).decode()
    e_private_key = CaesarCipher(str(private_key), offset=8)
    return str(wallet_address), e_private_key.encoded



