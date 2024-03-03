import requests

dexToolsheaders = {
    "X-BLOBR-KEY": "5XuBH68cvNulgMBrYhqJPMtk4y2tOYC5"
}

scanned_coins = []

matching_coins = []


def readfile():
    with open("tokens.txt") as file_in:
        for line in file_in:
            token = str(line).strip()
            scanned_coins.append(token)  # add the already checked token to the list to not give a false alarm
            # this may be changed depending on how I fetch the api data in the future


def main():
    readfile()
    print(scanned_coins)

    counter = 0

    max_marketcap = 500000000
    min_marketcap = 300000

    for address in scanned_coins:
        dextools_url = ("https://open-api.dextools.io/free/v2/token/solana/" + str(
            address) + "/info")
        dex_response = requests.get(dextools_url, headers=dexToolsheaders)
        dex_response_json = dex_response.json()
        if dex_response_json["data"] is not None:
            if dex_response_json["data"]["mcap"] is not None:  # ingores nones
                if max_marketcap >= int(dex_response_json["data"][
                                            "mcap"]) >= min_marketcap:  # will snipe is mc still low
                    # asyncio.run(swap_token(str(temp_token_address)))
                    # ping_user_of_new_moon_coin(str(coin_info['address'])) # will adjust this
                    # via other api
                    print(str(address))
                    matching_coins.append(str(address))
                    # print("found candid token: " + str(address))
        print("iteration: " + str(counter))
        counter += 1
    print("done: "+str(matching_coins))


if __name__ == "__main__":
    main()
