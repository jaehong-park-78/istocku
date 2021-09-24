from mod.headerx import *

class MarketRiskUtil(object):
    def __init__():
        init=True

    @classmethod
    def get_vix(cls):
        r=requests.get("https://api.stock.naver.com/index/.VIX/basic")
        return r.json()

    @classmethod
    def get_2xinverse(cls):
        r=requests.get("https://stockplus.com/api/securities/KOREA-A252670/day_candles.json?limit=20")
        return r.json()

    @classmethod
    def get_hsi(cls):
        r=requests.get("https://stockplus.com/api/securities/HONGKONG-HSI.json")
        return r.json()

        