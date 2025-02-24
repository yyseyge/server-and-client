import socket
from threading import Thread
import tkinter

HOST = '192.168.0.20'
PORT = 9900

# GUI 설정
tk = tkinter.Tk()
tk.geometry("800x500")

sendmsg = tkinter.Entry(tk)
chattingBox = tkinter.Listbox(tk, width=30, height=20)

# ID 입력창
toplevel = tkinter.Toplevel(tk)
toplevel.title("아이디입력창")
toplevel.geometry("280x150")

idlavel = tkinter.Label(toplevel, text='ID')
idlavel.place(x=70, y=30)
ID = tkinter.Entry(toplevel)
ID.place(x=50, y=60, width=80)

sock = None  # 소켓을 전역 변수로 선언

def rcvMsg(sock):
    while True:
        try:
            data = sock.recv(1024)
            temp= data.decode()
            if not data:
                break
            elif '>>>' in temp:
                chattingBox.insert(-1, temp + '\n')
                chattingBox.itemconfig(0,foreground='green')
                chattingBox.update()
                chattingBox.see(0)
            elif '<<<' in temp:
                chattingBox.insert(-1, temp + '\n')
                chattingBox.itemconfig(0, foreground='blue')
                chattingBox.update()
                chattingBox.see(0)

            else:
                chattingBox.insert(-1, temp + '\n')
                chattingBox.update()
                chattingBox.see(0)
        except:
            pass

def runChat():
    global sock  # 전역 변수 사용 선언

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 소켓 생성
    sock.connect((HOST, PORT))  # 서버 연결

    t1 = Thread(target=rcvMsg, args=(sock,))
    t1.daemon = True
    t1.start()

    def onClick():
        sock.send(sendmsg.get().encode())

    def onEnter(event):
        onClick()
        sendmsg.delete(0, tkinter.END)

    def login():
        sock.send(ID.get().encode())  # ID 전송
        toplevel.destroy()  # 로그인 창 닫기

    # GUI 요소 배치
    sendmsg.place(x=10, y=400)
    chattingBox.place(x=10, y=30)

    btn = tkinter.Button(tk, text='보내기', command=onClick)
    log = tkinter.Button(toplevel, text='로그인', command=login)

    log.place(x=100, y=100)
    btn.place(x=170, y=400)

    sendmsg.bind("<Return>", onEnter)

    tk.mainloop()

    sock.close()  # GUI 종료 시 소켓 닫기

runChat()
