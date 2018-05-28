#!/usr/bin/env python
from threading import Thread
from bottle    import get, post, run, request
from time      import sleep
from sys       import exit, argv
from strategy  import Strategy

import requests

port         = 8090
username     = 'insert here your bot username, find it at https://www.pokerwars.io/profile'
api_token    = 'insert here your api token, find it at https://www.pokerwars.io/token'
bot_endpoint = 'insert here your bot ip address. i.e.: http://1.2.3.4:8090/'

strategy_option = 333  # Can be overwritten by console argument

@post('/pokerwars.io/play')
def play():
    # This endpoint is called by pokerwars.io to request your bot next move on a tournament.
    # You have the current state of the table in the game_info object, which you can use to decide
    # your next move.
    game_info = request.json
    print('Game info received for tournament ' + str(game_info["tournamentId"]) + ' and round ' + str(game_info["roundId"]) + ', let\'s decide the next bot move for this hand')
    print('Current round turn is ' + str(game_info["roundTurn"]))
    print('Cards on the table are ' + str(game_info["tableCards"]))
    print('Your bot cards are ' + str(game_info["yourCards"]))

    action = Strategy.decide_action(game_info, strategy_option)

    if game_info["canCheckOrBet"]:
        # remember: in poker you can check or bet only if in the current turn no bot has bet already
        # if a bot bet already, you'll need to call or raise.
        print('In this hand, your bot can check or bet')
        print('If you bet, the minimum bet is ' + str(game_info["minBet"]))

    if game_info["canCallOrRaise"]:
        # remember: in poker you can call or raise only if there has been a bet before
        print('In this hand, your bot can call or raise')
        print('If you call, you will spend ' + str(game_info["chipsToCall"]) + ' chips')
        print('If you raise, the minimum raise is ' + str(game_info["minRaise"]))

    print('The value of small blind now is ' + str(game_info["smallBlindValue"]))
    print('The value of big blind now is ' + str(game_info["bigBlindValue"]))
    print('Small blind player is ' + str(game_info["smallBlindPlayer"]))
    print('Big blind player is ' + str(game_info["bigBlindPlayer"]))
    print('Players in turn order with their info are: ' + str(game_info["players"]))

    # implement your strategy here, now we always return fold, not great for your leaderboard!
    print('Action -------> ' + str(action))
    return action

@get('/pokerwars.io/ping')
def ping():
    # This is used by pokerwars.io when your bot subscribe to verify that is alive and responding
    print('Received ping from pokerwars.io, responding with a pong')
    return {"pong": True}

@post('/pokerwars.io/notifications')
def notifications():
    notification = request.json
    print('Received notification -------> ' + str(notification["type"]))
    print('Received notification -------> ' + str(notification["message"]))
    return

def subscribe():
    down = True

    while down:
        try:
            print('Trying to subscribe to pokerwars.io ...')
            r = requests.get(bot_endpoint + 'pokerwars.io/ping')

            if r.status_code == 200:
                down = False

                json = {
                    'username': username,
                    'token': api_token,
                    'botEndpoint': bot_endpoint
                }

                r = requests.post('https://play.pokerwars.io/v1/pokerwars/subscribe', json)

                print('Subscription --> Status code: ' + str(r.status_code))
                print('Subscription --> Body: ' + str(r.json()))

                if r.status_code != 202:
                    print('Failed to subscribe, aborting ...')
                    exit()
        except:
            exit()

        sleep(2)

def validate_strategy():
    if len(argv) == 1:
        strategy_option = str(strategy_option)
        print('|------ Strategy selected (default): ' + strategy_option)
        print('|------ Aggressiveness factor: ' + strategy_option[0])
        print('|------ Bluffing factor: ' + strategy_option[1])
        print('|------ Bet/Raise factor: ' + strategy_option[2])

        return

    if len(argv) != 2:
        print('Illegal number of arguments [max 1 argument], aborting ...')
        exit(1)

    try:
        if 111 <= int(argv[1]) <= 555:
            global strategy_option
            strategy_option = argv[1]
            print('|------ Strategy selected: ' + strategy_option)
            print('|------ Aggressiveness factor: ' + strategy_option[0])
            print('|------ Bluffing factor: ' + strategy_option[1])
            print('|------ Bet/Raise factor: ' + strategy_option[2])
            return

        print('Illegal number of arguments [max 1 argument], aborting ...')
        exit(1)
    except ValueError:
        print('Illegal choice of strategy [not in range 111 - 555], aborting ...')
        exit(1)

if __name__ == '__main__':
    validate_strategy()
    s = Thread(target=subscribe)
    s.daemon = True
    s.start()

    run(host='0.0.0.0', port=port)
