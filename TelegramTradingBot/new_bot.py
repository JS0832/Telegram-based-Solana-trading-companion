import math
from time import sleep

import asyncio
from typing import List, AsyncIterator, Tuple
from asyncstdlib import enumerate

from solders.pubkey import Pubkey
from solders.rpc.config import RpcTransactionLogsFilterMentions

from solana.rpc.websocket_api import connect
from solana.rpc.commitment import Finalized
from solana.rpc.api import Client
from solana.exceptions import SolanaRpcException
from websockets.exceptions import ConnectionClosedError, ProtocolError

# Type hinting imports
from solana.rpc.commitment import Commitment
from solana.rpc.websocket_api import SolanaWsClientProtocol
from solders.rpc.responses import RpcLogsResponse, SubscriptionResult, LogsNotification, GetTransactionResp
from solders.signature import Signature
from solders.transaction_status import UiPartiallyDecodedInstruction, ParsedInstruction
import helius_api_key

helius_key = helius_api_key.hel_api_key
# Raydium Liquidity Pool V4
RaydiumLPV4 = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
RaydiumLPV4 = Pubkey.from_string(RaydiumLPV4)
URI = "https://mainnet.helius-rpc.com/?api-key=" + str(helius_key)
WSS = "wss://mainnet.helius-rpc.com/?api-key=" + str(helius_key)
solana_client = Client(URI)
# Radium function call name, look at raydium-amm/program/src/instruction.rs
log_instruction = "initialize2"
# liquidty removed is not accurate so do fix this alter
import threading
# my imports
import time
import telegram
import requests
from requests import request
import json
import subprocess

from helius import BalancesAPI
from helius import TransactionsAPI

transactions_api = TransactionsAPI(helius_key)
balances_api = BalancesAPI(helius_key)  # my private key to the api
# from jsonrpcclient import request, parse, Ok
import solana.transaction

token_queue = []  # [token addy,epoch time,verified previously? (bool)]
past_tokens = []  # all tokens (to not allow replicate)
token_remove_errors = []  # [[token,reason],...]

pinged_tokens = []

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}

tx_queue = []  # this will add transaction quickly to the queue

# for dev wallet tracking

# token adress,inital time(to figure out expiration time),all dev associated wallets,all current wallet balances.


visited_wallets = []  # [token_address,expiration time],[wallet_address,previous checked amount]]   # all wallets that have been visited

ping_queue = []  # tokens to be sent out


async def process_queue():  # performance upgrade
    print("process queue running....")
    while True:
        if len(tx_queue) > 0:
            # always read first element because easy
            var1 = tx_queue[0][0]  # singature
            var2 = tx_queue[0][1]  # raydiumlpv4
            get_tokens(var1, var2)
            tx_queue.pop(0)
        await asyncio.sleep(0.1)


async def main():
    print("listening to new pools....")
    async for websocket in connect(WSS, ping_timeout=None, ping_interval=None):  # maybe tweak this a bit
        try:
            subscription_id = await subscribe_to_logs(
                websocket,
                RpcTransactionLogsFilterMentions(RaydiumLPV4),
                Finalized
            )
            print("subscribed to websocket :" + str(subscription_id))
            async for i, signature in enumerate(process_messages(websocket, log_instruction)):  # type: ignore
                tx_queue.append([signature, RaydiumLPV4])
        except (ProtocolError, ConnectionClosedError, ConnectionResetError) as err:
            print(err)
            continue
        except KeyboardInterrupt:
            if websocket:
                await websocket.logs_unsubscribe(subscription_id)


async def subscribe_to_logs(websocket: SolanaWsClientProtocol,
                            mentions: RpcTransactionLogsFilterMentions,
                            commitment: Commitment) -> int:
    await websocket.logs_subscribe()
    """  filter_=mentions,
        commitment=commitment"""
    first_resp = await websocket.recv()
    return get_subscription_id(first_resp)  # type: ignore


def get_subscription_id(response: SubscriptionResult) -> int:
    return response[0].result


async def process_messages(websocket: SolanaWsClientProtocol,
                           instruction: str) -> AsyncIterator[Signature]:
    """Async generator, main websocket's loop"""
    async for idx, msg in enumerate(websocket):
        value = get_msg_value(msg)
        for log in value.logs:
            if instruction not in log:
                continue
            yield value.signature


def get_msg_value(msg: List[LogsNotification]) -> RpcLogsResponse:
    return msg[0].result.value


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


def get_instructions(
        transaction: GetTransactionResp
):
    instructions = transaction \
        .value \
        .transaction \
        .transaction \
        .message \
        .instructions
    return instructions


def instructions_with_program_id(
        instructions: List[UiPartiallyDecodedInstruction | ParsedInstruction],
        program_id: str
):
    return (instruction for instruction in instructions
            if instruction.program_id == program_id)


def get_tokens_info(
        instruction: UiPartiallyDecodedInstruction | ParsedInstruction
) -> Tuple[Pubkey, Pubkey, Pubkey]:
    accounts = instruction.accounts
    Pair = accounts[4]
    Token0 = accounts[8]
    Token1 = accounts[9]
    return Token0, Token1, Pair


