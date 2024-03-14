import asyncio
import base58
import base64
import json
from telebot.async_telebot import AsyncTeleBot, types
import caesarcipher
from solders import message
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from jupiter_python_sdk.jupiter import Jupiter
from caesarcipher import CaesarCipher
import tradingDataBase  # for inserting new positions
import helius_api_key

helius_key = helius_api_key.hel_api_key
async_client = AsyncClient("https://mainnet.helius-rpc.com/?api-key=" + str(helius_key))
order_queue = []  # soon will implement this

TOKEN = "6769248171:AAERXN-athfaM8JtK7kTYfNO6IpfJav7Iug"
bot = AsyncTeleBot(token=TOKEN)


async def buy_token(token_ca, amount, slippage, e_private_key, user_id):
    pkey = CaesarCipher(e_private_key, offset=8).decoded
    private_key = Keypair.from_bytes(base58.b58decode(str(pkey)))
    jupiter = Jupiter(async_client, private_key)
    converted_amount = int(amount * 10 ** 9)
    try:
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
        # in the future check if the transaction is finalised
        await bot.send_message(user_id, f"Transaction sent: https://solscan.io/tx/{transaction_id}")
    except KeyError:
        await bot.send_message(user_id, "Token not Tradable on jupiter")


async def sell_token(token_ca, token_amount, slippage, e_private_key, user_id, token_decimals):
    pkey = CaesarCipher(e_private_key, offset=8).decoded
    private_key = Keypair.from_bytes(base58.b58decode(str(pkey)))
    jupiter = Jupiter(async_client, private_key)
    print(token_amount)
    try:
        transaction_data = await jupiter.swap(
            input_mint=token_ca,
            output_mint="So11111111111111111111111111111111111111112",
            amount=token_amount * 10 ** token_decimals,  # this is the amount of sol used ? ( 0.5 sol each time for now)
            slippage_bps=slippage,
        )
        # Returns str: serialized transactions to execute the swap.
        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
        signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
        result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        transaction_id = json.loads(result.to_json())['result']
        await bot.send_message(user_id, f"Transaction sent: https://solscan.io/tx/{transaction_id}")
    except KeyError:
        await bot.send_message(user_id, "Token not Tradable on jupiter")


async def buy_token_func(token_ca, amount, slippage, e_private_key, user_id):
    asyncio.run(buy_token(token_ca, amount, slippage, e_private_key, user_id))
