#서버와 클라이언트 통신
#클라이언트 사이드


#GUI : tkinter / ttk / QT
#TCP & SOCKET : 통신 기반

#TCP transmisson control protocol로 통신 규칙
#TCP 특징 : 연결 지향적 -> TCP는 데이터를 보내기 전 서버와 클라이언트가 서로 확인 절차 (3way 핸드셰이크)가 있음.
#3way핸드셰이크로 서로 확인 후 데이터에 대한 전송이 이루어짐
#데이터 전송 신뢰성이 높다 : TCP는 데이터가 정확하게 전달되도록 보장해줌
#예를들어 데이터가 전송 중 끊기거나 잘못 전달되면 다시 보내는 등 처리를 함

#순서를 보장해줌(보내는 데이터가 엉키지 않도록)
#보내고자하는 데이터가 12345 인 경우
#여러 환경적 이유로 13245 등 데이터가 꼬이는 현상이 발생할 수 있는데, TCP는 이런 현상을 방지해줌

#흐름제어
#(tick으로 양방향에서의 박자를 맞추는 것 처럼 서버와 클라이언트가 서로 데이터 송수신과정을 소화할 수 있는 흐름으로 제어)




#3way handshake
#TCP 연결시 3웨이핸드셰이크 상세 과정
#1.syn (송신자의 연결 요청)
#2.syn-ack(수신자의 연결 요청 수락)
#3.ack(송신자의 연결 확인)



#TCP의 연결 종료시 4way handshake과정으로 처리함
#1.한쪽에서 연결종료 요청(FIN)
#2.상대방은 1번 요청을 확인 (ACK)
#3.상대방도 종료 준비가 되면 연결 종료 요청을 보냄(FIN)
#4.송신자는 그 요청을 확인하고 연결을 완전히 종료 (ACK)



#위 특징들로 TCP는 데이터가 정확하고 , 손실없이 송수신과정에서 신뢰성을 보장받으며 통신할 수 있도록 하는 규약

import socketserver #소켓서버 모듈을 불러온다.
import threading
HOST='localhost'
PORT=9900
lock=threading.Lock() #동기화 진행 스레드
class UserManager: #user관리하는 class
    def __init__(self): #속성에 users라는 딕셔너리있음
        self.users={}
    def addUser(self,username,conn,addr): #user추가하는 함수, 매개변수로 username,주소,conn받음(conn은 리퀘스틑 객체이다. request는 클라이언트 객체이다. )
        if username in self.users: #username이 딕셔너리에 존재하면
            conn.send("등록된 사용자".encode()) #send()함수는 보낸다. recv() 받는다
            return None
        lock.acquire() #lock의 기능을 스레드의 동시다발적인 접속을 잠궈서 막고 풀고 하는거다.
        self.users[username]=(conn,addr)
        lock.release()
        self.sendMessageToAll('[%s]접속' % username)
        print('대화 참여 수 [%d]'% len(self.users))
        return username
    def removeUser(self,username):
        if username not in self.users:
            return
        lock.acquire()
        del self.users[username] #유저를 삭제하는 행위, 여기서 lock객체를 잠궜다 풀었다 하고 있다.
        lock.release()
        self.sendMessageToAll('[%s]접속해제'%username)
        print('대화 참여 수 [%d]'%len(self.users))
    def messageHandler(self,username,msg):
        if msg[0]!='/':
            self.sendMessageToAll("[%s] %s"%(username,msg))
            return
        if msg.strip()=='/quit':
            self.removeUser(username)
            return -1
    def sendMessageToAll(self,msg):
        print(threading.active_count())
        for conn,addr in self.users.values():
            conn.send(msg.encode())
