import time
from time import strftime, localtime
import dataBase
import asyncio
from telebot.async_telebot import AsyncTeleBot, types
import dev_previous_projects
import new_bot
import query_token
import check_advanced_rug
import buy_jupiter
import query_user_wallet
import threading
import dev_sold_so_far
import calcualte_risk_level
import DevWalletDatabase
import Ratings_database
import get_token_name_ticker
import check_dev_wallet_recent_tx
import check_first_layer_sol_transfers
import check_mint_time
import advanced_rug_two_checker
TOKEN = "6769248171:AAERXN-athfaM8JtK7kTYfNO6IpfJav7Iug"
bot = AsyncTeleBot(token=TOKEN)
db = dataBase.DataBase()  # initialise
trading_db = dataBase.trading_db  # initialise
wb = DevWalletDatabase.DevWalletDataBase()
rd = Ratings_database.TokenRateDataBase()
buy_queue = []  # will feed the buy engine so each user purchases a token (each user who selected auto buy


# add user scam reports

# [token_ca,amount,slippage,e_private_key,user_id]

# make a dictionary of pinged tokens and when used requests it can easily preview data

# add "past criminal activity such as "withdraw liquidty"

# confirm of buy
# calculate entry price (number of tokens ,amount spent and supply will help to calculate this)
# when user sells place them on a sell queue and [[user,amount,token],....]
# so far each user will only have one position per trade allowable
# needs position open
# open trades: (buy amount in sol,token address,token supply,),().....
# to share pnl(unrealised you fetch current price and compare to buy price
# to share pnl realised you search the wallet and see what token sells where made(harder)
async def buy_engine():
    while True:
        if len(buy_queue) > 0:  # need to be changed in the future
            order_details = buy_queue[0]
            await buy_jupiter.buy_token_func(order_details[0], order_details[1], order_details[2], order_details[3],
                                             order_details[4])
            buy_queue.pop(0)
        await asyncio.sleep(0.1)  # fast check


async def ping_all_subscribers():  # when a token is abot to get pinged generate its "ai" summary please ( make this
    # o sperate thread too) ,check how to manage variable used by different threads in python
    while True:
        if len(new_bot.ping_queue) > 0:  # if there is a token to be pinged
            list_of_users = db.return_all_activated_users()
            data = new_bot.ping_queue[0]  # grabs the first in queue
            if data[9]:
                timed_launch = " ⏲ TIMED LAUNCH ⏲ "
            else:
                timed_launch = ""
            txn_hash = data[7]
            decimals = data[8]
            # also grab the token name from the bot.
            largest_holder = str(data[0])  # 1
            inital_liq = str(data[1]).replace('.', ',')  # 2
            liq_burned = str(data[2]).replace('.', ',')  # 3
            tokens_to_lp_percent = str(data[3]).replace('.', ',')
            decentralisation = str(data[4])
            whale_holders = str(data[5])
            token_ca = str(data[6])
            advnaced_rug = check_advanced_rug.check(token_ca)  # add this to the refresh (query token code)
            if advnaced_rug == "High" or advnaced_rug == "Extremely High":  # make cusomisable pings for this option and set it to filter extremely high mayeb but for now it wills et thigh
                print("Removed token due to a high risk of advanced rug.")
                new_bot.ping_queue.pop(0)  # won't even ping the token due to the risk
                continue
            print("checking for advanced rug 2.0")
            if advanced_rug_two_checker.check_for_common_funding_wallets(token_ca):
                print("Removed token due to a high risk of advanced rug 2.0 .")
                new_bot.ping_queue.pop(0)  # won't even ping the token due to the risk
                continue
            print("passed rug 2.0 checks!")
            temp_dev_info = dev_previous_projects.check_previous_project(txn_hash, token_ca)
            past_token_list = temp_dev_info[0]
            deployer = temp_dev_info[1]
            # deployer info :
            deployer_balances = query_user_wallet.return_token_balances(deployer)  # balance in the deployer
            # here make a function to return the funding wallet and plug that into the query user wallet
            funding_wallet_info = check_first_layer_sol_transfers.get_funding_wallet(deployer, inital_liq)
            if funding_wallet_info != "":
                fund_wallet = query_user_wallet.return_token_balances(funding_wallet_info)
            else:
                fund_wallet = "NOT TRACKABLE"
            past_tokens_string = "\n"
            if len(past_token_list) > 0:
                if len(past_token_list) > 8:
                    print("removed due to too many past tokens")
                    new_bot.ping_queue.pop(0)  # won't even ping the token due to the risk
                    continue
                for token in past_token_list:
                    temp_string = "https://dexscreener.com/solana/" + str(token)
                    past_tokens_string += f"📈 [Previous Project]({temp_string})\n"
            else:
                past_tokens_string = " *None 😇*"
            # dev selling report:
            result = dev_sold_so_far.check_dev(txn_hash, token_ca)
            if int(result[0]) > 2:  # dev selling early is bearish
                new_bot.ping_queue.pop(0)  # won't even ping the token due to the risk
                continue
            risk_level = calcualte_risk_level.process_risk(advnaced_rug, largest_holder, result[0],
                                                           tokens_to_lp_percent, decentralisation)
            number_of_dev_wallets = len(result[1])
            if number_of_dev_wallets >= 8:
                print("dev wallets number exceeded risk level")
                new_bot.ping_queue.pop(0)  # won't even ping the token due to the risk
                continue
            token_ui_supply = int(result[2])
            get_mint_epoch = check_mint_time.check_mint_epoch(txn_hash, token_ca, token_ui_supply)
            if get_mint_epoch == 0:
                get_mint_epoch = "Not Found"
            else:
                get_mint_epoch = str(int((time.time()-get_mint_epoch)/60)) + " Minutes Ago"
            # name and ticker
            token_meta = get_token_name_ticker.get_name_ticker(txn_hash)
            token_name = str(token_meta[0])
            token_ticker = str(token_meta[1])
            if not wb.check_token(token_ca):  # if toke has not been saved in database
                wb.add_dev_wallets(token_ca, ','.join(result[1]))
            percent_amount = str(result[0]).replace('.', ',')  # names can contain illegal chars so sort it out
            # extract data from the ping queue
            markup = types.InlineKeyboardMarkup()
            t_settings = types.InlineKeyboardButton("Settings", callback_data="trading_settings")
            buy = types.InlineKeyboardButton("Buy", callback_data="trigger_buy " + str(data[6]))
            sell = types.InlineKeyboardButton("Sell",
                                              callback_data="trigger_sell " + str(data[6]) + " " + str(decimals))
            refresh = types.InlineKeyboardButton("Refresh Info",
                                                 callback_data="refresh " + str(data[6]) + " " + tokens_to_lp_percent)
            positions = types.InlineKeyboardButton("Check all positions", callback_data="positions")
            info = types.InlineKeyboardButton("Info", callback_data="info")
            share = types.InlineKeyboardButton("Share PNL", callback_data="pnl")
            rate = types.InlineKeyboardButton("Rate This Ping", callback_data="rate " + str(data[6]))
            check_dev_activity = types.InlineKeyboardButton("Check activity", callback_data="check_dev " + str(data[6]))
            markup.row(t_settings, buy, sell)
            markup.row(refresh, check_dev_activity, positions)
            markup.row(share, info, rate)
            for user in list_of_users:  # just so I can debug
                full_configuration = trading_db.return_all_settings(user[0])
                if full_configuration[9] == "True":  # if active trading user
                    temp = []
                    user_ping_settings = full_configuration[10]
                    if user_ping_settings != "DEFAULT":  # if the settings aren't Default
                        temp = user_ping_settings.split(",")  # converts the comma separated string to an aray
                    else:
                        temp = [2, 98, 60, 6, 20]  # change a bit later
                    if int(data[1]) >= int(temp[0]) and int(data[2]) >= int(temp[1]) and int(data[3]) >= int(
                            temp[2]) and int(data[0]) <= int(temp[4]):  # implement risk level here later
                        if full_configuration[4] == "ON":  # maybe here place on a buy queue
                            slippage = float(full_configuration[12])
                            sol_amount = float(full_configuration[3])
                            ekey = full_configuration[2]
                            buy_queue.append([token_ca, sol_amount, slippage, ekey, int(user[0])])
                        await bot.send_message(chat_id=int(user[0]),
                                               text=f"🤑 New Token *{timed_launch}* : `{token_ca}`\n\n🎂 Name and "
                                                    f"Ticker: *{token_name}* , *{token_ticker}*\n\n🤝 "
                                                    f"Basics"
                                                    f": "
                                                    f"Liquidty Burned and Mint Disabled 🍀"
                                                    f"\n🤖 AI "
                                                    f"token summary : *Coming Soon* \n🐋 "
                                                    f"Largest Cumulative "
                                                    f"holder : *{
                                                    largest_holder}*\n🎗 Dev sold : {percent_amount} percent so far\n🗂 Number of Dev's Wallets : *{number_of_dev_wallets}*\n🎉 Initial Liquidity :"
                                                    f" *{inital_liq}*\n🔥 Liquidity Burned : "
                                                    f"*{liq_burned}*\n🌊 Tokens sent to LP : "
                                                    f"*{tokens_to_lp_percent}*\n💳 "
                                                    f"Decentralisation :  "
                                                    f"*{decentralisation}*\n🐳 Number of whale "
                                                    f"holders : *{whale_holders}*\n⚰️ Advanced "
                                                    f"Rug : *{advnaced_rug}*\n🩸 Risk "
                                                    f"Level : *{risk_level}*\n🍬 Minted : *{get_mint_epoch}*\n\n📈 [Token Chart]("
                                                    f"https://dexscreener.com/solana/{token_ca})"
                                                    f"\n📱 [Telegram]("
                                                    f"http://www.example.com/)\n\n😁 *Funding Wallet :* \n*{fund_wallet}\n*👝 [Deployer]("
                                                    f"https://solscan.io/account/{deployer})\n🗃 Deployer Balances : \n*{deployer_balances}* \n📚"
                                                    f"Dev's Previous"
                                                    f" Projects: {past_tokens_string}",
                                               reply_markup=markup, parse_mode='MarkdownV2',
                                               disable_web_page_preview=True)  # CHECK IS IT WORKS
            new_bot.ping_queue.pop(0)  # remove from the queue (FIFO)
        await asyncio.sleep(1)


