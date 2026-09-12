import sqlite3 as sq
import customtkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg ,NavigationToolbar2Tk
import matplotlib.pyplot as pl
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter as ff
import pandas as pd
import datetime as dt
from PIL import Image,ImageTk
cn=sq.connect('myfdb.db',check_same_thread=False)
df=pd.read_sql_query('SELECT * FROM tbl ORDER BY id',cn)
news=pd.read_sql_query('SELECT * FROM ntbl ORDER BY id',cn)
cn.close()

if df.empty:
    print('No data here!')

barcols=['price_gram_24k','price_gram_22k','price_gram_21k' , 'price_gram_20k',
              'price_gram_18k','price_gram_16k','price_gram_14k','price_gram_10k']

def linechart():  
    y=inp.get()
    cy=combo.get().strip()
    if y.strip() !='':
       if y in barcols:
          fy=y 
       else: 
           print('Not found!')
           fy='price_gram_18k'
    elif cy and cy in barcols:
       fy=cy
    else: 
       fy='price_gram_18k'
    
    chrtdta=df.dropna(subset=['timestamp',fy]).copy()
    chrtdta['timestamp']=pd.to_datetime(chrtdta['timestamp'],unit='s',errors='coerce')
    ydta=chrtdta[fy]/31.1035
    xdta=chrtdta['timestamp']

    ax.clear()
    ax.plot(xdta,ydta,marker='.')

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d ,%H:%M'))
    ax.yaxis.set_major_formatter(ff(lambda x,pos:f'{x:,.0f}'))

    pl.setp(ax.get_xticklabels(),rotation=25)
    ax.set_xlabel('time') 
    ax.set_ylabel('price')
    ax.set_title(f'{fy} per chang_time')

    cnv.draw()

def barchart():    
    x=range(len(barcols))
    dftimecopy=df.dropna(subset='timestamp').copy()
    dftimecopy=pd.to_datetime(dftimecopy['timestamp'],unit='s',errors='coerce')

    date=inp.get().strip()
    cdate=combo.get()
    if date!='':
       if date in dftimecopy:
          fdate=date 
       else:
          print('Not found!')
          fdate=dftimecopy.max()

    elif cdate and cdate in dftimecopy:
      fdate=cdate
    else:
       fdate=dftimecopy.max()

    ax.clear()
    ycopy=df[dftimecopy==fdate][barcols].values.flatten().astype(float)

    ax.bar(x,ycopy)

    ax.yaxis.set_major_formatter(ff(lambda x,pos:f'{int(x):,.0f}'))
    ax.set_ylim( 0,ycopy.max()+10**7)
    ax.set_xlabel('items')
    ax.set_xticks(x)
    ax.set_xticklabels(barcols)
    pl.setp(ax.get_xticklabels(),rotation=20 )
    ax.set_title(f'prices at date {cdate}')
    
    cnv.draw()

def inpbox(chart):
    if chart=='line_chart':
       combo.configure(values=barcols)
       combo.set(combo.get())

    elif chart=='bar_chart':
       last6=df.tail(6).copy()
       last6['timestamp']=pd.to_datetime(last6['timestamp'],unit='s')
       last6['timestamp']=last6['timestamp'].dt.strftime('%Y-%m-%d ,%H:%M').tolist()
       time=[str(i) for i in last6['timestamp'].tolist()]
       combo.configure(values=time)
       combo.set(combo.get())

def News(title,news,date,url,writer):
    Ncard=tk.CTkFrame(scrolw)
    Ncard.grid()

    tlabl=tk.CTkLabel(Ncard,text=title ,font=('Arial',20,'bold'))
    tlabl.grid(padx=10,pady=10,sticky='e')
    nlabl=tk.CTkLabel(Ncard,text=f"{news}({writer})",font=('Arial',16),wraplength=600,anchor='e')
    nlabl.grid(sticky='e')
    dlabl=tk.CTkLabel(Ncard,text=f'Date: {date}')
    dlabl.grid(sticky='w')
    ulabl=tk.CTkLabel(Ncard,text=f'Address:{url}')
    ulabl.grid(sticky='w')
    slabl=tk.CTkLabel(Ncard,text='_'*90)
    slabl.grid()

