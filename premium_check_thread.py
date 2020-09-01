import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import requests
import pyupbit
import pybithumb
import ccxt


tickers = ["BTC", "ETH", "BCH", "LTC", "XRP", "TRX", "ADA", "EOS", "XLM", "LINK"]
form_class = uic.loadUiType("premium.ui")[0]

r = requests.get("https://earthquake.kr:23490/query/USDKRW")
currency = r.json()
usd_krw = currency["USDKRW"][0]


class Worker(QThread):
    finished = pyqtSignal(dict)

    def run(self):
        while True:
            data = {}

            for ticker in tickers:
                data[ticker] = self.get_market_info(ticker)

            self.finished.emit(data)
            self.msleep(500)

    def get_market_info(self, ticker):
        try:
            upbit_price = pyupbit.get_current_price("KRW-" + ticker)
            upbit_price_usd = "%.2f" % round(upbit_price / usd_krw, 2)

            bithumb_price = pybithumb.get_current_price(ticker)
            bithumb_price_usd = "%.2f" % round(bithumb_price / usd_krw, 2)

            binance = ccxt.binance()
            binance_ticker = binance.fetch_ticker(ticker + "/USDT")
            binance_price = binance_ticker["close"]

            binance_price_krw = int(binance_price * usd_krw)

            upbit_premium = "%.2f" % round((upbit_price / usd_krw) - binance_price, 2)
            bithumb_premium = "%.2f" % round((bithumb_price / usd_krw) - binance_price, 2)

            return upbit_price, upbit_price_usd, bithumb_price, bithumb_price_usd, \
                binance_price, binance_price_krw, upbit_premium, bithumb_premium
        except:
            return None, None, None, None, None, None, None, None


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tableWidget.setRowCount(len(tickers))
        self.worker = Worker()
        self.worker.finished.connect(self.update_table_widget)
        self.worker.start()

    @pyqtSlot(dict)
    def update_table_widget(self, data):
        try:
            for ticker, infos in data.items():
                index = tickers.index(ticker)

                self.tableWidget.setItem(index, 0, QTableWidgetItem(ticker))
                self.tableWidget.setItem(index, 1, QTableWidgetItem(str(infos[0])))
                self.tableWidget.setItem(index, 2, QTableWidgetItem(str(infos[1])))
                self.tableWidget.setItem(index, 3, QTableWidgetItem(str(infos[2])))
                self.tableWidget.setItem(index, 4, QTableWidgetItem(str(infos[3])))
                self.tableWidget.setItem(index, 5, QTableWidgetItem(str(infos[4])))
                self.tableWidget.setItem(index, 6, QTableWidgetItem(str(infos[5])))
                self.tableWidget.setItem(index, 7, QTableWidgetItem(str(infos[6])))
                self.tableWidget.setItem(index, 8, QTableWidgetItem(str(infos[7])))
        except:
            pass


app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()