# add scoails commands
# add all list commands too

@bot.message_handler(commands=['positions'])  #
async def check_open_positions(message):  # handle user positions
    pass
    # buy price  -> comapre to current price and deduce roi based on evrage entry price and corrent holdings x price?

    # roi will simpl be inital sol spent vs current sol holdigns in that token
    # (token ca , initial buy amount in sol)
    # convert comma separated string into a list then every 2 places is new entry


@bot.message_handler(commands=['start'])
async def activate_bot(message):
    # check if the user is allowed to use the bot
    user_id = int(message.chat.id)
    if any(user_id in user for user in db.return_all_activated_users()):  # check if user subscribed
        await bot.send_message(user_id,
                               "Welcome to AlphaPulse,you will now receive coin pings.Please use /commands if you "
                               "want to "
                               "setup the bot to meet your needs.")
        trading_db.update_active(user_id, "True")  # reactivate trading ability
    else:
        await bot.send_message(user_id, "Sorry,You dont have a active subscription,please use our subscription bot to"
                                        "activate a subscription plan")


@bot.callback_query_handler(func=lambda query: query.data == "info")
async def info(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    info_markup = types.InlineKeyboardMarkup(row_width=1)
    close_info = types.InlineKeyboardButton("Hide", callback_data="hide")
    info_markup.add(close_info)
    await bot.send_message(user_id, "Understanding Pings:\nFundamentals: \nLiquidty locked : This indicates tat the "
                                    "Dev has Destroyed liquidty tokens used to remove liquidty.This a bullish sign as "
                                    "the developer cannot just remove liquidty when they desire.\nMint disabled: A "
                                    "common scam is for the dev to mint many tokens which turns the investor holding "
                                    "to dust and allows the dev to remove al liquidty from the token by selling them "
                                    "back to the liquidty pool.When the dev disables the min this is not "
                                    "possible.\nPercent of tokens sent to Liquidty Pool: The more token the developer "
                                    "dedicates tot he liquidty pool the less they hold.Ideally bullish projects have "
                                    "at least 80% of token sent to the Liquidty pool.The more tokens are sent the "
                                    "more selfless the developer is.\nInitial liquidty: Most successful projects seem "
                                    "to have at least 5 Sol of initial liquidty or more.very low amounts of initial "
                                    "liquidty indicate that the dev has low funds which is bearish.Large amount of "
                                    "liquidty can indicate commitment to the project assuming its locked.\nMore "
                                    "Advanced concepts:\nDecentralisation: This is a very vital concept in crypto.When "
                                    "a token is highly decentralised it means no single entity can manipulate it.low "
                                    "level of decentralisation usually indicate whales with bad intentions that may "
                                    "crash the price.\nWhale Holders: A large number of whale holders will without "
                                    "doubt affect decentralisation which can negatively affect the price.this is "
                                    "especially vital for micro cap tokens as the price can be moved very "
                                    "quickly.\nAdvanced Rug: Evil Devs now developed more advanced ways to trick "
                                    "investors and profit from them.This is sometimes referred as Farming  Which is "
                                    "a fast pump and dump event. The token may look very good on paper but it still "
                                    "secretly might be a SCAM. Our state fo the art system is now able to detect "
                                    "advanced scam techniques prevention YOU from loosing you capital.We Cannot revel "
                                    "how how Algorithm works because we want you to have a market edge over other "
                                    "crypto traders. We an say that it involves alot fo computation and has been "
                                    "back tested with over 2000 past SPL tokens.Our bot stores every spl token that "
                                    "released and analyses its behaviour using RAG and other advanced techniques that "
                                    "are mentions in the whitepaper.\nRisk Level: This is still in development.Stay "
                                    "tuned!\nDev Past Tokens: While many devs Always use a new wallet to create a new "
                                    "tokens some lazy devs keep using the same wallet to create a token.Our bot is "
                                    "able to check this.If the dev is reusing the same wallet it's usually a bearish "
                                    "sign and it indicated low effort farming tactics.If the bot finds any projects "
                                    "the bot will show you the 3 most recent ones.", reply_markup=info_markup)


# trading settings:
@bot.callback_query_handler(func=lambda query: query.data == "trading_settings")
# show funds here and the address to the wallet
async def help_func_callback(callback_query: types.CallbackQuery):
    # here display current settings:
    user_id = int(callback_query.from_user.id)
    user_settings = trading_db.return_all_settings(user_id)  # no sure why error
    sol_buy_amount = str(user_settings[3]).replace('.', ',')
    temp = []  # for user ping settings fetching
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to an aray
    else:
        temp = [2, 98, 85, 6, 20]
    ping_inital_liquidty = str(temp[0])
    ping_liquidty_burned = str(temp[1])
    ping_tokens_to_lp = str(temp[2])
    ping_risk_level = str(temp[3])
    lch = str(temp[4])
    # wallet stuff:
    wallet_address = str(user_settings[1])
    balances_string = query_user_wallet.return_token_balances(wallet_address)
    help_markup = types.InlineKeyboardMarkup()
    auto_buy = types.InlineKeyboardButton("Auto Buy", callback_data="AB_SETTINGS")
    auto_sell = types.InlineKeyboardButton("Auto Sell", callback_data="AS_SETTINGS")
    sell_w_dev_settings = types.InlineKeyboardButton("sell with dev", callback_data="SWD_SETTINGS")
    customise_pings = types.InlineKeyboardButton("Configure pings", callback_data="PING_SETTINGS")
    reset_default = types.InlineKeyboardButton("Reset to defaults", callback_data="default_config")
    funds = types.InlineKeyboardButton("Configure Funding", callback_data="funds_config")
    hide_trading_settings = types.InlineKeyboardButton("Hide Settings", callback_data="hide")
    help_markup.row(auto_buy, auto_sell, sell_w_dev_settings)
    help_markup.row(funds, customise_pings)
    help_markup.row(reset_default, hide_trading_settings)
    await bot.send_message(callback_query.from_user.id,
                           f"__Current Settings:__\n\n💰 Manual/Auto Buy Amount: *{sol_buy_amount}* SOL\n💳 Auto Buy : *{str(user_settings[4])}*\n🤑 Auto "
                           f"Sell : *{str(user_settings[6])}*\n👳🏾 Sell With Dev : *{str(
                               user_settings[5])}*\n\n__Ping Settings:__\n\n🎉 Initial "
                           f"Liquidity : {ping_inital_liquidty}\n🔥 Liquidity Burned : {ping_liquidty_burned}\n🌊"
                           f"Tokens sent to LP : {ping_tokens_to_lp}\n🩸 Risk Level : {ping_risk_level}\n🐋 Largest "
                           f"Cumulative holder : < {lch}\n👝 Wallet Balances : \n\n📍 My Address : *`{wallet_address}`*\n{balances_string}"
                           f"\n\n__Select the setting you wish to"
                           f" modify:__", reply_markup=help_markup, parse_mode='MarkdownV2',
                           disable_web_page_preview=True)


