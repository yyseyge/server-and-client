import socketserver
import threading
from doctest import master
from threading import Thread
import datetime
import random

import pymysql

HOST='192.168.0.20'
PORT=9900
lock=threading.Lock() #동기화 진행 스레드
class usermg:
    def __init__(self):
        self.userdict={}
    def adduser(self,userID,conn,addr):
        if userID in self.userdict:  # username이 딕셔너리에 존재하면
            conn.send("등록된 사용자".encode())  # send()함수는 보낸다. recv() 받는다
            return None
        lock.acquire()  # lock의 기능을 스레드의 동시다발적인 접속을 잠궈서 막고 풀고 하는거다.
        self.userdict[userID] = (conn,addr)
        lock.release()
        self.sendMessageToAll('[%s]접속' % userID)
        return userID

    def removeuser(self,userID):
        if userID not in self.userdict:
            return
        lock.acquire()
        del self.userdict[userID]  # 유저를 삭제하는 행위, 여기서 lock객체를 잠궜다 풀었다 하고 있다.
        lock.release()
        self.sendMessageToAll('[%s]접속해제' % userID)
        print('대화 참여 수 [%d]' % len(self.userdict))

    def messagehandler(self,userID,msg):
        if msg[0] != '/' and msg[0] != '*':
            self.sendMessageToAll("[%s] %s" % (userID, msg))
            return
        if msg[0] == '/':
            self.sendMessageToOne("[%s] >>> %s" % (userID, msg))
            return
        if msg.strip() == '/quit':
            self.removeuser(userID)
            return -1


    def sendMessageToOne(self,msg):
        try:
            who=msg.split()
            print(msg)

            sendWho=who[0]
            print(sendWho, '누가 보냄')

            recvWho=who[3]
            print(recvWho, '누가받냐')

            msg=who[4]
            msg2 = '>>>' + msg
            msg3 = '<<<' + msg

            print(msg2,'뭔내용')
            print(msg3,'뭔내용')

            for i in self.userdict.keys():
                if i == recvWho:
                    conn=self.userdict[i][0]
                    print(conn)
                    conn.send(msg2.encode())
                if [i] == sendWho:
                    print([i])
                    conn = self.userdict[i][0]
                    print(conn)
                    conn.send(msg3.encode())
                else:
                    pass
        except:
            pass

    def sendMessageToAll(self,msg):
        for conn, addr in self.userdict.values():
            conn.send(msg.encode())


class myTcpHandler(socketserver.BaseRequestHandler):
    umg = usermg()
    def handle(self):
        try:
            userID=self.registerUsername()
            DATE=datetime.datetime.now()
            master = random.randint(0,1)
            print(userID)
            print(master)


            msg = self.request.recv(1024)
            while msg:
                if self.umg.messagehandler(userID, msg.decode()) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)
                DB = self.update_user_in_db(userID, DATE,msg,master)
                print(msg,'msg 입니다')


        except Exception as e:
            print(e)
            self.umg.removeuser(userID)

    def registerUsername(self):
        while True:  # 계속 반복문 돌면서
            userID = self.request.recv(1024)  # client한테 처음 받는건 username 변수에 저장해놓음
            userID = userID.decode().strip()  # username에 decode하고 공백제거해서 다시 저장
            if self.umg.adduser(userID, self.request,self.client_address):  # self의 userman class에 addUser함수 호출 매개변수로  username이랑,client 소켓 객체랑 client 주소 줌
                return userID

    def update_user_in_db(self, userID, DATE, msg,master):
        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            # 데이터베이스 생성 및 사용
            cursor.execute("CREATE DATABASE IF NOT EXISTS server1_1")
            cursor.execute("USE server1_1")

            # membermg 테이블 생성 (유저 관리)
            cursor.execute("""
                      CREATE TABLE IF NOT EXISTS membermg (
                          userID VARCHAR(255) NOT NULL, 
                          `Date` VARCHAR(255) NOT NULL,
                          master INT NOT NULL,
                          PRIMARY KEY(userID)   
                      )
                  """)

            # chatting 테이블 생성 (채팅 관리)
            cursor.execute("""
                      CREATE TABLE IF NOT EXISTS chatting (
                          userID VARCHAR(255) NOT NULL,
                          msg VARCHAR(255) NOT NULL
                      )
                  """)

            # 유저 데이터 삽입
            cursor.execute("INSERT IGNORE INTO membermg (userID, `Date`,master) VALUES (%s, %s,%d)", (userID, DATE,master))

            # 채팅 데이터 삽입
            cursor.execute("INSERT INTO chatting (userID,msg) VALUES (%s,%s)", (userID,msg))

            # 변경 사항 저장
            connection.commit()

        except Exception as e:
            print("Database Error:", e)

        finally:
            cursor.close()
            connection.close()

    def get_db_connection(self):
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='0000',
                                     port=3306,
                                     charset='utf8mb4')

        return connection




class chattingServer(socketserver.TCPServer,socketserver.ThreadingMixIn):
    pass


def startServer():
    try:
        server=chattingServer((HOST,PORT),myTcpHandler)
        server.serve_forever()

    except KeyboardInterrupt:
        print("서버 종료되었습니다")
        server.shutdown()
        server.server_close()



startServer()