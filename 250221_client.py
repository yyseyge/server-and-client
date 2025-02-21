import socket
from threading import Thread #이거랑 그냥 import하는거랑 차이가 뭔지
import tkinter

HOST='192.168.0.20'
PORT=9900
tk=tkinter.Tk()
tk.geometry("800x500")

sendmsg=tkinter.Entry(tk)
chattingBox=tkinter.Listbox(tk,width=30,height=20)

# people=tkinter.Listbox(tk)
# peoplemg=tkinter.Label(tk)

toplevel = tkinter.Toplevel(tk)
toplevel.title("아이디입력창")
toplevel.geometry("280x150")

idlavel = tkinter.Label(toplevel, text='ID')
idlavel.place(x=70, y=30)
ID = tkinter.Entry(toplevel)
ID.place(x=50, y=60, width=80)




def rcvMsg(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            chattingBox.insert(-1, data.decode() + '\n')
            chattingBox.update()
            chattingBox.see(0)
        except:
            pass


def runChat():
     with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
         sock.connect((HOST,PORT))
         t1=Thread(target=rcvMsg,args=(sock,))
         t1.daemon=True
         t1.start()
         def onClick():
             sock.send(sendmsg.get().encode())
         def onEnter(event):
             onClick()
             sendmsg.delete(0,tkinter.END)
         def login():
             sock.send(ID.get().encode())
     sendmsg.place(x=10,y=400) # 메세지 보내는 entry 창
     chattingBox.place(x=10,y=30) # 채팅 list box
     btn = tkinter.Button(tk, text='보내기',command=onClick) #메세지 보내기 버튼
     log = tkinter.Button(toplevel, text='로그인', command=login) #로그인 창의 로그인 버튼
     log.place(x=100, y=100)
     btn.place(x=170,y=400)
     # people.place(x=300,y=30)
     sendmsg.bind("<Return>", onEnter)
     tk.mainloop()  #메인스레드는 메인루프를 돌리고 있다.
     # tk.after(1000000, runChat)


runChat()
