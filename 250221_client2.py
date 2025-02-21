import socket
from threading import Thread
import tkinter

tk=tkinter.Tk()
tk.geometry("1000x400")
entry=tkinter.Entry(tk)
entry2=tkinter.Listbox(tk,height=50,width=30)

HOST='192.168.0.20'
PORT=9900

def rcvMsg(sock):
    while True:
        try:
            data=sock.recv(1024)
            if not data:
                break
            print(data.decode())
            entry2.insert(-1,data.decode()+'\n')
            entry2.update()
            entry2.see(0)
        except:
            pass
def runChat():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock: #클라이언트의 소켓 객체를 만듬
        sock.connect((HOST,PORT)) #서버한테 요청보내는 것
        t=Thread(target=rcvMsg,args=(sock,)) #서브스레드를 만듬 왜냐하면 메인스레드는 지금 mainloop돌리느라 바쁘니까 서브스레드 만들어서 메세지 받는 처리 시키려고
        t.daemon=True #rcvMsg를 데몬으로 처리한 이유는 메인 스레드가 죽으면 rcvMsg도 죽게 하기 위해서.
        t.start()
        def onClick():
            sock.send(entry.get().encode())
        def onEnter(event):
            onClick()
            entry.delete(0,tkinter.END)
        entry2.pack(side=tkinter.LEFT,fill=tkinter.BOTH,padx=5,pady=5)
        label=tkinter.Label(tk,text='chat message')
        entry.pack()
        label.pack()
        btn=tkinter.Button(tk,text='확인',command=onClick)
        btn.pack()
        entry.bind("<Return>",onEnter)
        tk.mainloop() #메인스레드는 메인루프를 돌리고 있다.
runChat()