import threading
import time
counter=0

lock=threading.Lock() #스레드 자체의 lock객체 선언


def increment(threadname):
    global counter
    lock.acquire()  #자물쇠 거는 함수
    try:
        for a in range(100): #0부터

            time.sleep(0.01)
            counter+=1
            print(f'{threadname} count{counter}')
    finally:
        lock.release() #자물쇠 푸는 함수


thread1 = threading.Thread(target=increment,args=('th1',)) #얘는 서브 스레드1 #스레딩의 스레드 객체 만드는데 타겟은 위에 있는 함수고 매개변서는 args에 있는 것
thread2 = threading.Thread(target=increment,args=('th2',)) #얘는 서브 스레드2


thread1.daemon=True
thread2.daemon=True

thread1.start() #daemon=true값이 없는 상태면 서브스레드1은 100까지 서브스레드2는 200까지 출력됨.
thread2.start()

#thread1.join()
#thread2.join()
print(f'Count: {counter}') #메인 스레드로 실행되는 부분

#결과창에 Count:0 이 제일 먼저 출력 되는데 이게 메인 스레드이다 .
#프로세스의 종료 : 메인스레드의 종료로 기준점으로 잡지만. 서브스레드가 작업이 마친 상태가 아니라면 서브스레드 작업을 마치고 프로세스가 닫힘
#서브스레드.daemon으로 설정하면 메인스레드 종료시 프로세스 종료 됨 그래서 count:0만 출력되고 서브스레드는 일 못하고 끝나버림
#join의 의미 : thread1.join()은 스레드1이 마칠때까지 기다려라



#예를 들어 가정을 해보면
# 서브 스레드가 1개 있다. 이 서브스레드는 for문으로 1~1000까지 카운드 올리는 함수에 연결
# 만약 얘가 데몬이라면 (즉, subthread.daemon=True)이면, 서브스레드(데몬) 종료와 상관없이 메인스레드 종료 시점에 프로세스 종료
#만약 서브스레드가 daemon이고 join도 있으면 , 메인스레드가 서브스레드(데몬) 할 일 전부 마칠 때까지 기다린다.
# 만약 서브 스레드(데몬 없고) join도 없다면 메인스레드가 서브스레드를 기다리진 않지만 프로세스를 종료하진 않는다.
#서브스레드(데몬 없고) join있으면 메인스레드가 서브스레드의 작업이 완료될때까지 기다려주고 그 후에 메인스레드가 진행