# trading settings clone (till i figure out how to not delete the buy notification
@bot.callback_query_handler(func=lambda
        query: query.data == "trading_settings2")  # here i need to add wallet balance check ,current wallet adress
# and spl token balances too
async def help_func_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    # here display current settings:
    user_id = int(callback_query.from_user.id)
    user_settings = trading_db.return_all_settings(user_id)  # no sure why error
    sol_buy_amount = str(user_settings[3]).replace('.', ',')
    temp = []  # for user ping settings fetching
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to an aray
    else:
        temp = [2, 98, 85, 6, 20]
    ping_inital_liquidty = str(temp[0])
    ping_liquidty_burned = str(temp[1])
    ping_tokens_to_lp = str(temp[2])
    ping_risk_level = str(temp[3])
    lch = str(temp[4])

    # wallet stuff:
    wallet_address = str(user_settings[1])
    balances_string = query_user_wallet.return_token_balances(wallet_address)
    help_markup2 = types.InlineKeyboardMarkup()
    auto_buy = types.InlineKeyboardButton("Auto Buy", callback_data="AB_SETTINGS")
    auto_sell = types.InlineKeyboardButton("Auto Sell", callback_data="AS_SETTINGS")
    sell_w_dev_settings = types.InlineKeyboardButton("sell with dev", callback_data="SWD_SETTINGS")
    customise_pings = types.InlineKeyboardButton("Configure pings", callback_data="PING_SETTINGS")
    reset_default = types.InlineKeyboardButton("Reset to defaults", callback_data="default_config")  # giving problems
    funds = types.InlineKeyboardButton("Configure Funding", callback_data="funds_config")
    hide_trading_settings = types.InlineKeyboardButton("Hide Settings", callback_data="hide")
    help_markup2.row(auto_buy, auto_sell, sell_w_dev_settings)
    help_markup2.row(funds, customise_pings)
    help_markup2.row(reset_default, hide_trading_settings)
    await bot.send_message(callback_query.from_user.id,
                           f"__Current Settings:__\n\n💰 Manual/Auto Buy Amount: *{sol_buy_amount}* SOL\n💳 Auto Buy : *{str(user_settings[4])}*\n🤑 Auto"
                           f"Sell : *{str(user_settings[6])}*\n👳🏾 Sell With Dev : *{str(
                               user_settings[5])}*\n\n__Ping Settings:__\n\n🎉 Initial "
                           f"Liquidity : {ping_inital_liquidty}\n🔥 Liquidity Burned : {ping_liquidty_burned}\n🌊"
                           f"Tokens sent to LP : {ping_tokens_to_lp}\n🩸 Risk Level : {ping_risk_level}\n🐋 Largest "
                           f"Cumulative holder : < {lch}\n👝 Wallet Balances : \n\n📍 My Address : *`{wallet_address}`*\n{balances_string}"
                           f"\n\n__Select the setting you wish to"
                           f" modify:__", reply_markup=help_markup2, parse_mode='MarkdownV2',
                           disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda query: query.data == "hide")  # hiding the settings menu
async def hide_settings(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)


