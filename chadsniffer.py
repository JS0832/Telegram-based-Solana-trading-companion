import asyncio
from asyncstdlib import enumerate
from solana.rpc.websocket_api import connect
import re

raydium_public_key = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
rpc_wss = "wss://mainnet.helius-rpc.com/?api-key=3e1717e1-bf69-45ae-af63-361e43b78961"
tx_hash_length = 76


# Alternatively, use the client as an infinite asynchronous iterator:
async def main():
    async with connect(rpc_wss) as websocket:
        try:
            await websocket.logs_subscribe()
            first_resp = await websocket.recv()
            subscription_id = first_resp[0].result

            async for idx, msg in enumerate(websocket):
                if "initialize2" in str(msg[0]):
                    start_pos = str(msg[0]).rfind("signature: ") + 11
                    # print(str(msg[0])[start_pos:start_pos+tx_hash_length+14])
                    print(re.findall(r'"([^"]*)"', str(msg[0])[start_pos:start_pos + tx_hash_length + 14])[0])
        except KeyboardInterrupt:
            if websocket:
                await websocket.logs_unsubscribe(subscription_id)


'''
for converting  txn hash to information

def get_tokens(signature: Signature, RaydiumLPV4: Pubkey) -> None:
    transaction = solana_client.get_transaction(
        signature,
        encoding="jsonParsed",
        max_supported_transaction_version=0
    )
    if str(transaction) == "GetTransactionResp(None)":
        pass
    else:
        tx_signature = str(json.loads(str(transaction.to_json()))['result']['transaction']['signatures'][0])
        instructions = get_instructions(transaction)
        filtred_instuctions = instructions_with_program_id(instructions, RaydiumLPV4)
        for instruction in filtred_instuctions:
            tokens = get_tokens_info(instruction)
            append_to_queue(tokens, tx_signature)  # pass the tokens transaction has for adding liquidty event
'''
asyncio.run(main())
