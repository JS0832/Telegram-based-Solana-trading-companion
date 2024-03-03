import asyncio
import telegram
import requests
import time
import json

from urllib.request import Request, urlopen

# for now we fetch random coins but soon i will update this to a better code

# if the marketcap is still too low i will place a potential candidate
# #on a buffer list to check it agin and then if it filfils the critertia
# #it will snipe the token and remove ti form the buffer list

buffer_list = []  # list of candidate tokens that need to first grow a bit higher to buy them

scanned_coins = []  # past coins with adequate confluences

all_tokens = []  # grows as the program is executing ( able to show if there's a new token added to the json

url = "https://public-api.birdeye.so/public/tokenlist?sort_by=v24hUSD&sort_type=desc&limit=50"
headers = {"X-API-KEY": "282e76c342a649ad945dd16cff76d00a"}

dexToolsheaders = {
    "X-BLOBR-KEY": "5XuBH68cvNulgMBrYhqJPMtk4y2tOYC5"
}
# when I open a program it will read the test file and load up the list .


##jupiter related imports##

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

private_key1 = Keypair.from_bytes(  # me
    base58.b58decode("3yPt9DZp1BeRMa34gjNQdJ9bHHVgVqJZVyGvZrjrApYEtHpNQQgSLwdNPekbaTCoEY9Y6c33GzneogvPzVPuqqHN"))

private_key2 = Keypair.from_bytes(  # will
    base58.b58decode("6beroQxZeFdGsokdQczKwcQ17K1jrdZxNMkit8gNPuQWT3MbscUar66WBnSYLNGqtUT8t7Fi7uJLgwAaXB1dZna"))

async_client = AsyncClient(
    "https://api.mainnet-beta.solana.com")
jupiter_1 = Jupiter(async_client, private_key1)  # my wallet

jupiter_2 = Jupiter(async_client, private_key2)  # will


