from datetime import datetime as dt
import json
import requests as rq
import sqlite3 as sq
import traceback
import os 

purl='https://www.goldapi.io/api/XAU/IRR'
nurl='https://newsapi.org/v2/everything?q=طلا,بازار,دلار,ایران&language=fa&apiKey=3250d9dda6dc4f3eb3439c18b72f9e1d'

# headers = {'x-access-token': "goldapi-519d7092e7b7265fd0c6c2e2ff76fa4c-io"}
headers = {'x-access-token': "goldapi-8cea1164fc972fd501279ce2e2ab39f3-io"} #2

req=rq.get(purl, headers=headers)
nreq=rq.get(nurl)


def Noperation(df,colstypes):
    with sq.connect('myfdb.db',check_same_thread=False) as cn:
         cursor=cn.cursor()
         cursor.execute('PRAGMA journal_mode=WAL')
         try:

            cursor.execute(f'CREATE TABLE IF NOT EXISTS ntbl(id INTEGER PRIMARY KEY AUTOINCREMENT ,{','.join(colstypes)} )')

            clns=list(df[0].keys())
            data=[tuple(item.get(i) for i in clns) for item in df ]
            vls=data
            plchldr=','.join('?'*len(clns))
            qury=f'INSERT OR IGNORE INTO ntbl ({', '.join(clns)}) VALUES({plchldr})'
            cursor.executemany(qury,vls)


            dropt='-6 days'
            dropq=f'DELETE FROM ntbl WHERE publishedAt< (SELECT datetime(MAX(publishedAt), ?) FROM ntbl)'
            cursor.execute(dropq,(dropt,))

            cn.commit()

            cursor.execute('select * from ntbl')
            c=cursor.fetchall()
            for i in c :
               print(i)

         except sq.Error as e:
            print(traceback.print_exc())               


def Nwork(stop):
   ndta=None
   ncolstypes=[]

   while not stop.is_set:
    try:
       ndta=nreq.json()
       for a in ndta['articles']:
           remove = [k for k, v in a.items() if isinstance(v, dict)]
           for i in remove:
               del a[i]
       
       for i,o in ndta['articles'][0].items():
           if i=='publishedAt':
              ncolstypes.append(f'{i} DATETIME UNIQUE')
           else:
              typ='TEXT' if isinstance(o,str) else 'REAL'
              ncolstypes.append(f'{i} {typ}')

       Noperation(ndta['articles'],ncolstypes)
       
       to=12*60
       if stop.wait(timeout=to):
          break
    except sq.Error as e:
        print(e) 

def Poperation(df,colstyps):
    
    with sq.connect('myfdb.db',check_same_thread=False) as cn:
          cursor=cn.cursor()
          cursor.execute('PRAGMA journal_mode=WAL')

          try:   
             cursor.execute(f'CREATE TABLE IF NOT EXISTS tbl(id INTEGER PRIMARY KEY AUTOINCREMENT,{','.join(colstyps)})')
             plchldr=','.join(['?']*len(df))
             vls=tuple(df.values())
             cols=','.join(df.keys())
             qry=f'INSERT OR IGNORE INTO tbl ({cols}) VALUES({plchldr})'
             cursor.execute(qry,vls)

             weeks=604800
             months=2592000
             dropq='DELETE FROM tbl WHERE timestamp < (SELECT MAX(timestamp) FROM tbl)- ?'
             cursor.execute(dropq,(months,))
      
             cn.commit()
       
            #  cursor.execute('select * from tbl')
            #  rows=cursor.fetchall()
            #  for r in rows:
            #   print(r)
          
          except sq.Error as e:
                 print(e)
                #  traceback.print_exc()
                 cn.rollback()

def Pwork(stop):             
 while not stop.is_set():
   data=None
   colstyps=[]
   try:
      data=req.json()
      for i ,o in data.items():
       if i=='timestamp':
          colstyps.append(f'{i} DATETIME UNIQUE')
       else: 
          typ='TEXT' if isinstance(o,str) else 'REAL'
          colstyps.append(f'{i} {typ}')
   
      Poperation(data,colstyps)
      # to=(60*30) if 8<=dt.now().hour<22 else (60*150)
      to=10 if 8<=dt.now().hour<22 else 15
      if stop.wait(timeout=to):
         break

      if data is not None:
         pass

   except Exception as e:
         print(f'Error: {e}')



         
           
       


