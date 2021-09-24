from mod.headerx import *

form_class = uic.loadUiType("mr.ui")[0]

class Worker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True

    def do_work(self):
        while True:
            data = []
            data = self.risk_monitoring()
            self.finished.emit(data)
            QThread.sleep(60)

    def risk_monitoring(self):
        data=[0 for i in range(0,3)]
        ret=MarketRiskUtil.get_vix()
        ret2=MarketRiskUtil.get_2xinverse()
        ret3=MarketRiskUtil.get_hsi()
       
        data[0]=ret['closePrice']
        data[1]=round(float(ret2['dayCandles'][0]['changePriceRate'])*100,2)
        data[2]=round(float(ret3['recentSecurity']['changePriceRate'])*100,2)
        
        return data

    def stop_work(self):
        self.continue_run = False

class MyWindowClass(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.update_widget)
        self.thread.started.connect(self.worker.do_work) 
        self.thread.finished.connect(self.worker.stop_work)
        self.Monitorbutton.clicked.connect(self.run_thread)
        self.Exitbutton.clicked.connect(self.stop_thread)
        self.show()


    def run_thread(self):
        self.thread.start()
        self.today=date.today()
        self.Maindatalabel.setText(str(self.today))

        with open('fomc.txt') as f:
            first_line = f.readline()

        self.targetday = datetime.strptime(first_line, '%Y-%m-%d').date()
        self.values = self.targetday - self.today
        self.Fomcnumlabel.setText(str(self.targetday))
        self.Fomcjudgelabel.setText(str(self.values))

    def update_widget(self,data):
        self.VixnumLabel.setText(data[0])
        self.Inversenumlabel.setText(str(data[1]))
        self.Hsinumlabel.setText(str(data[2]))

        if float(data[0])>=35:
            self.Vixjudgelabel.setStyleSheet("color: red;border: 1px solid black;")
            self.Vixjudgelabel.setText("RISK")
        else:
            self.Vixjudgelabel.setStyleSheet("color: green")
            self.Vixjudgelabel.setText("NORMAL")

        if float(data[1])>=1.5:
            self.Inversejudgelabel.setStyleSheet("color: red;border: 1px solid black;")
            self.Inversejudgelabel.setText("RISK")
        else:
            self.Inversejudgelabel.setStyleSheet("color: green")
            self.Inversejudgelabel.setText("NORMAL")

        if float(data[2])<=-1.5:
            self.Hsijudgelabel.setStyleSheet("color: red;border: 1px solid black;")
            self.Hsijudgelabel.setText("RISK")
        else:
            self.Hsijudgelabel.setStyleSheet("color: green")
            self.Hsijudgelabel.setText("NORMAL")


    def stop_thread(self):
        self.thread.terminate()
        QCoreApplication.instance().quit()
        # print(values.days)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyWindowClass()
    myWindow.show()
    app.exec_()
