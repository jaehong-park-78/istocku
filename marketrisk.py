from mod.headerx import *

form_class = uic.loadUiType("mr.ui")[0]

class Worker(QThread):
    finished = pyqtSignal(list)
    progressed = pyqtSignal(int)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True

    def run_work(self):
        data = []
        i=0
        while self.continue_run:
            i+=1
            if i==5:
                i=0
            self.progressed.emit(i)
            data = self.risk_monitoring()
            self.finished.emit(data)
            QThread.sleep(1)

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
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.progressed.connect(self.loop_test)
        self.worker.finished.connect(self.update_widget)
        self.thread.started.connect(self.worker.run_work) 
        self.thread.finished.connect(self.worker.stop_work)
        self.Monitorbutton.clicked.connect(self.run_thread)
        self.Monitorbutton.setCheckable(True)
        self.Monitorbutton.toggle()
        self.Hidebutton.clicked.connect(self.hide_app)
        self.Exitbutton.clicked.connect(self.exit_app)
        
    def run_thread(self,*args):
        # import pdb; pdb.set_trace()
        if not self.Monitorbutton.isChecked():
            self.Monitorbutton.setText("STOP")
            self.worker.continue_run = True
            self.thread.start()
        
            self.today=date.today()
            self.Maindatalabel.setText(str(self.today))

            with open('fomc.txt') as f:
                first_line = f.readline()

            self.targetday = datetime.strptime(first_line, '%Y-%m-%d').date()
            self.values = self.targetday - self.today
            self.Fomcnumlabel.setText(str(self.targetday))
            self.Fomcjudgelabel.setText(str(self.values))
        else:
            self.Monitorbutton.setText("Monitoring")
            self.thread.terminate()
            self.worker.continue_run = False

    def stop_thread(self):
        self.thread.terminate()
        self.worker.continue_run = False

    def hide_app(self):
        self.showMinimized()

    def exit_app(self):
        QCoreApplication.instance().quit()

    def loop_test(self,i):
        loading="+" if i%2 else '-' 
        self.Looplabel.setText(str(loading))

    def update_widget(self,data):
        vix=data[0]
        inverse2x=data[1]
        hsi=data[2]
        self.VixnumLabel.setText(str(vix))
        self.Inversenumlabel.setText(str(inverse2x))
        self.Hsinumlabel.setText(str(hsi))

        if float(vix)>=35:
            self.Vixjudgelabel.setStyleSheet("color: red;border: 1px solid black;")
            self.Vixjudgelabel.setText("RISK")
        else:
            self.Vixjudgelabel.setStyleSheet("color: green")
            self.Vixjudgelabel.setText("NORMAL")

        if float(inverse2x)>=1:
            self.Inversejudgelabel.setStyleSheet("color: red;border: 1px solid black;")
            self.Inversejudgelabel.setText("RISK")
        else:
            self.Inversejudgelabel.setStyleSheet("color: green")
            self.Inversejudgelabel.setText("NORMAL")

        if float(hsi)<=-1:
            self.Hsijudgelabel.setStyleSheet("color: red;border: 1px solid black;")
            self.Hsijudgelabel.setText("RISK")
        else:
            self.Hsijudgelabel.setStyleSheet("color: green")
            self.Hsijudgelabel.setText("NORMAL")

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyWindowClass()
    myWindow.show()
    app.exec_()