def append_to_queue(tokens: Tuple[Pubkey, Pubkey, Pubkey], tx_sig) -> None:
    if str(tokens[0]) != "So11111111111111111111111111111111111111112":  # don't need this
        if str(tokens[0]) not in past_tokens:
            past_tokens.append(str(tokens[0]))
            token_queue.append(
                [str(tokens[0]), int(time.time()),
                 False, tx_sig, '', 0,
                 0, '', 0, False, 0, 0])
            print(token_queue)


# my token processing logic + telegram stuff
async def token_report():
    while True:
        with open('../errors.txt', 'a') as file:
            error_list_length = len(token_remove_errors)  # length of the list at time of reading (lowerbound)
            for item in token_remove_errors:
                file.write(str(item) + '\n')
            # remove the items that where appended from the list just now
            del token_remove_errors[0:error_list_length]
        await asyncio.sleep(300)


async def append_past_tokens_to_file():
    while True:
        # dump tokens to file
        temp_array = []
        with open("../past_tokens.txt") as file_in:  # read past tokens to not over write
            for line in file_in:
                token = str(line).strip()
                temp_array.append(token)  # add the already checked token to the list to not give a false alarm
                # this may be changed depending on how I fetch the api data in the future
        with open('../past_tokens.txt', 'a') as file:
            for item in past_tokens:
                if item not in temp_array:
                    file.write(str(item) + '\n')
        await asyncio.sleep(30)


