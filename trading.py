import requests
import sqlite3
import hmac
import hashlib

from datetime import datetime

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

def create_binance_tikers_table():
    """ create table for all tikers in binance"""

    data = requests.get(main_point + symbol_info)

    data = data.json()
    data = data["symbols"]
    data = tuple([{"symbol": item["symbol"], "master": item["baseAsset"], "satelite": item["quoteAsset"] } for item in data])
    
    db.executemany("INSERT INTO binance_tikers (tiker, master, satelite) VALUES(:symbol, :master, :satelite)", data)
    connection.commit()
    
    connection.close()
      
    return True
    

def price_request():
    data = db.execute("SELECT id, tiker FROM binance_tikers").fetchall()
    data = [{"id": item[0], "tiker": item[1]} for item in data]

    for item in data:

        price_request = requests.get(main_point + cyrent_avarage_price + "?symbol=" + item["tiker"]).json()

        query = ("INSERT INTO binance_prices (tiker_id, cyrent_price) VALUES (?, ?)")
        
        query = db.execute(query, (item["id"], price_request["price"]))


def temp():