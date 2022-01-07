import sys
import socket
import threading
import time
import numpy
from PyQt5 import QtWidgets, QtGui, QtCore

from UI import Ui_MainWindow
#from datetime import datetime
# 903 604
chat = ['歡迎加入聊天室\n']
class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()  # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

    def setup_control(self):

        # TODO
        # qpushbutton doc: https://doc.qt.io/qt-5/qpushbutton.html
        
        # self.ui.push123.clicked.connect(self.close)
        # self.ui.push123.clicked.connect(self.buttonClicked)
        # self.ui.push123.mousePressEvent = self.show_mouse_press 
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.start_button.clicked.connect(self.execute)
        self.ui.login_button.clicked.connect(self.login)
        
        # self.ui.start.setStyleSheet("background-image: url(bg.jpg);")

        #self.ui.start_button.hide()
        #pixmap = QtGui.QPixmap('blue.png')
        #self.ui.game_title.setPixmap(pixmap)
        pixmap = QtGui.QPixmap('img/chessboard.png')
        self.ui.chessboard.setPixmap(pixmap)
        pixmap = QtGui.QPixmap('img/title.png')
        self.ui.game_title.setPixmap(pixmap)
        
        pixmap = QtGui.QPixmap('img/win_title.png')
        self.ui.win_title.setPixmap(pixmap)
        pixmap = QtGui.QPixmap('img/kabowin.png')
        self.ui.win_capoo.setPixmap(pixmap)
        pixmap = QtGui.QPixmap('img/lose_title.png')
        self.ui.lose_title.setPixmap(pixmap)
        pixmap = QtGui.QPixmap('img/kabolose.png')
        self.ui.lose_capoo.setPixmap(pixmap)

        self.ui.chatroom.setText("".join(chat))
        self.ui.chat_send.clicked.connect(send_chat)
        self.ui.back_homepage.clicked.connect(self.back_homepage)
        self.ui.back_homepage_2.clicked.connect(self.back_homepage)

        self.ui.login_button.hide()
        self.ui.watch_button.hide()

        for i in range(16):
            for j in range(16):
                label_tmp = QtWidgets.QLabel(self.ui.game)
                label_tmp.setGeometry(QtCore.QRect(chessX[i]-12, chessY[j]-12, 25, 25))
                label_tmp.setObjectName(f"label{i}-{j}")
                # label_tmp.setText('1')
                #label_tmp.setStyleSheet("background-color: rgb(255,0,255);")
        #for checkstate in self.findChildren(QtWidgets.QLabel):
            #print(f'get check state:{checkstate.objectName()}')
        #print(self.findChildren(QtWidgets.QLabel,"label44")[0].text())


        # self.ui.label2 = QtWidgets.QLabel(self.ui.start)
        # self.ui.label2.setGeometry(QtCore.QRect(180, 60, 145, 49))
        # self.ui.label2.setObjectName("label2")
        # self.ui.label2.setText('111111123131')
        self.re = receive()
    
    def login(self):
        self.ui.stackedWidget.setCurrentIndex(1)
    
    # 滑鼠點擊事件
    def mousePressEvent(self,event):
        global waiting
        if waiting == True:
            pass
            print('waiting')
            return
        
        if event.button() == QtCore.Qt.LeftButton:
            print('x: ', event.x(), 'y: ', event.y())
            i, j = self.find_chess(event.x(), event.y())
            print('i,j:',i,j)
            if i != -1 and j != -1 and board[i, j] == 0:
                # new qizi
                waiting = True
                msg = "b" + str(i)+" "+str(j)
                print(msg)
                client.sendall(msg.encode('utf-8'))

                latestX = i
                latestY = j

                if black_player:
                    board[i, j] = 1
                    pixmap = QtGui.QPixmap('img/blue.png')
                else:
                    board[i, j] = 2
                    pixmap = QtGui.QPixmap('img/rabbit.png')
                chat.append('你下棋：' + str(i+1) + '-' + str(j+1) + '\n')
                self.ui.chatroom.setText("".join(chat))
                self.display_chess(i,j,pixmap)
                self.ui.waiting_status.setText("waiting")
                self.check_winner()    
            #print('left')
            print('wait status:',waiting)

    def find_chess(self,x,y):
        radius = 10
        chess_index_X = -1
        chess_index_Y = -1

        min_dist_x = 999
        min_dist_y = 999

        for i in range(16):
            if numpy.abs(chessX[i] - x) < min_dist_x:
                min_dist_x = numpy.abs(chessX[i] - x)
                chess_index_X = i
            if numpy.abs(chessY[i] - y) < min_dist_y:
                min_dist_y = numpy.abs(chessY[i] - y)
                chess_index_Y = i
        if min_dist_x < radius and min_dist_y < radius:
            return chess_index_X,chess_index_Y
        return -1,-1
    # receive的thread開始執行
    
    def display_chess(self,i,j,pixmap):
        self.findChildren(QtWidgets.QLabel, f"label{i}-{j}")[0].setPixmap(pixmap)
    
    def execute(self):
        self.re.start()
        self.re.set_chat.connect(self.display_chat)
    def display_chat(self,str):
        self.ui.chatroom.setText(str)
        #TODO 聊天室滾動到最底下

    def back_homepage(self):
        global chat
        chat = ['歡迎加入聊天室\n']
        self.ui.setupUi(self)
        self.setup_control()
        self.ui.stackedWidget.setCurrentIndex(0)
        init_game()
    
    def check_winner(self):
        global waiting
        result = find_five_son()
        if result != 0:
            waiting = True
            
            msg = "over"
            # print('send!!!')
            client.sendall(msg.encode('utf-8'))
            if (result == 1 and black_player) or (result == 2 and not black_player):
                # win
                thread = threading.Thread(target=self.win_display)
                thread.start()
                #self.win_display()
                # self.ui.waiting_status.setText("恭喜獲勝")
                # time.sleep(4)
                # self.ui.stackedWidget.setCurrentIndex(4)
            else:
                # lose
                self.ui.waiting_status.setText("可惜敗北")
                time.sleep(4)
                self.ui.stackedWidget.setCurrentIndex(5)
    def win_display(self):
       self.ui.waiting_status.setText("恭喜獲勝")
       time.sleep(4)
       self.ui.stackedWidget.setCurrentIndex(4)