async def tokenomics_followup():
    "[[full token array passed here,followup count,].....]"
    while True:
        if len(pinged_tokens) > 0:
            i = 0
            for pinged_token in pinged_tokens:
                if pinged_token[1] < 3:

                    # grabs distribution info
                    # add dev selling report here too:
                    token_address = pinged_token[0][0]
                    holder_result = request('GET',
                                            "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                                token_address) + "&limit=13&offset=0",
                                            headers=solscan_header)
                    holder_list = holder_result.json()
                    five_or_above = 0  # number of holders that have 5%+
                    total_supply_held = 0  # amount fo supply top 10 holders hold
                    amount_of_coins_for_five_percent = \
                        int(float(pinged_token[0][10]) * float(0.05))
                    # total supply * 0.05 then convert to int
                    supply = pinged_token[0][10]
                    total_held_string = ""
                    five_above_string = ""
                    if "total" in holder_list:
                        if int(holder_list["total"]) > 12:
                            iterator = 0
                            for holder in holder_list["data"]:
                                if iterator > 12:
                                    break
                                if str(holder[
                                           "owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # raydium pool
                                    if int(float(holder["amount"]) / float(
                                            10 ** int(pinged_token[0][11]))) >= amount_of_coins_for_five_percent:
                                        five_or_above += 1
                                    total_supply_held += int(float(holder["amount"]) / float(10 ** pinged_token[0][11]))
                                iterator += 1
                        if int(float(total_supply_held / supply) * float(100)) < 20:  # safu
                            total_held_string = "Excellent : " + str(
                                int(float(total_supply_held / supply) * float(100)))
                        elif 40 > int(float(total_supply_held / supply) * float(100)) > 20:  # moderate risk
                            total_held_string = "Moderate : " + str(
                                int(float(total_supply_held / supply) * float(100)))
                        else:  # high risk
                            total_held_string = "Poor : " + str(
                                int(float(total_supply_held / supply) * float(100)))
                    try:
                        # send info to telegram
                        bot = telegram.Bot(token='6405793513:AAEPOCPP022SkJlg6iYI-RgSHJ9AZOaoQy4')
                        await bot.sendMessage(chat_id="-4129157033",
                                              text="Token Follow-up: \n " + str(pinged_token[0][0] + "\n total held by "
                                                                                                     "top 10: " + str(
                                                  total_held_string) + "\n number of wallets 5%+ : " + str(
                                                  five_or_above)))
                    except Exception as e:
                        print("Unable to send: ", e)
                    time.sleep(3)
                    pinged_token[1] += 1  # increase follow-up count
                else:
                    pinged_tokens.pop(i)
                i += 1
        await asyncio.sleep(300)  # every 5 minutes


def check_dev_wallets(txn_hash, token_supp, token_add):
    # [token_address,expiration time],[wallet_address,previous checked amount]]
    visited_wallets.clear()
    visited_wallets.append([token_add, time.time(), token_supp])
    # stack
    token_supply = token_supp
    amount_sold = 0
    wallet_stack = []  # wallets to be checked
    token_addrres = token_add
    root = check_mint_wallet(txn_hash, token_supp, token_add)
    if root == "":
        print("error not supported")
        return "unconventional root."
        # check_mint_wallet(txn_hash) (until fixed set root to be something else)
    wallet_stack.append(root)  # stack begins from the root wallet
    while True:
        if len(wallet_stack) > 0:  # given the stack is not empty we know there is more to be traversed
            temp_wallet = str(
                wallet_stack.pop())  # remove the top item from the stack and it becomes the next wallet of interest
            print("checking : " + str(temp_wallet))
            # add corresponding balance
            while True:
                try:
                    balances = balances_api.get_balances(temp_wallet)
                    spl_balance = balances["tokens"]
                    break
                except ValueError:
                    continue
            for token in spl_balance:
                if str(token["mint"]) == token_addrres:
                    visited_wallets.append(
                        ([temp_wallet, int(float(token["amount"])) / 10 ** float(token["decimals"])]))  # normalise
            time.sleep(0.1)
            tries = 0
            while True:
                try:
                    all_spl_tx = request('GET',
                                         "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                                             temp_wallet) + "&limit=" + str(10) + "&offset=0",
                                         headers=solscan_header)  # query all spl token transactions
                    spl_transfers = all_spl_tx.json()["data"]  # all spl transfers in this current wallet
                    break
                except ValueError:
                    if tries > 5:
                        break
                    tries += 1
                    print("solscan error2")

            for spl_transfer in spl_transfers:  # loop over all transaction per give wallet
                if int(spl_transfer["changeAmount"]) < 0 and str(spl_transfer["tokenAddress"]) == token_addrres:
                    temp_hash = str(spl_transfer["signature"][0])
                    time.sleep(0.2)
                    tx_info = request('GET',
                                      "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                          temp_hash),
                                      headers=solscan_header)
                    time.sleep(0.1)
                    tx_json = tx_info.json()
                    if "raydiumTransactions" in tx_json:
                        if len(tx_json["raydiumTransactions"]) > 0:
                            if str(tx_json["raydiumTransactions"][0]["swap"]["event"][0][
                                       "sourceOwner"]) == temp_wallet and str(
                                tx_json["raydiumTransactions"][0]["swap"]["event"][0][
                                    "destinationOwner"]) == "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                                amount_sold += int(
                                    float(tx_json["raydiumTransactions"][0]["swap"]["event"][0]["amount"]) / float(
                                        10) ** float(
                                        tx_json["raydiumTransactions"][0]["swap"]["event"][0]["decimals"]))
                    for tx_items in tx_json["tokenTransfers"]:
                        if str(tx_items["token"]["address"]) == token_addrres:
                            print(temp_wallet)
                            if str(tx_items["destination_owner"]) not in visited_wallets:  # seen before?
                                wallet_stack.append(str(tx_items["destination_owner"]))
        else:
            break  # done
    return str(float(amount_sold) / float(token_supply) * float(100)) + " %"


async def poll_dev_wallet_activity():  # make it for one ping atm
    expiration_time = 1800
    while True:
        # [[token_address,time],[wallet_address,previous checked amount]]
        index = 0  # start from the second item
        if len(visited_wallets) > 0:
            token_supply = visited_wallets[0][2]
            if int(time.time()) - visited_wallets[0][1] > expiration_time:
                visited_wallets.clear()
            else:
                token_addrres = visited_wallets[0][0]
                # by the current convention the first item will be the address of the token
                for wallet in visited_wallets:
                    if index == 0:
                        index += 1
                        continue  # move to the next item as the first item is the token address
                    try:
                        balances = balances_api.get_balances(wallet[0])
                        spl_balance = balances["tokens"]
                        break
                    except ValueError:
                        print("error checking again.")
                        continue
                    for token in spl_balance:
                        if str(token["mint"]) == token_addrres:
                            if int(float(token["amount"])) / 10 ** float(token["decimals"]) < visited_wallets[index][
                                1]:  # reduction(movement)
                                try:
                                    # send info to telegram
                                    bot = telegram.Bot(token='6405793513:AAEPOCPP022SkJlg6iYI-RgSHJ9AZOaoQy4')
                                    await bot.sendMessage(chat_id="-4129157033",
                                                          text="Dev sold! - " + str(float(
                                                              visited_wallets[index][1] - int(
                                                                  float(token["amount"])) / 10 ** float(
                                                                  token["decimals"])) / float(
                                                              token_supply) * float(100)))
                                except Exception as e:
                                    print("Unable to send: ", e)
                                time.sleep(2)
                                visited_wallets[index][1] = int(float(token["amount"])) / 10 ** float(token["decimals"])
                    index += 1
        await asyncio.sleep(5)  # just for one buy order now


def check_mint_wallet(liquidty_add_txn_hash, token_supp, token_add):
    token_addrres = token_add
    token_supply = token_supp
    # determine the address of the liquidty provider
    signer_address = ""  # signer of the lp addition
    liquidity_tx_info = request('GET',
                                "https://pro-api.solscan.io/v1.0/transaction/" + str(
                                    liquidty_add_txn_hash),
                                headers=solscan_header)

    liquidity_tx_info_json = liquidity_tx_info.json()
    # check for signer
    signer = str(liquidity_tx_info_json["signer"][0])
    tx_count_check = request('GET',
                             "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" +
                             signer + "&limit=1&offset=0",
                             headers=solscan_header)  # will know how many to query
    spl_tx_count = tx_count_check.json()["total"]
    all_spl_tx = request('GET',
                         "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                             signer) + "&limit=" + str(spl_tx_count) + "&offset=0",
                         headers=solscan_header)  # will know how many to query
    spl_transfers = all_spl_tx.json()
    for spl_tx in spl_transfers["data"]:
        if str(spl_tx["changeType"]) == "inc":
            if int(float(int(spl_tx["changeAmount"])) / float(10 ** int(spl_tx["decimals"]))) == token_supply and str(
                    spl_tx["tokenAddress"]) == token_addrres:
                return str(signer)
                # the signer is the mint account(root wallet)
    return ""  # if it doesn't find it (soon upgrade)


# possibly also mak a queue and if the token has been sniped by devs then just reject the token
#  [[token_address,checked=true/flase,passed=true or false,supply]]
large_holder_check_queue = []

removed_tokens_queue = []  # here I will just place any token that has very bad results


class StopSniperCheck(Exception):
    pass


bots_wallet_balcklist = []
special_token_queue = []  # special discarded tokens are placed here for another round of checking timed release tokens)


# large_holder_check_queue.append([token[0],False,False,token[10],True])
def check_for_large_holder():  # here maybe mostly focus on wallets with a low tx count too?(not accurate since not many holders checked)
    while True:
        if len(large_holder_check_queue) > 0:
            index = 0
            for item in large_holder_check_queue:
                if not item[1]:  # not checked yet
                    print("checking token for large cumulative holder: " + str(item[0]))
                    token_address = item[0]
                    token_supp = item[3]
                    holders = []
                    holder_result = request('GET',
                                            "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                                token_address) + "&limit=13&offset=0",
                                            headers=solscan_header)
                    holder_list = holder_result.json()
                    # if "total" in holder_list: #removed this as it missed good tokens by sometimes ignoring a low
                    # holder count if int(holder_list["total"]) > 10:
                    iterator = 0
                    for holder in holder_list["data"]:
                        if iterator > 4:
                            break
                        if str(holder[
                                   "owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # radium pool
                            holders.append(str(holder["owner"]))
                        iterator += 1
                    # else:
                    # item[2] = False  # fail it as there is very little holders
                    # break
                    all_seen_wallets = []  # helps to avoid double seen wallets when some holder is actually linked
                    # to another holder
                    token_addy = token_address
                    token_supply = token_supp
                    true_supply_held_by_top_twenty = []  # this list will show true token holdings by the top 20 holders
                    try:
                        for holder in holders:
                            still_in_queue = False
                            for temp_item in large_holder_check_queue:  # check if it was removed
                                if temp_item[0] == token_address:
                                    still_in_queue = True
                                    break
                            if not still_in_queue:
                                print("Token removed....halting sniper check")
                                raise StopSniperCheck  # stop as not queue
                            max_val = 70  # this is the danger zone of very high odds snipe
                            if any(val >= max_val for val in true_supply_held_by_top_twenty):#stoping search prematurely
                                print("Token removed....halting sniper check")
                                raise StopSniperCheck  # stop as not queue
                            if holder not in all_seen_wallets and holder not in bots_wallet_balcklist:
                                print("checking holder: " + str(holder))
                                temp_associated_wallets = []  # for each holder checked (stack)
                                root = holder
                                temp_associated_wallets.append(root)
                                all_seen_wallets.append(root)
                                temp_total_spl_balance = 0
                                while True:  # here traverse all wallets connected to one wallet and count the total
                                    if len(temp_associated_wallets) > 11:  # not good
                                        true_supply_held_by_top_twenty.append(100)  # we don't want this token
                                        raise StopSniperCheck  # too many
                                    # supply holding.
                                    if len(temp_associated_wallets) > 0:  # means there is more to check
                                        temp_wallet = temp_associated_wallets.pop()
                                        try:
                                            balances = balances_api.get_balances(temp_wallet)
                                        except ValueError:
                                            bots_wallet_balcklist.append(
                                                temp_wallet)  # to ignore solana bots that have insane amount of
                                            # shitcoins in them
                                            print("error reading address...ignoring the wallet: " + str(temp_wallet))
                                            continue
                                        spl_balance = balances["tokens"]
                                        for token in spl_balance:
                                            if str(token["mint"]) == token_addy:
                                                temp_total_spl_balance += int(float(token["amount"])) / 10 ** float(
                                                    token["decimals"])
                                        tx_count = 8
                                        while True:
                                            try:
                                                res = solana_client.get_signatures_for_address(
                                                    Pubkey.from_string(temp_wallet),
                                                    limit=tx_count  # Specify how much last transactions to fetch
                                                )
                                                break
                                            except solana.exceptions.SolanaRpcException:
                                                tx_count = tx_count - 2  # decrement until we get to allowable amount
                                            if tx_count == 0:
                                                break
                                        if tx_count == 0:
                                            break
                                        transactions = json.loads(str(res.to_json()))["result"]
                                        for spl_transfer in transactions:  # loop over all transaction per give wallet
                                            try:
                                                parsed_transactions = transactions_api.get_parsed_transactions(
                                                    transactions=[spl_transfer["signature"]])
                                            except ValueError:
                                                print("error reading a spl transfer: " + str(spl_transfer))
                                                break
                                            if len(parsed_transactions) > 0:
                                                if "tokenTransfers" in parsed_transactions[0]:
                                                    if len(parsed_transactions[0]["tokenTransfers"]) > 0:
                                                        for tx_items in parsed_transactions[0]["tokenTransfers"]:
                                                            if str(tx_items["mint"]) == token_addy:
                                                                if str(tx_items["toUserAccount"]) == temp_wallet:
                                                                    if str(tx_items[
                                                                               "fromUserAccount"]) not in all_seen_wallets and str(
                                                                        tx_items["fromUserAccount"]) != "":
                                                                        if str(tx_items[
                                                                                   "fromUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                                                                            temp_associated_wallets.append(
                                                                                str(tx_items["fromUserAccount"]))
                                                                elif str(tx_items["fromUserAccount"]) == temp_wallet:
                                                                    if str(tx_items[
                                                                               "toUserAccount"]) not in all_seen_wallets and str(
                                                                        tx_items["toUserAccount"]) != "":
                                                                        if str(tx_items[
                                                                                   "toUserAccount"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                                                                            temp_associated_wallets.append(
                                                                                str(tx_items["toUserAccount"]))
                                                else:
                                                    print("strange error wallet: " + str(temp_wallet))
                                        all_seen_wallets.append(
                                            temp_wallet)  # add the traversed wallet to all see wallets

                                    else:
                                        percentage = float(temp_total_spl_balance) / float(token_supply) * float(100)
                                        true_supply_held_by_top_twenty.append(percentage)  # convert it as a percentage
                                        break  # done
                    except StopSniperCheck:
                        print("one wallet tied to many other wallets stopping reading....")
                    still_in_queue = False
                    for temp_item in large_holder_check_queue:  # check if it was removed
                        if temp_item[0] == token_address:
                            still_in_queue = True
                            break
                    if still_in_queue:
                        item[1] = True  # set as checked
                        if len(true_supply_held_by_top_twenty) == 0:
                            large_holder_check_queue.pop(index)
                        elif len(true_supply_held_by_top_twenty) == 1 and token_address not in special_token_queue:  # only dev holding means this is a pre-launch,if token adress is in the list we know its been checked no again so can be processed as normal coin
                            # token(timed token) so we will add more time to its expiration time (1h)
                            for token in token_queue:
                                if token[0] == token_address:
                                    print("Added a time extension to token: " + str(token_address))
                                    token[1] += 3600  # adding an hour to the epoch
                                    temp_counter = 0
                                    for temp_item in large_holder_check_queue:
                                        if temp_item[0] == token_address:
                                            large_holder_check_queue.pop(temp_counter)
                                            break
                                        temp_counter += 1
                        else:
                            max_val = 70  # this is the danger zone of very high odds snipe
                            if any(val >= max_val for val in true_supply_held_by_top_twenty):
                                item[2] = False  # failed
                                removed_tokens_queue.append(item[0])  # add address
                            else:
                                item[2] = True  # passed
                                item[5] = max(true_supply_held_by_top_twenty)
                            print("for token: " + str(token_address) + " " + str(true_supply_held_by_top_twenty))
                index += 1
        time.sleep(0.2)


class TokenError(Exception):  # helps to exist deeply nested loops
    pass


async def verify_token():  # figure out how to make this async (needs to be async) ( for now concurrent)
    print("Executing token verification thread....")
    token_expiration_time = 2400  # 40 minutes in seconds
    inital_checks_expiration_time = 900  # 15 minutes for initial checks
    minimum_token_sent_to_lp_percent = 80
    decimals = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18}  # a list of allowable decimal amount
    rpc_url = "https://mainnet.helius-rpc.com/?api-key=" + str(helius_key)
    spl_executable = r'C:\\Users\MEMEdev\.local\share\solana\install\active_release\bin\spl-token.exe'  # for
    # checking mint
    special_meta_key = ["bafkrei", "mypinata", "ipfs.nftstorage.link"]  # for now, it will use this
    minimum_initial_liquidty = 5  # most good coins have 10
    while True:  # infinite loop to keep checking
        index = 0
        for token in token_queue:
            img_uri = ""  # blank as we are looking at next token
            if int(time.time()) - token[1] > token_expiration_time:  # check if the token is expired
                token_remove_errors.append(["removed token since it's expiration time has passed ", token[0]])
                print("removed token since it's expiration time has passed " + str(token[0]))
                temp = 0
                for item in large_holder_check_queue:
                    if item[0] == token[0]:
                        large_holder_check_queue.pop(temp)
                        break
                    temp += 1
                token_queue.pop(index)  # remove the token from the queue as its expired
                continue
            else:
                if token[0] in removed_tokens_queue:
                    print("removed token due to a bad holder result: " + str(token[0]))
                    token_queue.pop(index)  # remove the token from the queue as its expired
                    continue
                # here also check if the token has not passed the initial checks after first 25 min then remove it
                # because most likely rugged by now
                if int(time.time()) - token[1] > inital_checks_expiration_time and not token[2]:  # 15 minutes passed
                    # but not verified
                    token_remove_errors.append(
                        ["removed token since its initial checks aren't still validated ", token[0]])
                    print("removed token since its initial checks aren't still validated ", token[0])
                    temp = 0
                    for item in large_holder_check_queue:
                        if item[0] == token[0]:
                            large_holder_check_queue.pop(temp)
                            break
                        temp += 1
                    token_queue.pop(index)  # remove the token from the queue as its expired
                    continue
                if not token[2]:  # a boolean to save on api calls
                    if token[10] == 0:  # (used to wait for image uri to update)
                        token_amount_sent_to_lp_pool = 0  # to keep track how many tokens are sent to the pool
                        # check if mintable:
                        contract_address = token[0]
                        command = [spl_executable, "display", contract_address, "-u", rpc_url]
                        result = subprocess.run(command, capture_output=True, text=True, shell=True)
                        # Output the result
                        if result.returncode == 0:
                            if "Mint authority: (not set)" in str(result.stdout):
                                token[9] = True  # confirms that mint authority set to none
                        else:
                            token_remove_errors.append(
                                ["Command failed 2 ", token[0]])
                            print("error2 " + str(result.stderr))
                            temp = 0
                            for item in large_holder_check_queue:
                                if item[0] == token[0]:
                                    large_holder_check_queue.pop(temp)
                                    break
                                temp += 1
                            token_queue.pop(index)
                            continue

                        alchemy_url = "https://solana-mainnet.g.alchemy.com/v2/bzkveugN6acIccgGUJTetb95Sz0yo8W_"
                        payload = {
                            "id": 1,
                            "jsonrpc": "2.0",
                            "method": "getTokenSupply",
                            "params": [token[0]]
                        }
                        alchemy_headers = {
                            "accept": "application/json",
                            "content-type": "application/json"
                        }
                        get_supply_response = requests.post(alchemy_url, json=payload, headers=alchemy_headers)
                        token[10] = int(float(get_supply_response.json()["result"]['value']["uiAmountString"]))
                        token[11] = int(get_supply_response.json()["result"]['value']["decimals"])
                    tx_hash = str(token[3])
                    result = request('GET', "https://pro-api.solscan.io/v1.0/transaction/" + tx_hash,
                                     headers=solscan_header)
                    transaction = result.json()
                    mint = ''  # the lp token address
                    amount = 0  # lp token amount
                    initial_sol_amount = 0
                    if 'innerInstructions' in transaction:  # if success (need to fix)
                        try:
                            for tx in transaction['innerInstructions'][0]['parsedInstructions']:
                                try:
                                    if 'extra' in tx:
                                        if str(tx['extra'][
                                                   'tokenAddress']) == "So11111111111111111111111111111111111111112" and str(
                                            tx['extra'][
                                                'destinationOwner']) == "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # raydium authority
                                            initial_sol_amount = int(int(tx['extra']['amount']) / 1000000000)
                                        if str(tx['extra'][
                                                   'tokenAddress']) == str(
                                            token[0]):  # find how many coins sent to lp pool
                                            token_amount_sent_to_lp_pool = \
                                                int(int(tx['extra']['amount']) / 10 ** token[11])
                                except Exception as e:
                                    print("error " + str(e))
                        except IndexError:
                            print("error retrying....")
                            token_remove_errors.append(
                                ["error retrying....", token[0]])
                            continue  # move to the next token as this one might need more time to be read from solscan.
                        if token_amount_sent_to_lp_pool == 0:
                            print("removed token due to very low amount of  tokens sent to lp pool " + str(token[0]))
                            token_remove_errors.append(
                                ["removed token due to very low amount of  tokens sent to lp pool ", token[0]])
                            token_queue.pop(index)
                            continue
                        if (int((float(token_amount_sent_to_lp_pool) / float(token[10])) * float(100)) <
                                minimum_token_sent_to_lp_percent):
                            print("removed token due to low token ratio added to the lp pool: " + str(
                                int((float(token_amount_sent_to_lp_pool) / float(token[10])) * float(
                                    100))) + " token address:" + str(token[0]))
                            token_remove_errors.append(
                                ["removed token due to low token ratio added to the lp pool:  ", token[0]])
                            token_queue.pop(index)
                            continue
                        else:
                            token[8] = int((float(token_amount_sent_to_lp_pool) / float(token[10])) * float(100))
                        if initial_sol_amount < minimum_initial_liquidty:
                            # token started with low "liquidty" meaning it's a shitcoin
                            print("removed token due to low initial liquidity " + str(token[0]))
                            token_remove_errors.append(
                                ["removed token due to low initial liquidity :  ", token[0]])
                            token_queue.pop(index)
                            continue
                        else:
                            token[6] = initial_sol_amount
                        for tx in transaction['innerInstructions'][0]['parsedInstructions']:
                            if 'program' in tx and 'type' in tx and 'name' in tx:
                                if str(tx['type']) == "mintTo" and str(tx['type']) == "mintTo":
                                    mint = str(tx['params']['mint'])
                                    amount = int(tx['params']['amount'])
                        token[4] = mint
                        token[5] = amount
                        # no data regarding the token meaning liquidty removed
                    else:  # failed probably
                        # error try again
                        print("error retrying....")
                        token_remove_errors.append(
                            ["error retrying....", token[0]])
                    #  [[token_address,checked=true/false,passed=true or false,supply,checked on time?]]
                    found = False
                    for item in large_holder_check_queue:
                        if item[0] == token[0]:
                            found = True
                    if not found:
                        large_holder_check_queue.append([token[0], False, False, token[10], "True", 0])
                        print(large_holder_check_queue)
                if token[11] in decimals or token[2]:
                    # i can check if dev removed liquidity too then I removed the token from queue
                    token[2] = True  # sets to true in case it is its first run
                    if not token[9]:  # if mint hasn't been disabled then check again if the dev disabled it
                        # check if mintable:
                        contract_address = token[0]
                        command = [spl_executable, "display", contract_address, "-u", rpc_url]
                        result = subprocess.run(command, capture_output=True, text=True, shell=True)
                        # Output the result
                        if result.returncode == 0:
                            if "Mint authority: (not set)" in str(result.stdout):
                                token[9] = True  # confirms that mint authority set to none
                                print("token mint has been disabled. " + str(token[0]))
                        else:
                            print("Command failed.")
                            print("Error:", result.stderr)
                    if token[9]:  # if mint disabled
                        # check if the lp token has been burned
                        if token[7] == "":  # means if the owner of the lp token has not been found yet
                            lq_token = str(token[4])
                            result_holder_list = request('GET',
                                                         "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" +
                                                         lq_token + "&limit=10&offset=0",
                                                         headers=solscan_header)
                            lp_holder = result_holder_list.json()
                            if "data" in lp_holder:
                                if str(lp_holder["total"]) == "1":
                                    token[7] = str(lp_holder["data"][0]["owner"])
                                elif int(lp_holder["total"]) > 1:
                                    print("error more than lp one Holder " + str(token[0]))
                                    token_remove_errors.append(
                                        ["error more than lp one Holder ....", token[0]])
                                    temp = 0
                                    for item in large_holder_check_queue:
                                        if item[0] == token[0]:
                                            large_holder_check_queue.pop(temp)
                                            break
                                        temp += 1
                                    token_queue.pop(index)
                                    continue
                            else:
                                print("error fetching lp token holder data " + str(token[0]))
                                token_remove_errors.append(
                                    ["error fetching lp token holder data ", token[0]])
                                temp = 0
                                for item in large_holder_check_queue:
                                    if item[0] == token[0]:
                                        large_holder_check_queue.pop(temp)
                                        break
                                    temp += 1
                                token_queue.pop(index)
                                continue
                        tx_result = request('GET',
                                            "https://pro-api.solscan.io/v1.0/account/splTransfers?account=" + str(
                                                token[7]) + "&limit=10&offset=0",
                                            headers=solscan_header)
                        tx_list = tx_result.json()
                        try:
                            if "data" in tx_list:
                                for user_tx in tx_list["data"]:
                                    if str(user_tx['changeType']) == "closedAccount":
                                        # check the tx hash
                                        signature = str(user_tx["signature"][0])
                                        burn_tx = request('GET',
                                                          "https://pro-api.solscan.io/v1.0/transaction/" + signature,
                                                          headers=solscan_header)
                                        json_burn_tx = burn_tx.json()
                                        for meta_burn_tx in json_burn_tx[
                                            "parsedInstruction"]:  # confirm burn and the amount
                                            if meta_burn_tx["type"] == "burn":
                                                if meta_burn_tx["params"]["mint"] == str(token[4]):
                                                    passed = False
                                                    token_checked = True
                                                    on_time = ""
                                                    largest_holder = 0
                                                    found = False
                                                    for item in large_holder_check_queue:
                                                        # [[token_address,checked=true/false,passed=true or false,supply,
                                                        # checked on time?]]
                                                        if item[0] == token[0]:
                                                            found = True  # this is simply used for special tokens
                                                            if not item[1]:  # if not checked
                                                                item[4] = "False"  # true default
                                                                token_checked = False
                                                            else:
                                                                if not item[2]:
                                                                    passed = False  # just for clarity(token failed test)
                                                                else:
                                                                    on_time = item[4]
                                                                    largest_holder = item[5]
                                                                    temp = 0
                                                                    for item2 in large_holder_check_queue:  # remove as done
                                                                        if item2[0] == token[0]:
                                                                            large_holder_check_queue.pop(temp)
                                                                            break
                                                                        temp += 1
                                                                    passed = True
                                                    if int(math.floor(float(meta_burn_tx["params"]["amount"]) / float(
                                                            token[5]) * float(100))) > 95:
                                                        if not found:
                                                            print(
                                                                "re-checking sniper status for token: " + str(token[0]))
                                                            special_token_queue.append(token[0])#place in this list so it signifies no need to re check the token after this final check check
                                                            token_checked = False  # token was not checked yet
                                                            large_holder_check_queue.append(
                                                                [token[0], False, False, token[10], "True", 0])
                                                            print(large_holder_check_queue)
                                                        if passed and token_checked:
                                                            holder_result = request('GET',
                                                                                    "https://pro-api.solscan.io/v1.0/token/holders?tokenAddress=" + str(
                                                                                        token[
                                                                                            0]) + "&limit=13&offset=0",
                                                                                    headers=solscan_header)
                                                            holder_list = holder_result.json()
                                                            five_or_above = 0  # number of holders that have 5%+
                                                            total_supply_held = 0  # amount fo supply top 10 holders hold
                                                            amount_of_coins_for_five_percent = \
                                                                int(float(token[10]) * float(0.05))
                                                            # total supply * 0.05 then convert to int
                                                            supply = token[10]
                                                            total_held_string = ""
                                                            five_above_string = ""
                                                            if "total" in holder_list:
                                                                if int(holder_list["total"]) > 12:
                                                                    iterator = 0
                                                                    for holder in holder_list["data"]:
                                                                        if iterator > 12:
                                                                            break
                                                                        if str(holder[
                                                                                   "owner"]) != "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":  # raydium pool
                                                                            if (int(float(holder["amount"]) / float(
                                                                                    10 ** token[11])) >=
                                                                                    amount_of_coins_for_five_percent):
                                                                                five_or_above += 1
                                                                            total_supply_held += int(
                                                                                float(holder["amount"]) / float(
                                                                                    10 ** token[11]))
                                                                        iterator += 1
                                                                if int(float(total_supply_held / supply) * float(
                                                                        100)) < 20:  # safu
                                                                    total_held_string = "Excellent : " + str(
                                                                        int(float(total_supply_held / supply) * float(
                                                                            100)))
                                                                elif 40 > int(float(total_supply_held / supply) * float(
                                                                        100)) > 20:  # moderate risk
                                                                    total_held_string = "Moderate : " + str(
                                                                        int(float(total_supply_held / supply) * float(
                                                                            100)))
                                                                else:  # high risk
                                                                    total_held_string = "Poor : " + str(
                                                                        int(float(total_supply_held / supply) * float(
                                                                            100)))
                                                                five_above_string = str(
                                                                    five_or_above)
                                                            ping_queue.append(
                                                                [int(largest_holder), token[6], int(math.floor(float(
                                                                    meta_burn_tx["params"][
                                                                        "amount"]) / float(
                                                                    token[5]) * float(
                                                                    100))), token[
                                                                     8], total_held_string, five_above_string, token[0],
                                                                 token[3]])
                                                            print(
                                                                "sent token for further checks (pre ping - DO NOT "
                                                                "BUY!): " + str(
                                                                    token[0]))
                                                            temp = 0
                                                            for item in large_holder_check_queue:  # remove it from
                                                                # the check queue
                                                                if item[0] == token[0]:
                                                                    large_holder_check_queue.pop(temp)
                                                                    break
                                                                temp += 1
                                                            raise TokenError
                                                        elif token_checked and not passed:
                                                            print(
                                                                "token was most likely sniped by dev: " + str(token[0]))
                                                            token_remove_errors.append(
                                                                ["token sniped by dev: ", token[0]])
                                                            raise TokenError
                                                    else:
                                                        print(
                                                            "low amount of liquidty burned..removing token ,amount the jeet"
                                                            "burned was : " + str(
                                                                float(meta_burn_tx["params"]["amount"]) /
                                                                float(token[5])) + " " + str(token[0]))
                                                        token_remove_errors.append(
                                                            ["low amount of liquidty burned..removing token ",
                                                             token[0]])
                                                        temp = 0
                                                        for item in large_holder_check_queue:
                                                            if item[0] == token[0]:
                                                                large_holder_check_queue.pop(temp)
                                                                break
                                                            temp += 1
                                                        token_queue.pop(index)
                                                        continue
                                                else:
                                                    print(
                                                        "error fetching burn tx...most likely removed liquidty ,token : " + str(
                                                            token[0]))
                                                    token_remove_errors.append(
                                                        ["error fetching burn tx...most likely removed liquidty ",
                                                         token[0]])
                                                    raise TokenError
                            else:
                                token_remove_errors.append(
                                    ["liquidty removed", token[0]])
                                print("liquidty removed...." + str(token[0]))
                                temp = 0
                                for item in large_holder_check_queue:
                                    if item[0] == token[0]:
                                        large_holder_check_queue.pop(temp)
                                        break
                                    temp += 1
                                token_queue.pop(index)
                                continue
                        except TokenError:
                            print("token removed!")
                            temp = 0
                            for item in large_holder_check_queue:
                                if item[0] == token[0]:
                                    large_holder_check_queue.pop(temp)
                                    break
                                temp += 1
                            token_queue.pop(index)
                            continue
                else:
                    token_remove_errors.append(
                        ["Removed a token due to token errors", token[0]])
                    print("Removed a token due to token errors " + str(token[0]))
                    temp = 0
                    for item in large_holder_check_queue:
                        if item[0] == token[0]:
                            large_holder_check_queue.pop(temp)
                            break
                        temp += 1
                    token_queue.pop(index)
                    continue
            index += 1
        await asyncio.sleep(4)  # small pause


def run():
    th = threading.Thread(target=check_for_large_holder)
    th.start()
    print("Running Bot....")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coros = [verify_token(), main(), append_past_tokens_to_file(), process_queue(),
             token_report()]#, check_for_large_holder()]  # poll_dev_wallet_activity()]
    loop.run_until_complete(asyncio.gather(*coros))
