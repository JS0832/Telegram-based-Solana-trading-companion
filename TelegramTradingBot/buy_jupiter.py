import asyncio
import base58
import base64
import json
from solders import message
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from jupiter_python_sdk.jupiter import Jupiter
from caesarcipher import CaesarCipher

async_client = AsyncClient("https://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961")
order_queue = []  # soon will implement this


async def buy_token(token_ca, amount, slippage, e_private_key):
    pkey = CaesarCipher(e_private_key, offset=8)
    private_key = Keypair.from_bytes(base58.b58decode(pkey.decoded))
    jupiter = Jupiter(async_client, private_key)
    converted_amount = int(amount * 10 ** 9)
    print(converted_amount)
    transaction_data = await jupiter.swap(
        input_mint="So11111111111111111111111111111111111111112",
        output_mint=token_ca,
        amount=converted_amount,  # this is the amount of sol used ? ( 0.5 sol each time for now)
        slippage_bps=slippage,
    )
    # Returns str: serialized transactions to execute the swap.
    raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
    signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
    signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
    opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
    result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
    transaction_id = json.loads(result.to_json())['result']

    return f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}"


def purchase_spl_token(token_ca, amount, slippage):
    return asyncio.run(buy_token(token_ca, amount, slippage))