class myTcpHandler(socketserver.BaseRequestHandler): #socketserver 모듈에 내장된 BaseRequestHandler class를 상속받음 ,
    # BaseRequestHandler class에는 클라이언트의 메세지 받는 recv()와 send() 함수가 내장되어 있다.
    userman=UserManager()

    def handle(self): #handle 함수명 바꾸면 안됨. BaseRequestHandler라는 class에 이미 내장된 handle함수를 오버라이드 한것이기 때문에.
        # 기본 내장되어 있을때는 비어있는 기본 구현이므로 오버라이드 해야함. 실제로 요청을 어떻게 처리할지 코드 내가 정하면 됨.
        print(self,'self memory')
        print('client[%s]연결'%self.client_address[0])
        try:
            username=self.registerUsername()
            print(username,":username")
            msg=self.request.recv(1024)
            print(self.request)
            print(self.client_address)
            print(self.server)
            while msg:
                print(msg.decode())
                if self.userman.messageHandler(username,msg.decode())==-1:
                    self.request.close()
                    break
                msg=self.request.recv(1024)
        except Exception as e:
            print(e)
        print("[%s]접속 종료" %self.client_address[0])
        self.userman.removeUser(username)
    def registerUsername(self):
        while True:
            self.request.send('ID'.encode())
            username=self.request.recv(1024)
            username=username.decode().strip()
            if self.userman.addUser(username,self.request,self.client_address):
                return username


class ChatingServer(socketserver.ThreadingMixIn,socketserver.TCPServer): #이 클래스가 호출되면, class의 init()메서드가 실행되면서 객체가 만들어짐
    pass #ChatingServer class는 socketserver.ThreadingMinIn과 TCPServer를 상속받아 만들어진 class 이다.
            # #TCPServer는 server생성하는 생성자 메소드와, 클라이언트와 연결되면 리퀘스트 처리할 class(매개변수로 넣어줌)의 handle() 함수 호출해줌


def runServer():
    try:
        server=ChatingServer((HOST,PORT),myTcpHandler) #server라는 객체 만듬. chatingServer class를 호출함. 그럼 class의 생성자(_init)가 호출되어 객체만들어짐
        #ChatingServer class는 TCPServer를 상속받았는데 TCPServer의 생성자 함수에는 매개변수로 server주소와 클라이언트의 요청을 처리할 class가 들어간다.
        #여기서는 우리가만든 myTcpHandler class가 request처리하는 class이다.
        #클라이언트 요청을 처리할 핸들러 클래스는 BaseRequestHandler를 상속받아야한다.

        server.serve_forever() #소켓서버의 TCPServer class에 내장된 server_forever함수이다.  #여기서 계속 클라이언트의 요청을 듣는다.
    except KeyboardInterrupt:
        print("서버 종료")
        server.shutdown()
        server.server_close() #
runServer()  #메인스레드이다.
















#DATABASE : 프로젝트 데이터 관리


#DB
#1.귓속말 주고받기 보내는 표기 >>> // 받는 표기 <<< # request객체 이용해서 연동해보라는 것이 중요 포인트
#귓속말은 둘에게만 보이게 처리 , 색상을 전체 대화 색상과 다르게 처리
#받은 귓속말 텍스트를 마우스로 누르면 보내온 사람에게 답장모드로 변환
#/w 아이디 보내려는 텍스트

#2. DB연동하기
#각자 로컬 mysql서버를 이용해서 현재 대화방의 로그를 기록한다. #이거의 포인트는 얘를 관리하는 스레드를 하나 더 만들어야함
#접속자의 오늘 로그인 여부
#접속자로그 테이블은 1일 1개 생성
#대화방로그 테이블에는 모든 텍스트 기록이 담긴다.
#강제퇴장인원/ 채팅 금지관련 로그

#3.강제퇴장기능 - 관리자 권한
#4.채팅금지/ 해제 기능 - 관리자 권한
#5.관리자 계정 기능 - DB에 회원 계정 테이블이 존재하다는 것
#6.DB에 회원 계정 테이블에 존재하는 회원만 로그인 ID/PW방식으로 로그인하여 대화방에 진입한다


#<테이블은 총 3~4개 나오면 될 것같다.>
#테이블에 자격권한은 int로 0,1로 password 등등 있는 회원 명부 테이블하나 만들어야함
#접속자로그 기록 테이블 : 어떤 회원이 언제들어와서 언제 나갔다 이런거 기록하는 테이블  #위에 테이블과 얘는 둘이 join해서 쓰면 될 것 같음.

#대화방 로그 기록 테이블 : 어떤시간에 누가 무슨말하고, 누가 강퇴당하고, 누가 귓속말하고 이런거 쓰는 테이블

