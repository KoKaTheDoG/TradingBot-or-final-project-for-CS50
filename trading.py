import requests
import sqlite3
import hmac
import hashlib

from datetime import datetime

""" This will look for arbitrage on binance. 
    The idea is to generate all chains with the same start and end. 
    If it is possible to come from beginning to end at different prices, 
    a circle is formed: start -> cheap_route -> end -> expensive_route -> start """

# initialization
connection = sqlite3.connect("trading.db")
db = connection.cursor()

main_point = "https://api.binance.com"

# пример строки запроса
symbol="BTCUSDT"
side="SELL"
type_tr="LIMIT"
timeInForce="GTC"
quantity="1"
price="0.2"
timestamp="1668481559918"
recvWindow="5000"

req_str = "symbol=BTCUSDT&side=SELL&type=LIMIT&timeInForce=GTC&quantity=1&price=0.2&timestamp=1668481559918&recvWindow=5000"

# статус системы
system_status = "/sapi/v1/system/status"

# информация о всех монетах в кошельке
valet_info = "/sapi/v1/capital/config/getall"# hmac 

# статус подключения
con_stat = "/api/v3/ping"

# время сервера (нужно делить на 1000 чтобы получить адекватный результат)
server_time = "/api/v3/time"

# вроде как тут информация о символах
symbol_info = "/api/v3/exchangeInfo"

# текущая средняя цена символа
cyrent_avarage_price = "/api/v3/avgPrice"

def main():
    chains = create_chains_table()

    for item in chains:
        item["weight"] = []
        for chain in item["middle_points"]:
            item["weight"].append(price_request(item["start"], chain, item["end"]))

        min_weight = item["weight"].index(min(item["weight"]))
        max_weight = item["weight"].index(max(item["weight"]))

        item["min"] = item["middle_points"][min_weight]
        item["max"] = item["middle_points"][max_weight]
        item["route"] = [item["start"], item["min"], item["end"], item["max"], item["start"]]
        item["profit"] = (item["weight"][max_weight] - item["weight"][min_weight]) / item["weight"][max_weight]

        print(item["route"])
        print(item["profit"])
        print()
        print("=" * 100)
        print()

    
            

        



def get_from_db(data):
    """ help for db.execute(SELECT .....).fetchall()"""
    
    return [item[0] for item in data]


def create_binance_tikers_table():
    """ create table for all tikers in binance"""

    data = requests.get(main_point + symbol_info)

    data = data.json()
    data = data["symbols"]
    data = tuple([{"symbol": item["symbol"], "master": item["baseAsset"], "satelite": item["quoteAsset"] } for item in data])
    
    db.executemany("INSERT INTO binance_tikers (tiker, master, satelite) VALUES(:symbol, :master, :satelite)", data)
    connection.commit()
    

def price_request(start, middle, end):
    
    first = requests.get(main_point + cyrent_avarage_price + "?symbol=" + middle + start).json()
    first = first["price"]
    second = requests.get(main_point + cyrent_avarage_price + "?symbol=" + middle + end).json()
    second = second["price"]

    weight = 1 / float(first) * float(second)
    

    return weight


def create_chains_table():

    """ function for generation traiding chains, 
        return list of {"start":<value>, "end":<value>, "middle_points": <[list_of_values]> } """
    
    print("[  OK  ] Start generate chains")
    
    # init
    chains = []

    # get main points
    main_coins = get_from_db(db.execute("SELECT satelite FROM binance_tikers GROUP BY satelite").fetchall())
    
    # using each element in main_coins as start point, generates all posible end points as main_coins without start point
    for start in main_coins:
        
        ends = [end for end in main_coins if end != start]
        
        for end in ends:

            chains.append({"start": start, "end": end})

    print("[  OK  ] Generate base points")

    # create all middle 
    for item in chains:
        
        middle_points_for_start = get_from_db(db.execute("SELECT master FROM binance_tikers WHERE satelite = ?", (item["start"],)).fetchall())
        middle_points_for_end = get_from_db(db.execute("SELECT master FROM binance_tikers WHERE satelite = ?", (item["end"],)).fetchall())
        middle_points = [item for item in middle_points_for_start if item in middle_points_for_end and item not in main_coins]
        
        
        if len(middle_points) <= 1:
            item["middle_points"] = None

        else:
            item["middle_points"] = middle_points

    chains = [item for item in chains if item["middle_points"]]

    print("[  OK  ] Generate middle points")
    print()
    print("=" * 100)
    print()

    return chains


main()
connection.close()