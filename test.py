import requests
import hmac
import hashlib

from datetime import datetime


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

    data = requests.get(main_point + symbol_info)

    print("request code : ")
    print(data.status_code)
    print("request headers : ")
    print(data.headers)
    print("request body : ")
    data = data.json()
    data = data["symbols"]
    data = [item["symbol"] for item in data]
    
    for item in data:
        print(requests.get(main_point + cyrent_avarage_price + "?symbol=" + item).json())

    
print(requests.get(main_point + cyrent_avarage_price + "?symbol=BEAMUSDT").json())
