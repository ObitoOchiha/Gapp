import threading as th
from Gbackground import Pwork,Nwork

stop=th.Event()

Pth=th.Thread(target=Pwork,args=(stop,))
Nth=th.Thread(target=Nwork,args=(stop,))

try:
    Pth.start()  
    Nth.start()
    import Gdashbord
    
except KeyboardInterrupt:
     print('closing the app...')
finally:
     stop.set()
     print('app is closed.')
    