@bot.callback_query_handler(func=lambda query: query.data == "default_config")  # hiding the settings menu
async def reset_all_settings(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.reset_user(user_id)
    await bot.send_message(callback_query.from_user.id, "Settings changed to Default")


# FUND SETTINGS
@bot.callback_query_handler(func=lambda query: query.data == "funds_config")
async def configure_funds(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    user_id = int(callback_query.from_user.id)
    configure_funds_markup = types.InlineKeyboardMarkup(row_width=3)
    create_new_wallet = types.InlineKeyboardButton("Create new wallet", callback_data="create_new_wallet")
    withdraw_funds = types.InlineKeyboardButton("Withdraw Funds", callback_data="withdraw_funds")
    hide_configure_funds = types.InlineKeyboardButton("Go Back", callback_data="trading_settings2")
    configure_funds_markup.add(create_new_wallet, withdraw_funds, hide_configure_funds)
    await bot.send_message(chat_id=user_id, text="💲 Manage Funds",
                           reply_markup=configure_funds_markup)


@bot.callback_query_handler(func=lambda query: query.data == "create_new_wallet")
async def confirm_new_wallet(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    confirm_new_keys = types.InlineKeyboardMarkup(row_width=3)
    confirm_new = types.InlineKeyboardButton("Confirm", callback_data="confirm_new_wallet")
    decline_new = types.InlineKeyboardButton("Decline", callback_data="trading_settings2")
    hide_new_wallet = types.InlineKeyboardButton("Go Back", callback_data="trading_settings2")
    confirm_new_keys.add(confirm_new, decline_new, hide_new_wallet)
    await bot.send_message(chat_id=user_id, text="Confirmation of new wallet creation,Please ensure you have removed "
                                                 "all funds or else they will be lost forever!",
                           reply_markup=confirm_new_keys)


# Confirming removal of wallet (ie create new wallet)
@bot.callback_query_handler(func=lambda query: query.data == "confirm_new_wallet")  # do later
async def configure_funds(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.create_new_wallet(user_id)
    await bot.send_message(chat_id=user_id, text="New wallet generated!\nOld wallet has been Destroyed!")


# PING SETTINGS:
@bot.callback_query_handler(func=lambda query: query.data == "PING_SETTINGS")  # hiding the settings menu
async def handle_ping_settings(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    ping_settings_options = types.InlineKeyboardMarkup(row_width=4)
    largest_cumulative_holder_size = types.InlineKeyboardButton("Largest cumulative holder", callback_data="lch")
    inital_liquidty = types.InlineKeyboardButton("Initial Liquidty", callback_data="inital_liquity")
    liquidty_burned_percent = types.InlineKeyboardButton("Liquidty Burnt %", callback_data="liquidity_burned")
    amount_of_tokens_to_lp = types.InlineKeyboardButton("Percent of supply sent to LP",
                                                        callback_data="percent_sent_lp")
    risk_level = types.InlineKeyboardButton("Risk Level", callback_data="risk_level_settings")
    reset_ping = types.InlineKeyboardButton("Reset Ping settings", callback_data="reset_ping")
    go_back = types.InlineKeyboardButton("close Ping Settings", callback_data="trading_settings2")
    ping_settings_options.add(inital_liquidty, liquidty_burned_percent, amount_of_tokens_to_lp, risk_level, reset_ping,
                              largest_cumulative_holder_size,
                              go_back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Adjust Ping Settings",
                           reply_markup=ping_settings_options)


# PING SETTINGS LAYOUT(MINIMUM INITIAL LIQUIDITY,MINIMUM LIQUIDTY BURNED,TOKENS SENT TO LP,RISK LEVEL,largest c holder)

# default_ping_setting = [5, 98, 80, 6]

# PING SETTINGS (branched)
@bot.callback_query_handler(func=lambda query: query.data == "lch")  # hiding the settings menu
async def largest_cumulative_holder(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    inital_liq_buttons = types.InlineKeyboardMarkup(row_width=5)
    lch_under_50 = types.InlineKeyboardButton("< 50 %", callback_data="lch_under_50")
    lch_under_20 = types.InlineKeyboardButton("< 20 %", callback_data="lch_under_20")
    lch_under_10 = types.InlineKeyboardButton("< 10 %", callback_data="lch_under_10")
    lch_under_5 = types.InlineKeyboardButton("< 5 %", callback_data="lch_under_5")
    back = types.InlineKeyboardButton("Go back", callback_data="PING_SETTINGS")
    inital_liq_buttons.add(lch_under_50, lch_under_20, lch_under_10, lch_under_5, back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="🐋 Adjust Largest Cumulative Holder size: ",
                           reply_markup=inital_liq_buttons)


# ping  largest cumulative holder settings:
@bot.callback_query_handler(func=lambda query: query.data == "lch_under_50")  # hiding the settings menu
async def largest_cumulative_holder_sub_settings(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[4] = "50"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "2,98,80,6,50")
    await bot.send_message(chat_id=user_id, text="Largest cumulative holder set to be under 50% supply holding")


@bot.callback_query_handler(func=lambda query: query.data == "lch_under_20")  # hiding the settings menu
async def largest_cumulative_holder_sub_settings(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[4] = "20"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "2,98,80,6,20")
    await bot.send_message(chat_id=user_id, text="Largest cumulative holder set to be under 20% supply holding")


@bot.callback_query_handler(func=lambda query: query.data == "lch_under_10")  # hiding the settings menu
async def largest_cumulative_holder_sub_settings(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[4] = "10"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "2,98,80,6,10")
    await bot.send_message(chat_id=user_id, text="Largest cumulative holder set to be under 10% supply holding")


@bot.callback_query_handler(func=lambda query: query.data == "lch_under_5")  # hiding the settings menu
async def largest_cumulative_holder_sub_settings(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[4] = "5"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "2,98,80,6,5")
    await bot.send_message(chat_id=user_id, text="Largest cumulative holder set to be under 5% supply holding")


@bot.callback_query_handler(func=lambda query: query.data == "inital_liquity")  # hiding the settings menu
async def initial_liquity_ping(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    inital_liq_buttons = types.InlineKeyboardMarkup(row_width=5)
    two_sol = types.InlineKeyboardButton(">=2 SOL", callback_data="inital_2")
    three_sol = types.InlineKeyboardButton(">=3 SOL", callback_data="inital_3")
    five_sol = types.InlineKeyboardButton(">=5 SOL", callback_data="inital_5")
    ten_sol = types.InlineKeyboardButton(">=10 SOL", callback_data="inital_10")
    back = types.InlineKeyboardButton("Go back", callback_data="PING_SETTINGS")
    inital_liq_buttons.add(two_sol, three_sol, five_sol, ten_sol, back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="🎉 Adjust Inital Liquity: ",
                           reply_markup=inital_liq_buttons)

    # PING SETTINGS LAYOUT(MINIMUM INITIAL LIQUIDITY,MINIMUM LIQUIDTY BURNED,TOKENS SENT TO LP,RISK LEVEL)


# ping liquidty settings:
@bot.callback_query_handler(func=lambda query: query.data == "inital_2")  # hiding the settings menu
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[0] = "2"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "2,98,80,6,20")
    await bot.send_message(chat_id=user_id, text="Initial Liquidity set to 2 SOL or Above")


@bot.callback_query_handler(func=lambda query: query.data == "inital_3")  # hiding the settings menu
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[0] = "3"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "3,98,80,6,20")
    await bot.send_message(chat_id=user_id,
                           text="Initial Liquidity set to 3 SOL or Above")  # might show then hide it using async io


@bot.callback_query_handler(func=lambda query: query.data == "inital_5")  # hiding the settings menu
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[0] = "5"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "5,98,80,6,20")
    await bot.send_message(chat_id=user_id, text="Initial Liquidity set to 5 SOL or Above")


@bot.callback_query_handler(func=lambda query: query.data == "inital_10")  # hiding the settings menu
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[0] = "10"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "10,98,80,6,20")
    await bot.send_message(chat_id=user_id, text="Initial Liquidity set to 10 SOL or Above")


@bot.callback_query_handler(func=lambda query: query.data == "liquidity_burned")  # hiding the settings menu
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    inital_liq_buttons = types.InlineKeyboardMarkup(row_width=3)
    ninezero_percent_ping = types.InlineKeyboardButton(">=90%", callback_data="90_percent_ping")
    nineeight_percent_ping = types.InlineKeyboardButton(">=98%", callback_data="98_percent_ping")
    back = types.InlineKeyboardButton("Go back", callback_data="PING_SETTINGS")
    inital_liq_buttons.add(nineeight_percent_ping, ninezero_percent_ping, back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="🔥 Adjust Liquidty Burned: ",
                           reply_markup=inital_liq_buttons)


# liquidty burned ping settings

@bot.callback_query_handler(func=lambda query: query.data == "90_percent_ping")
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[1] = "90"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "5,90,80,6,20")
    await bot.send_message(chat_id=user_id, text="Initial Liquidity Burn set to 90%+")


@bot.callback_query_handler(func=lambda query: query.data == "98_percent_ping")
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[1] = "98"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "5,98,80,6,20")
    await bot.send_message(chat_id=user_id, text="Initial Liquidity Burn set to 98%+")


@bot.callback_query_handler(func=lambda query: query.data == "percent_sent_lp")  # hiding the settings menu
async def percent_lp_ping(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    percent_sent_lp_buttons = types.InlineKeyboardMarkup(row_width=5)
    sixzero_percent_ping = types.InlineKeyboardButton(">=60%", callback_data="60_percent_ping")
    sevenzero_percent_ping = types.InlineKeyboardButton(">=70%", callback_data="70_percent_ping")
    eigthzero_percent_ping = types.InlineKeyboardButton(">=80%", callback_data="80_percent_ping")
    ninefive_percent_ping = types.InlineKeyboardButton(">=95%", callback_data="95_percent_ping")
    back = types.InlineKeyboardButton("Go back", callback_data="PING_SETTINGS")
    percent_sent_lp_buttons.add(sixzero_percent_ping, sevenzero_percent_ping, eigthzero_percent_ping,
                                ninefive_percent_ping, back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="🔥 Adjust Token % sent to LP: ",
                           reply_markup=percent_sent_lp_buttons)


@bot.callback_query_handler(func=lambda query: query.data == "60_percent_ping")
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[2] = "60"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "5,98,60,6,20")
    await bot.send_message(chat_id=user_id, text="Token sent to LP ping setting set to : 60%+")


@bot.callback_query_handler(func=lambda query: query.data == "70_percent_ping")
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[2] = "98"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "5,98,70,6,20")
    await bot.send_message(chat_id=user_id, text="Token sent to LP ping setting set to : 70%+")