def logo(fram):
    img=Image.open(r'C:\Users\kian net\Desktop\Gold proj\Elogo.png')
    img=img.resize((900,300),Image.Resampling.LANCZOS )
    image=ImageTk.PhotoImage(img) 
    ilabl=tk.CTkLabel(fram,image=image)
    ilabl.image=image
    ilabl.pack(fill='both' ,expand=True)


def openp():
    titw.grid_remove()
    sidew.grid_remove()
    scrolw.grid_remove()
    page2.rowconfigure(0,weight=1)
    page2.columnconfigure(0,weight=1)

    page2.grid(column=0,row=0,sticky='nsew')
    chartp.grid(column=1,row=1,sticky='nsew')
    btnp.grid(column=0,row=1,rowspan=2,sticky='nsew')
    topp.grid(column=1,row=0,columnspan=2,sticky='nsew')

def back():
    page2.grid_remove()
    titw.grid()
    sidew.grid()
    scrolw.grid()
    

    
win=tk.CTk()
win.title('$ Gold $')
win.geometry('1400x1000')

win.columnconfigure(0,weight=0)
win.columnconfigure(1,weight=1)
win.rowconfigure(0,weight=0)
win.rowconfigure(1,weight=1)

titw=tk.CTkFrame(win)
titw.rowconfigure(0,weight=1)
titw.grid(column=1,row=0,sticky='nsew',padx=(3,6))
logo(titw)

sidew=tk.CTkFrame(win)
# sidew.columnconfigure(1,weight=1)
sidew.grid(column=0,row=0,sticky='nsew')

scrolw=tk.CTkScrollableFrame(win)
scrolw.grid(column=1,row=1,sticky='nsew',padx=(3,6))
scrolw.columnconfigure(0,weight=1)
scrlt=tk.CTkLabel(scrolw,text='News!',font=('Serif',20,'bold'))
scrlt.grid(column=0,row=0,sticky='nw')
for i in list(range(len(news['id'])-1,0,-1)):
   News(news['title'][i],news['description'][i],news['publishedAt'][i],news['url'][i],news['author'][i])

time=dt.datetime.now().strftime('%H:%M:%S')
date=dt.datetime.now().date()
tlabl=tk.CTkLabel(sidew)
dlabl=tk.CTkLabel(sidew)
tlabl.grid(column=0,row=1)
dlabl.grid(column=0,row=0)
tlabl.configure(text=time)
dlabl.configure(text=date)

page2=tk.CTkFrame(win)
chartp=tk.CTkFrame(page2)
chartp.columnconfigure(0,weight=1)
btnp=tk.CTkFrame(page2)
topp=tk.CTkFrame(page2)

inp=tk.StringVar()
inpf=tk.CTkEntry(topp,textvariable=inp)
inpf.grid(row=0,column=1)
tbf=tk.CTkFrame(topp)
tbf.grid(column=2,row=0)
combo=tk.CTkComboBox(inpf)
combo.grid()

fig=Figure(figsize=(14,9),facecolor='darkgray',edgecolor='black')
ax=fig.add_subplot(111)
cnv=FigureCanvasTkAgg(fig,master=chartp)
cnvw=cnv.get_tk_widget().pack(fill='both',expand=True)
cnvw
tb=NavigationToolbar2Tk(cnv,tbf)
tb.update()

charts=tk.CTkButton(sidew,text='Charts',width=45,height=25,
                    command=lambda: openp()).grid(row=2,column=0)
line_chart=tk.CTkButton(btnp,text='line_chart',width=30,height=15,
                        command=lambda:( linechart(),inpbox('line_chart'))).grid(row=2,column=0)
bar_chart=tk.CTkButton(btnp,text='bar_chart',width=30,height=15,
                       command=lambda:( barchart(),inpbox('bar_chart'))).grid(row=3,column=0)
bck=tk.CTkButton(btnp,text='Back',width=30,height=15,
                 command=lambda: back()).grid(row=4,column=0)

win.mainloop()
 

