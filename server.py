import socket  
from threading import Thread
import threading

ADDRESS = ('', 6688)  
socket_server = None  
thread_pool = []  # 
player_ready = []
player_start = []


def init():

    global socket_server
    global ADDRESS
    # 建立 socket
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_server.bind(('', 6688))
    socket_server.listen(10)
    print("Waiting for new player")


def accept_client():
    """
    接收新的連線
    """
    find_thread = Thread(target=find_two_player)
    find_thread.start()
    while True:
        client, _ = socket_server.accept()
        # 加入 thread pool
        thread_pool.append(client)
        thread = Thread(target=message_handle, args=(
            client, len(thread_pool)-1,))
        
        thread.setDaemon(True)
        thread.start()


def find_two_player():
    while True:
        if len(player_ready) >= 2:
            #index1 = player_ready.pop(0)
            #index2 = player_ready.pop(0)
            client1 = player_ready.pop(0)
            client2 = player_ready.pop(0)
            #client1 = thread_pool[index1]
            #client2 = thread_pool[index2]
            client1.sendall("0".encode(encoding='utf8'))
            client2.sendall("1".encode(encoding='utf8'))
            
            game1 = Thread(target=game_start, args=(client1, client2))
            game2 = Thread(target=game_start, args=(client2, client1))
            player_start.append(client1)
            player_start.append(client2)
            thread_pool.remove(client1)
            thread_pool.remove(client2)
            game1.start()
            game2.start()


def game_start(client, destination_clinet):
    """
    開始遊戲 接收client的信息然後轉傳到另一端的client
    """
    while True:
        #print(index, "waiting for message")
        bytes = client.recv(1024)
        msg = bytes.decode(encoding='utf8')
        
        # if len(msg) > 20:
        #     client.close()
        #     # 關閉連接
        #     player_start.remove(client)
        #     print("有 client 失去連接")
        #     break

        
        if msg == "over": #結束遊戲
            client.close()
            # 關閉連接
            player_start.remove(client)
            print("有 client 失去連接")
            break
        if msg == "Error":
            client.close()
            # 關閉連接
            player_start.remove(client)
            print("有 client 失去連接")
            break

        if len(bytes) == 0:
            client.close()
            # 關閉連接
            player_start.remove(client)
            print("有 client 失去連接")
            break
        # 傳給另一端的server
        destination_clinet.sendall(msg.encode(encoding='utf8'))


def message_handle(client, index):
    # 用來接收 client 按下開始遊戲的按鈕
    global thread_pool

    bytes = client.recv(1024)
    msg = bytes.decode(encoding='utf8')
    if msg == "1":
        #player_ready.append(index)
        player_ready.append(client)
        print(index, 'OK')
        # client.settimeout(0.1)
        # while client not in player_start:
        #     print('timeout')
        #     try:
        #         bytes = client.recv(1024)
        #         msg = bytes.decode(encoding='utf8')
        #         if len(msg) == 0:
        #             client.close()
        #             # 關閉連接
        #             thread_pool.remove(client)
        #             player_ready.remove(index)
        #             print("有 client 失去連接")
        #             return
        #     except socket.timeout:
        #         pass
    # elif msg == "2": 
    #     # 觀戰
    #     player_watch.append(client)
    #     thread_pool.remove(client)
    #     while len(player_start) == 0:
    #         pass
    #     watch_client = player_start()
        
    if msg == "Error":
        client.close()
        # 關閉連接
        thread_pool.remove(client)
        print("有 client 失去連接")
        return
    if len(msg) == 0:
        client.close()
        # 關閉連接
        thread_pool.remove(client)
        print("有 client 失去連接")
        return


if __name__ == '__main__':
    init()
    # 用來接受連線的thread
    thread = Thread(target=accept_client)
    thread.setDaemon(True)
    thread.start()

    
    while True:
        print("--------------------------")
        cmd = input("1:看看線上的人數\n3:關掉 ＳＥＲＶＥＲ\n")
        print("--------------------------")
        print("--------------------------")
        if cmd == '1':
            print("--------------------------")
            print("目前人數：", len(thread_pool))
            print(thread_pool)
            print("--------------------------")
            print(player_ready)
            print("--------------------------")
            print(player_start)
        elif cmd == '3':
            exit()