# also make sure the token is young
def main():
    # asyncio.run(swap_token("4hqxNjEcyaPfyjQQCtc9JDWaGQ4M1nDScCMZ9TTwY4AX"))
    # send_to_tx_confirmation_telegram(str("4hqxNjEcyaPfyjQQCtc9JDWaGQ4M1nDScCMZ9TTwY4AX"))
    ping_user_of_new_moon_coin("8UcdfyJjPByAMsMJ8VH2SNJnF8cceWy426SiigPPrwZD")
    max_marketcap = 160000  # mc & fdv parameters
    min_marketcap = 20000

    check_count = 0
    readfile()  # populate the list of checked tokens (with adequate confluences)
    # print(scanned_coins)

    # populate the array initially
    req = Request(
        url='https://token.jup.ag/all',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    webpage = urlopen(req)
    coin_data = json.loads(webpage.read())
    webpage.close()
    for coin_info in coin_data:
        if "address" in coin_info:
            all_tokens.append(str(coin_info["address"]))  # populates the array with all tokens
            # in the json file that are present in initial state of running the program
    print("populated all tokens array...")
    time.sleep(2)
    while True:
        print(str(check_count) + " ) checking for new moon coins....")
        req = Request(
            url='https://token.jup.ag/all',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        webpage = urlopen(req)
        coin_data = json.loads(webpage.read())  # re-read the jupiter json file
        webpage.close()
        print("number of items in json file: " + str(len(coin_data)))
        json_iterations = 0
        # here check the buffer lists again:
        for token in buffer_list:  # check if the tokens added to the buffer have met criteria yet
            dextools_url = ("https://open-api.dextools.io/free/v2/token/solana/" + str(
                token) + "/info")
            dex_response = requests.get(dextools_url, headers=dexToolsheaders)
            dex_response_json = dex_response.json()
            if dex_response_json["data"] is not None:
                if dex_response_json["data"]["mcap"] is not None:  # ignores nones
                    if max_marketcap >= int(dex_response_json["data"]["mcap"]) >= min_marketcap:
                        ping_user_of_new_moon_coin(str(token))
                        asyncio.run(swap_token(str(token)))  # makes the purchase
                        buffer_list.remove(str(token))  # remove from the buffer list
                        # here make a purchase ( add later)
                elif dex_response_json["data"]["fdv"] is not None:
                    if max_marketcap >= int(dex_response_json["data"]["fdv"]) >= min_marketcap:
                        ping_user_of_new_moon_coin(str(token))
                        asyncio.run(swap_token(str(token)))  # makes the purchase
                        buffer_list.remove(str(token))  # remove from the buffer list
                        # here make a purchase ( add later)
        for coin_info in coin_data:  # a loop to check the token inside the cs file
            if "address" in coin_info:
                if str(coin_info["address"]) not in all_tokens and coin_info[
                    'logURI'] is not None:  # just adds any token that has not yet been added to
                    # the list of tokens that hev been checked
                    # if the uri is none then it wil not add the toke to visited tokens and ill nto proceeed checkin the token further until uri is added
                    all_tokens.append(str(coin_info["address"]))
                    print("new token added to jupiter json file")
                    candidate = False  # this will be a pointer if the current token checked is a candidate or not
                    if 'logoURI' in coin_info:  # check if the key filed exists for that particular token
                        if verify_metadata(str(coin_info['logoURI'])):
                            candidate = True
                    # if check_metadata_solanafm(coin_info['address']): wont add this yet as its slow and useless using the solana fm api
                    # candidate = True
                    if candidate:  # if the token has the right metadata
                        if "decimals" in coin_info:
                            if str(coin_info['decimals']) == "6" or str(
                                    coin_info['decimals']) == "9":  # matching decimals
                                # now check if that toke already belong to the scanned list
                                if str(coin_info[
                                           'address']) not in scanned_coins:  # redundant but can keep this line
                                    scanned_coins.append(str(coin_info[
                                                                 'address']))  # appends to list of tokens that have right metadata and also decimals agree
                                    append_token(str(coin_info['address']))
                                    # here I will add logic that ignores the first run as its just me
                                    # re-running the program and the tokens it picks up are too late
                                    if check_count > 0:  # if it's 0 it means it's the first run since launch
                                        if 'name' in coin_info:
                                            print("checking token: " + str(
                                                coin_info['address']) + "with name: " + str(
                                                coin_info['name']))
                                        dextools_url = ("https://open-api.dextools.io/free/v2/token/solana/" + str(
                                            coin_info['address'])
                                                        + "/info")
                                        dex_response = requests.get(dextools_url, headers=dexToolsheaders)
                                        dex_response_json = dex_response.json()
                                        if dex_response_json["data"] is not None:  # if there is no data
                                            if dex_response_json["data"]["mcap"] is not None:  # ignores nones
                                                if max_marketcap >= int(
                                                        dex_response_json["data"]["mcap"]) >= min_marketcap:
                                                    # market cap constraints
                                                    asyncio.run(
                                                        swap_token(coin_info['address']))  # makes the purchase
                                                    send_to_tx_confirmation_telegram(str(coin_info['address']))
                                                    ping_user_of_new_moon_coin(str(coin_info['address']))
                                                    # will adjust this
                                                    # via other api
                                                    print("new token with low mc: " + str(coin_info["name"]))
                                                elif int(dex_response_json["data"]["mcap"]) < min_marketcap:
                                                    print("added a token to buffer list")
                                                    buffer_list.append(str(coin_info['address']))
                                                elif int(dex_response_json["data"]["mcap"]) > max_marketcap:
                                                    print("token exceeds max mc:" + str(
                                                        coin_info['address']) + "with name: " + str(
                                                        coin_info['name']))
                                            elif dex_response_json["data"]["fdv"] is not None:
                                                if max_marketcap >= int(
                                                        dex_response_json["data"]["fdv"]) >= min_marketcap:
                                                    # market cap constraints
                                                    asyncio.run(
                                                        swap_token(coin_info['address']))  # makes the purchase
                                                    send_to_tx_confirmation_telegram(str(coin_info['address']))
                                                    ping_user_of_new_moon_coin(str(coin_info['address']))
                                                    # will adjust this
                                                    # via other api
                                                    print("new token with low mc: " + str(coin_info["name"]))
                                                elif int(dex_response_json["data"]["fdv"]) < min_marketcap:
                                                    print("added a token to buffer list")
                                                    buffer_list.append(str(coin_info['address']))
                                                elif int(dex_response_json["data"]["fdv"]) > max_marketcap:
                                                    print("token exceeds max fdv:" + str(
                                                        coin_info['address']) + "with name: " + str(
                                                        coin_info['name']))
                                        else:
                                            print("data not found,placing the token on a buffer")
                                            # place on a buffer here to give it a try again as the token may be
                                            # too fresh
                                            buffer_list.append(str(coin_info['address']))
                                            # add to buffer list so it checks again
            json_iterations += 1  # helps me figure out if the json file has been read properly
        print("iterations of json file: " + str(json_iterations))
        print("tokens in the buffer: " + str(buffer_list))
        time.sleep(60)  # two-minute delay to not exhaust the api calls
        check_count += 1


def check_metadata_solanafm(address):  # fix this later (use solana api soon)
    # if finds matching data then return true else false
    url_solfm = "https://api.solana.fm/v0/tokens/" + str(address)
    headers_solfm = {"accept": "application/json"}
    response = requests.get(url_solfm, headers=headers_solfm)
    specific_key = "bafkrei"  # this substring is in $HARAMBE,$wif and $TRUMP ect...
    response_json = response.json()
    if response_json is not None:
        if 'logoURI' in response_json:
            if specific_key in response_json['logoURI']:
                return True
            else:
                return False


def notify_of_errors_to_telegram(error_details):
    bot = telegram.Bot(token='6405793513:AAEPOCPP022SkJlg6iYI-RgSHJ9AZOaoQy4')
    try:
        asyncio.run(bot.sendMessage(chat_id="-4129157033", text="there is a error: " + error_details))
    except Exception as e:
        print("Unable to send: ", e)
    time.sleep(3)


def ping_user_of_new_moon_coin(new_token_address):  # done via telegram bot father
    print("found new moon coin: " + new_token_address)
    send_to_telegram(new_token_address)


def send_to_telegram(new_token_address):
    bot = telegram.Bot(token='6405793513:AAEPOCPP022SkJlg6iYI-RgSHJ9AZOaoQy4')
    try:
        asyncio.run(bot.sendMessage(chat_id="-4129157033", text="found new moon coin: " + new_token_address))
    except Exception as e:
        print("Unable to send: ", e)
    time.sleep(3)


def send_to_tx_confirmation_telegram(token):
    bot = telegram.Bot(token='6405793513:AAEPOCPP022SkJlg6iYI-RgSHJ9AZOaoQy4')
    try:
        asyncio.run(bot.send_message(chat_id="-4129157033",
                                     text=f"Token Purchased with 0.5 sol: {token}"))
    except Exception as e:
        print("Unable to send: ", e)
    time.sleep(3)


async def swap_token(token_addy):
    try:
        transaction_data = await jupiter_1.swap(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint=token_addy,
            amount=100000000,  # this is the amount of sol used ? ( 0.5 sol each time for now) #set later to :500000000
            slippage_bps=10,
        )

        # Returns str: serialized transactions to execute the swap.

        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature = private_key1.sign_message(message.to_bytes_versioned(raw_transaction.message))
        signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
        result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        transaction_id = json.loads(result.to_json())['result']
        # print band also send to telegram
        print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}")
    except Exception as e:
        print("Unable to send: ", e)

    try:
        transaction_data = await jupiter_2.swap(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint=token_addy,
            amount=4800000000,  # this is the amount of sol used ? ( 0.5 sol each time for now) #set later to :500000000
            slippage_bps=10,
        )
        # Returns str: serialized transactions to execute the swap.

        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature = private_key2.sign_message(message.to_bytes_versioned(raw_transaction.message))
        signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
        result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        transaction_id = json.loads(result.to_json())['result']
        # print band also send to telegram
        print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}")
    except Exception as e:
        print("Unable to send: ", e)


def readfile():
    with open("tokens.txt") as file_in:
        for line in file_in:
            token = str(line).strip()
            scanned_coins.append(token)  # add the already checked token to the list to not give a false alarm
            # this may be changed depending on how I fetch the api data in the future


def append_token(new_token):  # appends token with required metadata characteristic
    with open('tokens.txt', 'a') as file:
        # Write the new line to the end of the file
        file.write(str(new_token) + '\n')


def verify_metadata(meta_data_text):
    # coin-address will be used to verify other important spects of the metadata such as its general structure

    # here i will use solana fm api to check the metadata structure of a token even more stringiently

    # key for solana fm :  sk_live_373836f82b13473da659c975b9c11571

    specific_key = "bafkrei"  # this substring is in $HARAMBE,$wif and $TRUMP ect...
    if specific_key in meta_data_text:
        return True
    else:
        return False

    # here I check the structure of the metadata,if correct returns true


if __name__ == "__main__":
    main()