# ================================================================

def init_game():
    global black_player,waiting,board,chessX,chessY
    black_player = True
    waiting = True 
    board = numpy.zeros((16,16))
    # board size 為 603x604
    chessX = numpy.linspace(10, 603, 16)
    chessY = numpy.linspace(10, 604, 16)
    # connect to server
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 6688))

    

class receive(QtCore.QThread):
    #set_index = QtCore.pyqtSignal(int)
    set_chat = QtCore.pyqtSignal(str)
    def __init__(self):
        super(receive, self).__init__()

    def run(self):
        #
        print('waiting')
        window.ui.stackedWidget.setCurrentIndex(2)
        global black_player, waiting
        data = "1"
        data = data.encode('utf-8')
        #global client
        print('send!!!')
        client.sendall(data)
        waiting = True
        # server 會傳訊息跟第一位玩家說第二位玩家來了沒
        while True:
            msg = client.recv(1024).decode('utf8')
            # 0 為黑方
            if msg == "0":
                print('game Start:', msg)
                waiting = False
                window.ui.waiting_status.setText("Your turn")
                break
            else:
                print('game Start:', msg)
                #global blac_player, waiting
                black_player = False
                waiting = True
                # global mynumber
                # mynumber = 1
                break
        
        window.ui.stackedWidget.setCurrentIndex(3)
        # 等待完畢 開始遊戲
        while True:
            print("I'm waiting for the first message")
            rec_data = client.recv(1024).decode(encoding='utf8')
            print(rec_data)
            # 判斷開頭字元 'b' 為下棋訊息 'c'為聊天訊息
            if len(rec_data) == 0:
                #xerver close
                break
            if rec_data[0] == 'b':
                rec_data = rec_data[1:].split()
                if black_player:
                    board[int(rec_data[0]), int(rec_data[1])] = 2
                    pixmap = QtGui.QPixmap('img/rabbit.png')
                else:
                    board[int(rec_data[0]), int(rec_data[1])] = 1
                    pixmap = QtGui.QPixmap('img/blue.png')
                waiting = False
                window.display_chess(int(rec_data[0]), int(rec_data[1]), pixmap)
                chat.append('對手下棋：' + str(int(rec_data[0])+1) + '-' + str(int(rec_data[1])+1) + '\n')
                self.set_chat.emit("".join(chat))
                window.ui.waiting_status.setText("Your turn")
                window.check_winner()    
                
                #break
            elif rec_data[0] == 'c':
                rec_data = rec_data[1:]
                chat.append('對手：'+rec_data+'\n')
                self.set_chat.emit("".join(chat))

#檢查是否有五子連線
def find_five_son():
    global board
    # 遍歷所有方向
    ways = [
        [[-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0]],
        [[-2, -2], [-1, -1], [0, 0], [1, 1], [2, 2]],
        [[0, -2], [0, -1], [0, 0], [0, 1], [0, 2]],
        [[-2, 2], [-1, 1], [0, 0], [1, -1], [2, -2]]
    ]
    for i in range(2, 14):
        for j in range(2, 14):
            # 黑白雙方（t=1、2）
            for t in range(1, 3):
                # 四個方向
                for index in range(4):
                    if (board[i+ways[index][0][0], j+ways[index][0][1]] == t
                        and board[i+ways[index][1][0], j+ways[index][1][1]] == t
                        and board[i+ways[index][2][0], j+ways[index][2][1]] == t
                        and board[i+ways[index][3][0], j+ways[index][3][1]] == t
                            and board[i+ways[index][4][0], j+ways[index][4][1]] == t):
                        return t
    # 遍歷邊界
    index = 2
    for i in range(0, 16):
        for j in range(2, 14):
            for t in range(1, 3):
                if (board[i+ways[index][0][0], j+ways[index][0][1]] == t
                    and board[i+ways[index][1][0], j+ways[index][1][1]] == t
                    and board[i+ways[index][2][0], j+ways[index][2][1]] == t
                    and board[i+ways[index][3][0], j+ways[index][3][1]] == t
                        and board[i+ways[index][4][0], j+ways[index][4][1]] == t):
                    return t
    index = 0
    for i in range(2, 14):
        for j in range(0, 16):
            for t in range(1, 3):
                if (board[i+ways[index][0][0], j+ways[index][0][1]] == t
                    and board[i+ways[index][1][0], j+ways[index][1][1]] == t
                    and board[i+ways[index][2][0], j+ways[index][2][1]] == t
                    and board[i+ways[index][3][0], j+ways[index][3][1]] == t
                        and board[i+ways[index][4][0], j+ways[index][4][1]] == t):
                    return t

    return 0


# 傳送聊天訊息
def send_chat():
    chat_message = window.ui.chat_input.toPlainText()
    # window.ui.chat_input.toPlainText()
    window.ui.chat_input.setPlainText('')
    chat.append('你：' + chat_message + '\n')
    window.ui.chatroom.setText("".join(chat))
    client.sendall(('c'+chat_message).encode('utf-8'))


if __name__ == '__main__':
    
    init_game()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.show()
    sys.exit(app.exec_())