@bot.callback_query_handler(func=lambda query: query.data == "80_percent_ping")
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[2] = "80"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "5,98,80,6,20")
    await bot.send_message(chat_id=user_id, text="Token sent to LP ping setting set to : 80%+")


@bot.callback_query_handler(func=lambda query: query.data == "95_percent_ping")
async def liquity_burned_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ping_settings = str(trading_db.return_all_settings(user_id)[10])
    if user_ping_settings != "DEFAULT":
        temp = user_ping_settings.split(",")  # converts the comma separated string to a aray
        temp[2] = "95"
        trading_db.update_ping_settings(user_id, ','.join(temp))  # adds it back as a comma separated list of items
    else:
        trading_db.update_ping_settings(user_id, "5,98,95,6,20")
    await bot.send_message(chat_id=user_id, text="Token sent to LP ping setting set to : 95%+")


@bot.callback_query_handler(func=lambda query: query.data == "risk_level_settings")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    percent_sent_lp_buttons = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Go back", callback_data="PING_SETTINGS")
    percent_sent_lp_buttons.add(back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Released soon",
                           reply_markup=percent_sent_lp_buttons)


@bot.callback_query_handler(func=lambda query: query.data == "reset_ping")  # hiding the settings menu
async def reset_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.reset_ping_settings(user_id)
    await bot.send_message(chat_id=user_id, text="Ping Settings set to Factory settings")


# TRADING SUB SETTINGS

@bot.callback_query_handler(func=lambda query: query.data == "AB_SETTINGS")
async def auto_buy_settings(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    buy_settings = types.InlineKeyboardMarkup(row_width=5)
    buy_amount = types.InlineKeyboardButton("Buy Amount", callback_data="buy_amount")
    enable_ab = types.InlineKeyboardButton("Enable Auto Buy", callback_data="enable_ab")
    disable_ab = types.InlineKeyboardButton("Disable Auto Buy", callback_data="disable_ab")
    slippage = types.InlineKeyboardButton("Slippage", callback_data="slippage")
    back = types.InlineKeyboardButton("Go Back", callback_data="trading_settings2")
    buy_settings.add(back, buy_amount, slippage, enable_ab, disable_ab)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Configure Manual and Auto Buy settings",
                           reply_markup=buy_settings)


# AB Sub Settings

