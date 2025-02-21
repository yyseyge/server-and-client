import socketserver
import threading
from doctest import master

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

        if msg[0] == '*':
            print("강퇴")
            Leaderhandler.out("[%s] %s" % (userID, msg))
            return


        if msg.strip() == '/quit':
            self.removeuser(userID)
            return -1


    def sendMessageToOne(self,msg):
        try:
            who=msg.split()
            print(msg)
            sendWho=who[3]
            print(sendWho, '누가받냐')

            msg=who[4]
            print(msg,'뭔내용')

            for i in self.userdict.keys():
                if i == sendWho:
                    conn=self.userdict[i][0]
                    print(conn)
                    conn.send(msg.encode())
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
            msg = self.request.recv(1024)
            while msg:
                if self.umg.messagehandler(userID, msg.decode()) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)
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


    def out(self, userID, msg):
        master = self.umg.userdict[0]
        print(master)
        if userID == master:
            msg.split
            msg[2]
        if userID == "*":
            pass
        if msg == "*":
            pass









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