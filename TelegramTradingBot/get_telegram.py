# fetch telegram ( if available using solscan)

from requests import request

solscan_header = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MDY3NTM5ODAzOTQsImVtYWlsIjoic29sYmFieTMyNUBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJpYXQiOjE3MDY3NTM5ODB9.Lp77APFLV-rOnNbDzc1ob43Vp-9-KpeMe_b-fiOQrr0',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.82 Safari/537.36'
}


def get_telegram(token_ca):
    tele = ""
    web = ""
    twitter = ""
    metadata = request('GET',
                       "https://pro-api.solscan.io/v1.0/account/" + str(
                           token_ca),
                       headers=solscan_header)
    metadata_json = metadata.json()
    if "metadata" in metadata_json:
        token_info = metadata_json["metadata"]
        if "data" in token_info:
            if "extensions" in token_info["data"]:
                extensions = token_info["data"]["extensions"]
                if "telegram" in extensions:
                    tele = extensions["telegram"]
                if "website" in extensions:
                    web = extensions["website"]
                if "twitter" in extensions:
                    twitter = extensions["twitter"]
                return tele, web, twitter
            token_info_data = token_info["data"]
            if "telegram" in token_info_data:
                if token_info_data["telegram"] != "None":
                    return token_info_data["telegram"], "", ""
                else:
                    return "", "", ""
            else:
                return "", "", ""


def get_name_ticker(token_ca):
    name = ""
    ticker = ""
    creator_name = "UNKNOWN"
    metadata = request('GET',
                       "https://pro-api.solscan.io/v1.0/account/" + str(
                           token_ca),
                       headers=solscan_header)
    metadata_json = metadata.json()
    if "metadata" in metadata_json:
        token_info = metadata_json["metadata"]
        if "data" in token_info:
            info = token_info["data"]
            if "creator" in info:
                creator = info["creator"]
                if "name" in creator:
                    creator_name = creator["name"]
            return info["name"], info["symbol"], creator_name
    return "Error", "Error"


print(get_name_ticker("DT6tZPeknNEqcAkjUxoTRRLEQW6JS9p19rukCznAdxHv"))