# (enabling auto buy)
@bot.callback_query_handler(func=lambda query: query.data == "enable_ab")  # LATER CHECK CURRENT STATE SO IT TELS
# PERSON THEY DONT NEE TO CHANGE IF TIS ALREADY HE STAE THEY ANT IT TIT TOT BE
async def auto_buy_settings(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_auto_buy(user_id, "ON")
    await bot.send_message(chat_id=callback_query.from_user.id, text="Auto buy enabled")


# (disabling auto buy)
@bot.callback_query_handler(func=lambda query: query.data == "disable_ab")
async def auto_buy_settings(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_auto_buy(user_id, "OFF")
    await bot.send_message(chat_id=callback_query.from_user.id, text="Auto buy disabled")


@bot.callback_query_handler(func=lambda query: query.data == "buy_amount")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    buy_amount_buttons = types.InlineKeyboardMarkup(row_width=5)
    zero_one_sol = types.InlineKeyboardButton("0.1 SOL", callback_data="zero_one_sol")
    zero_two_five_sol = types.InlineKeyboardButton("0.25 SOL", callback_data="zero_two_five_sol")
    zero_five_sol = types.InlineKeyboardButton("0.5  SOL", callback_data="zero_five_sol")
    one_sol = types.InlineKeyboardButton("1  SOL", callback_data="one_sol")
    back = types.InlineKeyboardButton("Go Back", callback_data="AB_SETTINGS")
    buy_amount_buttons.add(zero_one_sol, zero_two_five_sol, zero_five_sol, one_sol, back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Released soon",
                           reply_markup=buy_amount_buttons)


# AB button selection options Settings

@bot.callback_query_handler(func=lambda query: query.data == "zero_one_sol")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_sol_amount_buy(user_id, str(0.1))
    await bot.send_message(user_id, text="Updated to 0.1 Sol per buy order")


@bot.callback_query_handler(func=lambda query: query.data == "zero_two_five_sol")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_sol_amount_buy(user_id, str(0.25))
    await bot.send_message(user_id, text="Updated to 0.25 Sol per buy order")


@bot.callback_query_handler(func=lambda query: query.data == "zero_five_sol")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_sol_amount_buy(user_id, str(0.5))
    await bot.send_message(user_id, text="Updated to 0.5 Sol per buy order")


@bot.callback_query_handler(func=lambda query: query.data == "one_sol")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_sol_amount_buy(user_id, str(1.0))
    await bot.send_message(user_id, text="Updated to 1.0 Sol per buy order")


# Slippage settings
@bot.callback_query_handler(func=lambda query: query.data == "slippage")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    slippage_settings = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Go back", callback_data="AB_SETTINGS")
    zo_slippage = types.InlineKeyboardButton("0.1%", callback_data="zo_slippage")
    zf_slippage = types.InlineKeyboardButton("0.5%", callback_data="zf_slippage")
    one_slippage = types.InlineKeyboardButton("1.0%", callback_data="one_slippage")
    five_slippage = types.InlineKeyboardButton("5.0%", callback_data="five_slippage")
    ten_slippage = types.InlineKeyboardButton("10.0%", callback_data="ten_slippage")
    slippage_settings.add(back, zo_slippage, zf_slippage, one_slippage, five_slippage, ten_slippage)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Adjust Slippage settings",
                           reply_markup=slippage_settings)


# slippage sub settings

@bot.callback_query_handler(func=lambda query: query.data == "zo_slippage")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_slippage(user_id, str(0.1))
    await bot.send_message(user_id, text="Updated to 0.1 % Slippage")


@bot.callback_query_handler(func=lambda query: query.data == "zf_slippage")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_slippage(user_id, str(0.5))
    await bot.send_message(user_id, text="Updated to 0.5 % Slippage")


@bot.callback_query_handler(func=lambda query: query.data == "one_slippage")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_slippage(user_id, str(1.0))
    await bot.send_message(user_id, text="Updated to 1.0 % Slippage")


@bot.callback_query_handler(func=lambda query: query.data == "five_slippage")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_slippage(user_id, str(5.0))
    await bot.send_message(user_id, text="Updated to 5.0 % Slippage")


@bot.callback_query_handler(func=lambda query: query.data == "ten_slippage")  # hiding the settings menu
async def risk_level_ping(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    trading_db.update_slippage(user_id, str(10.0))
    await bot.send_message(user_id, text="Updated to 10 % Slippage")


# other settings

@bot.callback_query_handler(func=lambda query: query.data == "AS_SETTINGS")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sub_help = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Go Back", callback_data="trading_settings2")
    sub_help.add(back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Released soon", reply_markup=sub_help)


@bot.callback_query_handler(func=lambda query: query.data == "SWD_SETTINGS")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sub_help = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Go Back", callback_data="trading_settings2")
    sub_help.add(back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Released soon", reply_markup=sub_help)


# Help info


@bot.callback_query_handler(func=lambda query: query.data == "help")  # might not need this
async def help_func(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)  # delete previous message
    user_id = int(callback_query.from_user.id)
    help_markup = types.InlineKeyboardMarkup(row_width=4)
    trading = types.InlineKeyboardButton("Trading help", callback_data="trading_help")
    sub_help = types.InlineKeyboardButton("Subscription", callback_data="subscription_help")
    talk_to_a_representative = types.InlineKeyboardButton("Speak to team", callback_data="representative")
    hide_help_menu = types.InlineKeyboardButton("Back", callback_data="settings")
    help_markup.add(trading, sub_help, talk_to_a_representative, hide_help_menu)
    await bot.send_message(user_id, "What would you want help with?", reply_markup=help_markup)


# INITIAL QUESTION OPTIONS
@bot.callback_query_handler(func=lambda query: query.data == "trading_help")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)  # delete previous message
    trading_help_markup = types.InlineKeyboardMarkup(row_width=4)
    sell_with_dev = types.InlineKeyboardButton("Sell with dev", callback_data="SWD")
    auto_buy = types.InlineKeyboardButton("Auto Buy", callback_data="AB")
    auto_sell = types.InlineKeyboardButton("Auto Sell", callback_data="AS")
    back_to_help = types.InlineKeyboardButton("Go back", callback_data="help")
    trading_help_markup.add(sell_with_dev, auto_buy, auto_sell, back_to_help)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Please select what trading feature you need "
                                                                     "help with?", reply_markup=trading_help_markup)


@bot.callback_query_handler(func=lambda query: query.data == "subscription_help")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sub_help = types.InlineKeyboardMarkup(row_width=4)
    check_expiration = types.InlineKeyboardButton("Check expiration", callback_data="CE")
    check_referral_code = types.InlineKeyboardButton("Check Referral code", callback_data="CRC")
    check_referral_stats = types.InlineKeyboardButton("Check Referral Stats", callback_data="CRS")
    back_to_help = types.InlineKeyboardButton("Go back", callback_data="help")
    sub_help.add(check_expiration, check_referral_code, check_referral_stats, back_to_help)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Subscription help,Please specify Further",
                           reply_markup=sub_help)


# subscription button info results

@bot.callback_query_handler(func=lambda query: query.data == "CE")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    user_id = int(callback_query.from_user.id)
    check_expiration_result = types.InlineKeyboardMarkup(row_width=1)
    back_to_help = types.InlineKeyboardButton("Go back", callback_data="subscription_help")
    check_expiration_result.add(back_to_help)
    check = db.check_subscription(user_id)
    if check[0] == "none" and check[1] == "none":
        await bot.send_message(user_id,
                               "error", reply_markup=check_expiration_result)
    else:
        # calculate days left and subscription type
        if str(check[0]) == "1":
            end_epoch = int(check[1]) + (3600 * 24 * 30)
            end_date = str(strftime('%Y-%m-%d %H:%M:%S', localtime(end_epoch)))
            subtype = "Monthly"
            await bot.send_message(user_id,
                                   f"⏲ you are one the {subtype} subscription\nEnd date: {end_date}",
                                   reply_markup=check_expiration_result)
        elif str(check[0]) == "2":
            end_epoch = int(check[1]) + (3600 * 24 * 90)
            end_date = str(strftime('%Y-%m-%d %H:%M:%S', localtime(end_epoch)))
            subtype = "3 Months"
            await bot.send_message(user_id,
                                   f"⏲ you are one the {subtype} subscription\nEnd date: {end_date}",
                                   reply_markup=check_expiration_result)
        else:
            await bot.send_message(user_id,
                                   "⏲ You have a Lifetime subscription.No future payments required to keep using our "
                                   "product", reply_markup=check_expiration_result)


@bot.callback_query_handler(func=lambda query: query.data == "CRC")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    user_id = int(callback_query.from_user.id)
    check_expiration_result = types.InlineKeyboardMarkup(row_width=1)
    back_to_help = types.InlineKeyboardButton("Go back", callback_data="subscription_help")
    check_expiration_result.add(back_to_help)
    referral = "AlphaPulse#" + str(user_id)
    await bot.send_message(user_id,
                           "🎟 Your Referral code is: " + referral, reply_markup=check_expiration_result)


@bot.callback_query_handler(func=lambda query: query.data == "CRS")  # check referral details
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sub_help = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Go Back", callback_data="subscription_help")
    sub_help.add(back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Soon", reply_markup=sub_help)


@bot.callback_query_handler(func=lambda query: query.data == "representative")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sub_help = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Go Back", callback_data="help")
    sub_help.add(back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="If you still are unsure about certain "
                                                                     "functionality or have any concerns please "
                                                                     "message: https://t.me/CryptoSniper000 .You "
                                                                     "should get a response within 48 hours but "
                                                                     "usually it's within minutes",
                           reply_markup=sub_help)


# TRADING QUESTION OPTIONS
@bot.callback_query_handler(func=lambda query: query.data == "SWD")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sub_help = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Go Back", callback_data="trading_help")
    sub_help.add(back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="'Sell with Dev' - This is our proprietary tool "
                                                                     "to help you escape a dump and also help you "
                                                                     "determine the top of the token.Using this "
                                                                     "option may not always yield best results as devs "
                                                                     "sometimes do take profits and push the project "
                                                                     "higher.Stay tuned for a custiomsiable "
                                                                     "option soon!", reply_markup=sub_help)


@bot.callback_query_handler(func=lambda query: query.data == "AB")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sub_help = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Go Back", callback_data="trading_help")
    sub_help.add(back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="'Auto Buy' - When enabled, it will "
                                                                     "automatically purchase a token as soon as it is "
                                                                     "pinged.You can tweak the auto buy position size "
                                                                     "to change the amount of Sol used per purchase.",
                           reply_markup=sub_help)


@bot.callback_query_handler(func=lambda query: query.data == "AS")
async def handle_button1_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sub_help = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Go Back", callback_data="trading_help")
    sub_help.add(back)
    await bot.send_message(chat_id=callback_query.from_user.id, text="'Auto Sell' - Automatically sell the Whole "
                                                                     "position at certain Roi%,Stay tuned for a More "
                                                                     "customisable version where users can Dca Sell",
                           reply_markup=sub_help)


@bot.callback_query_handler(func=lambda query: query.data == "settings")  # clone of settings
async def settings(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    user_id = int(callback_query.from_user.id)
    settings_command_buttons = types.InlineKeyboardMarkup(row_width=3)
    all_settings = types.InlineKeyboardButton("Settings", callback_data="trading_settings")
    general_help = types.InlineKeyboardButton("General help", callback_data="help")
    close_settings = types.InlineKeyboardButton("Close", callback_data="hide")
    settings_command_buttons.add(all_settings, general_help, close_settings)
    await bot.send_message(chat_id=user_id, text="📚 Access main Settings and General Help.",
                           reply_markup=settings_command_buttons)


@bot.message_handler(commands=['settings'])
async def settings(message):
    user_id = int(message.chat.id)
    settings_command_buttons = types.InlineKeyboardMarkup(row_width=3)
    all_settings = types.InlineKeyboardButton("Settings", callback_data="trading_settings2")
    general_help = types.InlineKeyboardButton("General help", callback_data="help")
    close_settings = types.InlineKeyboardButton("Close", callback_data="hide")
    settings_command_buttons.add(all_settings, general_help, close_settings)
    await bot.send_message(chat_id=user_id, text="📚 Access main Settings and General Help.",
                           reply_markup=settings_command_buttons)


# refresh info+other individual specific actions duck as buying or selling it:
@bot.callback_query_handler(func=lambda call: True)
async def help_func_callback(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    response_value = str(callback_query.data)
    token_ca = response_value.split()[1]
    msg_to_remove = callback_query.message.message_id
    if response_value.split()[0] == "refresh":
        response = query_token.main_query(token_ca)
        dev_intial_holdings = 100 - int(
            response_value.split()[2])  # percent that the ev held is 100-percent fo tokens sent to lp
        decentralisation = str(response[1]) + " % held by top 10"
        whale_holders = str(response[2])
        # ADD A DATABASE FOR DEV WALLETS
        wallet_list = wb.return_dev_wallets(token_ca).split(",")
        dev_sell = dev_sold_so_far.check_wallet_balance(wallet_list, token_ca)
        str_dev_sell = str(dev_sell).replace('.', ',')
        temp_val = -1 * (dev_sell - dev_intial_holdings)
        if temp_val > 0:
            # dev is selling
            percent_sold = "Reduced by " + str(temp_val) + " percent"
        elif temp_val < 0:
            percent_sold = "Increased by " + str(-1 * temp_val) + " percent"
            # dev is buying
        else:
            percent_sold = "Unchanged"
            # dev is buying
        refreshed_info = types.InlineKeyboardMarkup(row_width=1)
        hide_refreshed_info = types.InlineKeyboardButton("Hide", callback_data="hide_refreshed_info g")
        refreshed_info.add(hide_refreshed_info)
        # have dev selling report here i think instead a separate dev wallet
        await bot.send_message(chat_id=user_id, text=f"🤑 Refreshed Token Metrics : `{token_ca}`\nToken metrics "
                                                     f"that do not change have been omitted\n\n💳 "
                                                     f"Decentralisation :  "
                                                     f"*{decentralisation}*\n🐳 Number of whale "
                                                     f"holders : *{whale_holders}*\n💁🏽 Dev Balance: *{str_dev_sell}* Percent\n💸 Dev's balance change: *{percent_sold}*",
                               parse_mode='MarkdownV2',
                               reply_markup=refreshed_info)
    elif response_value.split()[0] == "hide_refreshed_info":
        await bot.delete_message(user_id, msg_to_remove)
    elif response_value.split()[0] == "trigger_buy":  # needs user wallet private key
        # here I will add a quick customisable amount to buy the token with
        buy_amount_keyboard = types.InlineKeyboardMarkup(row_width=6)
        buy_point_two_five = types.InlineKeyboardButton("0.25 SOLL", callback_data="025SOL " + str(token_ca))
        buy_point_five = types.InlineKeyboardButton("0.5 SOL", callback_data="05SOL " + str(token_ca))
        buy_one = types.InlineKeyboardButton("1 SOL", callback_data="1SOL " + str(token_ca))
        buy_one_point_five = types.InlineKeyboardButton("1.5 SOL", callback_data="15SOL " + str(token_ca))
        buy_two = types.InlineKeyboardButton("2 SOL", callback_data="2SOL " + str(token_ca))
        hide_refreshed_info = types.InlineKeyboardButton("Hide", callback_data="hide_refreshed_info g")
        buy_amount_keyboard.add(buy_point_two_five, buy_point_five, buy_one, buy_one_point_five, buy_two,
                                hide_refreshed_info)
        await bot.send_message(chat_id=user_id, text="💸 Please Select the amount of SOL",
                               reply_markup=buy_amount_keyboard)
        '''
        # check user trading settings
        all_settings = trading_db.return_all_settings(user_id)
        sol_amount = float(str(all_settings[3]))
        slippage = int(float(all_settings[12]))
        ekey = all_settings[2]
        await buy_jupiter.buy_token(token_ca, sol_amount, slippage, ekey, user_id)
        '''
    elif response_value.split()[0] == "trigger_sell":  # for now sell the whole position
        all_user_info = trading_db.return_all_settings(user_id)
        wallet_address = all_user_info[1]
        token_balance = int(float(query_user_wallet.return_specific_balance(token_ca, wallet_address)))
        if token_balance > 0:
            slippage = int(str((all_user_info[12])).replace(".", ""))
            ekey = all_user_info[2]
            token_decimals = response_value.split()[2]
            await buy_jupiter.sell_token(token_ca, token_balance, slippage, ekey, user_id, token_decimals)
    elif response_value.split()[0] == "rate":
        score = types.InlineKeyboardMarkup(row_width=6)
        score_one = types.InlineKeyboardButton("1", callback_data="sore_one " + str(token_ca))
        score_two = types.InlineKeyboardButton("2", callback_data="score_two " + str(token_ca))
        score_three = types.InlineKeyboardButton("3", callback_data="score_three " + str(token_ca))
        score_four = types.InlineKeyboardButton("4", callback_data="score_four " + str(token_ca))
        score_five = types.InlineKeyboardButton("5", callback_data="score_five " + str(token_ca))
        hide_refreshed_info = types.InlineKeyboardButton("Hide", callback_data="hide_refreshed_info g")
        score.add(score_one, score_two, score_three, score_four, score_five, hide_refreshed_info)
        # have dev selling report here i think instead a separate dev wallet
        await bot.send_message(chat_id=user_id, text="💯 Please Select a rating Score from 1-5 (higher is better)",
                               reply_markup=score)
    elif response_value.split()[0] == "sore_one":
        score = "1"
        if rd.check_token(token_ca):
            if not rd.check_if_user_rated(str(user_id)):  # if user not rated already
                rd.add_rating(token_ca, str(user_id), score)
        else:
            rd.add_token(token_ca)
            rd.add_rating(token_ca, str(user_id), score)
        await bot.send_message(chat_id=user_id, text="Thank you for rating!")
    elif response_value.split()[0] == "score_two":
        score = "2"
        if rd.check_token(token_ca):
            if not rd.check_if_user_rated(str(user_id)):
                rd.add_rating(token_ca, str(user_id), score)
        else:
            rd.add_token(token_ca)
            rd.add_rating(token_ca, str(user_id), score)
        await bot.send_message(chat_id=user_id, text="Thank you for rating!")
    elif response_value.split()[0] == "score_three":
        score = "3"
        if rd.check_token(token_ca):
            if not rd.check_if_user_rated(str(user_id)):
                rd.add_rating(token_ca, str(user_id), score)
        else:
            rd.add_token(token_ca)
            rd.add_rating(token_ca, str(user_id), score)
        await bot.send_message(chat_id=user_id, text="Thank you for rating!")
    elif response_value.split()[0] == "score_four":
        score = "4"
        if rd.check_token(token_ca):
            if not rd.check_if_user_rated(str(user_id)):
                rd.add_rating(token_ca, str(user_id), score)
        else:
            rd.add_token(token_ca)
            rd.add_rating(token_ca, str(user_id), score)
        await bot.send_message(chat_id=user_id, text="Thank you for rating!")
    elif response_value.split()[0] == "score_five":
        score = "5"
        if rd.check_token(token_ca):
            if not rd.check_if_user_rated(str(user_id)):
                rd.add_rating(token_ca, str(user_id), score)
        else:
            rd.add_token(token_ca)
            rd.add_rating(token_ca, str(user_id), score)
        await bot.send_message(chat_id=user_id, text="Thank you for rating!")
    elif response_value.split()[0] == "025SOL":
        # check user trading settings
        all_settings = trading_db.return_all_settings(user_id)
        sol_amount = float(0.25)
        slippage = int(float(all_settings[12]))
        ekey = all_settings[2]
        await buy_jupiter.buy_token(token_ca, sol_amount, slippage, ekey, user_id)
    elif response_value.split()[0] == "05SOL":
        # check user trading settings
        all_settings = trading_db.return_all_settings(user_id)
        sol_amount = float(0.5)
        slippage = int(float(all_settings[12]))
        ekey = all_settings[2]
        await buy_jupiter.buy_token(token_ca, sol_amount, slippage, ekey, user_id)
    elif response_value.split()[0] == "1SOL":
        # check user trading settings
        all_settings = trading_db.return_all_settings(user_id)
        sol_amount = float(1.0)
        slippage = int(float(all_settings[12]))
        ekey = all_settings[2]
        await buy_jupiter.buy_token(token_ca, sol_amount, slippage, ekey, user_id)
    elif response_value.split()[0] == "15SOL":
        # check user trading settings
        all_settings = trading_db.return_all_settings(user_id)
        sol_amount = float(1.5)
        slippage = int(float(all_settings[12]))
        ekey = all_settings[2]
        await buy_jupiter.buy_token(token_ca, sol_amount, slippage, ekey, user_id)
    elif response_value.split()[0] == "2SOL":
        # check user trading settings
        all_settings = trading_db.return_all_settings(user_id)
        sol_amount = float(2)
        slippage = int(float(all_settings[12]))
        ekey = all_settings[2]
        await buy_jupiter.buy_token(token_ca, sol_amount, slippage, ekey, user_id)
    elif response_value.split()[0] == "check_dev":
        # ADD A DATABASE FOR DEV WALLETS
        wallet_list = wb.return_dev_wallets(token_ca).split(",")
        response = check_dev_wallet_recent_tx.check_activity(wallet_list)
        time_ago = response[0]
        desc = response[1].replace(".", ",")
        hide = types.InlineKeyboardMarkup(row_width=1)
        hide_refreshed_info = types.InlineKeyboardButton("Hide", callback_data="hide_refreshed_info g")
        hide.add(hide_refreshed_info)
        await bot.send_message(chat_id=user_id,
                               text=f"🟣 For Token : *{token_ca}*\n\n💁🏽 Showing Dev's most recent activity:\n\n⌛️ "
                                    f"Time ago : *{time_ago}*\n📚"
                                    f"Description : *{desc}*", parse_mode='MarkdownV2', reply_markup=hide)


def subscription():
    pass


if __name__ == "__main__":
    threading.Thread(target=new_bot.run).start()  # starts bot on different thread
    loop = asyncio.get_event_loop()
    coros = [ping_all_subscribers(), bot.polling(non_stop=True), buy_engine()]
    loop.run_until_complete(asyncio.gather(*coros))
