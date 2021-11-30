import requests as r
import time
#import sys # Выход из программы sys.exit()
import psycopg2
import datetime
import subprocess
import telnetlib

udprml0last = -79

#------------------------------ФУНКЦИИ ПРОГРАММЫ----------------------------------

#-----------Функция для доступа к БД, чтения, записи данных-----------------------
def access_db(dbn, data=(), marker=0):
   connection = psycopg2.connect(dbn)
   cursor = connection.cursor()    
   if data != () and marker == 0:
      dt = 'INSERT INTO ubajax_dataubntall(udprml0, udprml1,\
            udprmr0, udprmr1, udspeedl, udspeedr, ipubnttwo, ipubnttworem,\
            mistake_ip, detail_txt, timewrite) \
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
      cursor.execute(dt, data)
      connection.commit()
      cursor.close()
      connection.close()
   elif data == () and marker == 0:
      dt = 'SELECT startproc from ubajax_startprocess'
      cursor.execute(dt)
      start_process = cursor.fetchall()[0][0]
      cursor.close()
      connection.close()
      return start_process
   elif marker == 1:  
      dt = 'SELECT ipubntremote from ubajax_ubntmodeltest WHERE ipubntone=%s'
      datan = (data,)
      cursor.execute(dt, datan)
      url = cursor.fetchone()[0]
      cursor.close()
      connection.close()
      return url
   elif data == () and marker == 2:
      dt = 'SELECT ipubntone from ubajax_ubntmodeltest'
      cursor.execute(dt)
      ip_all_sql = cursor.fetchall()
      cursor.close()
      connection.close()
      return ip_all_sql
   elif marker == 3:
      dt = 'SELECT statonoff from ubajax_ubntmodeltest WHERE ipubntone=%s'
      datan = [data]
      cursor.execute(dt, datan)
      onoff = cursor.fetchone()[0]
      cursor.close()
      connection.close()
      return onoff
#----------------------------------END--------------------------------------------

#----------------------------------ФУНКЦИЯ ALCOMA---------------------------------
def alcoma():
   global udprml0last
   try:
      tn = telnetlib.Telnet(url)           # Открытие сессии Телнет.
      time.sleep(0.1)                       # Задержка времени.
      tn.write(b"1\n")                      # Ввод логина (Логин: 1).
      time.sleep(0.1)                       # Задержка времени.
      tn.write(b"1\n")                      # Ввод пароля (Пароль: 1).
      time.sleep(1)                         # Задержка времени.
      tn.write(b"M\n")                      # Вход в главное меню [M]Main Menu.
      tn.write(b"D\n")                      # Вход в главное меню [D]Analysis.
      tn.write(b"A\n")                      # Вход в главное меню [A]Status Information.
      time.sleep(1)                         # Задержка времени.
      text = tn.read_very_eager().decode("utf-8")
      textlist = text.split('7f')
      textlistsrez = textlist[-11::1]
      udprml0 = int(float(textlistsrez[0][-14:-9]))
      if udprml0 == 0:
         udprml0 = udprml0last   
      udprml1 = udprml0
      udprmr0 = int(float(textlistsrez[1][-14:-9]))
      udprmr1 = udprmr0
      udspeedl = float(textlistsrez[6][-21:-19])
      udspeedr = float(textlistsrez[6][-21:-19])
      ipubnttwo = textlistsrez[7][-16:-5]
      ipubnttworem = textlistsrez[9][-16:-5]
      namerrsl = textlistsrez[8][-15:-6]
      namerrsr = textlistsrez[10][-80:-70]
      namerrl = namerrsl + '-' + namerrsr
      namerrs = namerrsl + '-' + namerrsr
      distrrl = '20.2'
      rx_freq = str(float(textlistsrez[4][-15:-9])*1000)
      tx_freq = str(float(textlistsrez[3][-15:-9])*1000)
      rxchanbw = textlistsrez[6][-11:-6]
      txmodrate = '--'
      linkmode = 'master'
      detail_txt = namerrl + ' ' + namerrs + ' ' + distrrl + ' ' + rx_freq + ' ' + tx_freq + \
                  ' ' + rxchanbw + ' ' + txmodrate + ' ' + linkmode + ' ' + ipubnttworem
# Записываем собранные данные в txt-файл detail.txt.
      with open(f'/home/zarya/project/ubntserver/sell/ip{url}_detail.txt'', 'w', encoding='utf-8') as f:
         f.write(detail_txt)

      tn.write(b"M\n")                       # Вход в главное меню [M]Main Menu.
      time.sleep(1)                          # Задержка времени.
      tn.write(b"Q\n")                       # Закрытие Телнет сессии.
   except Exception: # Исключение.
      #prinr('Mistake')
      mistake_ip = 'Ошибка Telnet'
# Записываем ошибку в текстовый файл  logmistakes.txt.
      text = f'{timewrite} --> Ошибка Telnet'
      write_txt(text)
      
# Записываем данные РРЛ в БД.        
   try:
      mistake_ip = 'Ошибок нет'
      data = (udprml0, udprml1, udprmr0, udprmr1, udspeedl, udspeedr,
              ipubnttwo, ipubnttworem, mistake_ip, detail_txt, timewrite)
      access_db(dbn, data)
      udprml0last = udprml0
   except Exception: # Исключение.
      mistake_ip = 'Ошибка записи данных в БД'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
      text = f'{timewrite} --> Ошибка записи данных в БД в IP_{url}'
      write_txt(text)

      if mistake_ip == 'Ошибка записи данных в БД':   
         try:
            data = (udprml0, udprml1, udprmr0, udprmr1, udspeedl,
            udspeedr, ipubnttwo, ipubnttworem, mistake_ip, detail_txt, timewrite)
            access_db(dbn, data)                                
         except Exception: # Исключение.
            mistake_ip = 'Ошибка записи данных в БД повторно'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
            text = f'{timewrite} --> Ошибка записи данных в БД повторно в IP_{url}'
            write_txt(text)
#----------------------------------END--------------------------------------------

#-----------------ФУНКЦИЯ ДЛЯ ЗАПИСИ ОШИБОК В ТЕКСТОВЫЙ ФАЙЛ----------------------    
def write_txt(text):
   with open('/home/zarya/project/ubntserver/sell/logmistakes.txt', 'a', encoding='utf-8') as f:
      f.write(text + '\n')
#----------------------------------END--------------------------------------------

#---------------ФУНКЦИЯ ПОЛУЧЕНИЕ СПИСКА IP АДРЕСОВ ИЗ БД-------------------------
def ip_all_ub():
   ip_all = []
# Получаем список кортежей [('10.1.113.2',), ('10.1.113.4',),.... ('10.1.120.1',)].   
   ipall = access_db(dbn, marker=2)
   while ipall:
      url = ipall.pop(0)[0]
# Получаем сигнал о разрешении или запрете мониторинга для данного IP.        
      nff = access_db(dbn, url, marker=3)
      if nff == 1: # Если сигнал равен 1 - мониторинг разрешён.
# Создаём список IP адресов учавствующих в мониторинге.            
         ip_all.append(url) 
      else:
         continue
      if ipall == []:
         break
# Возврашаем список адресов.
   return ip_all  
#----------------------------------END--------------------------------------------

#-----------------------------------ФУНКЦИИ END-----------------------------------


#-----------------------НАЧАЛО ПРОГРАММЫ МОНИТОРИНГА------------------------------

payload = {'username': 'ubnt', 'password': 'ubnt', 'login': 'Login'}

#--------------Получение из файла config данных для доступа к БД------------------       
try:
   with open('/home/zarya/project/ubntserver/sell/config', 'r') as f:
      dbn = f.read()
except Exception: # Исключение
   #print('Ошибка получения авторизационных данных для доступа к БД')
   #print('Проверьте данные в файле "config"')
# В переменную mistake_ip, записываем ошибку - 
# 'Ошибка получения авторизационных данных для доступа к БД,
# Проверьте данные в файле "config"'
   mistake_ip = 'Ошибка получения авторизационных данных для доступа к БД,\
                 проверьте данные в файле "config"'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
# Считываем и запоминаем в переменной timewrite дату и время.
   timewrite = datetime.datetime.now()
   text = f'{timewrite} --> Ошибка получения авторизационных данных для\
                            доступа к БД, проверьте данные в файле "config"'
   write_txt(text)
# Обнуляем переменную mistake_ip, записываем в неё 'Ошибок нет'.
   mistake_ip = 'Ошибок нет'
   
#----------------------------------END--------------------------------------------

#-----------------Получение из файла ipalcoma IP адреса РРС Alcoma----------------       
try:
   with open('/home/zarya/project/ubntserver/sell/ipalcoma', 'r') as f:
      ipal = f.read()
except Exception: # Исключение
   #print('Ошибка получения IP адреса РРС Alcoma')
   #print('Проверьте данные в файле "ipalcoma"')
# В переменную mistake_ip, записываем ошибку - 
# Ошибка получения IP адреса РРС Alcoma,
# проверьте данные в файле "ipalcoma".
   mistake_ip = 'Ошибка получения IP адреса РРС Alcoma,\
                 проверьте данные в файле "ipalcoma"'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
# Считываем и запоминаем в переменной timewrite дату и время.
   timewrite = datetime.datetime.now()
   text = f'{timewrite} --> Ошибка получения IP адреса РРС Alcoma,\
                            проверьте данные в файле "ipalcoma"'
   write_txt(text)
# Обнуляем переменную mistake_ip, записываем в неё 'Ошибок нет'.
   mistake_ip = 'Ошибок нет'
   
#----------------------------------END--------------------------------------------

# Получаем из базы данных информацию о разрешении старта общего мониторинга. 
# 1 - мониторинг разрешен.
start_process = access_db(dbn)
        
while start_process == 1:
# Получаем список IP адресов и записываем его в переменную ipsel.    
   ipsel = ip_all_ub()
#print(ipone) # Для проверки списка IP адресов.
   for url in ipsel: # Обрабатываем список IP адресов в цикле.
      #print(url)
      urlloc = url
# Обнуляем переменную mistake_ip, записываем в неё 'Ошибок нет'.
      mistake_ip = 'Ошибок нет'
        
#      print(url) # Для проверки.

#-----------------------НОВАЯ МЕТОДИКА ДОСТУПА К airFiber-------------------------
      
#-----------Считываем и запоминаем в переменной timewrite дату и время------------
      timewrite = datetime.datetime.now()
#---------------------------------END---------------------------------------------
      
#--ИЗМЕНЕНИЯ--------------------ПИНГУЕМ IP(url)локальный--------------------------
      command = ['ping', '-c', '1', url]
      if subprocess.call(command) == 0: # Если url на ping отозвался.
#----------------------------------АВТОРИЗАЦИЯ------------------------------------
#--------------------------------Раблта с РРС Alcoma------------------------------
         if url == ipal: # Если url совпадает с IP адресом Alcoma.
            alcoma()     # Вызываем функцию Alcoma().
            continue     # После выполнения функции переходим к следуюшему url.
#-------------------------------------END ALCOMA----------------------------------         
         ses = r.Session()
         sget = ses.get(f'http://{url}/login.cgi?uri=/')
         try:         
            spost = ses.post(f'http://{url}/login.cgi', params=payload)                                  
         except Exception: # Исключение.
            mistake_ip = 'Ошибка авторизации'
# Записываем ошибку в текстовы файл  logmistakes.txt.
            text = f'{timewrite} --> Ошибка авторизации в IP_{url}'
            write_txt(text)
# Формируем кортеж data для записи в БД.
            urlrem = access_db(dbn, url, marker=1)
            data = (0, 0, 0, 0, 0.0, 0.0, url, urlrem, mistake_ip,
                    '', timewrite)                    
# Записываем ошибку в БД.       
            access_db(dbn, data)
            if mistake_ip == 'Ошибка авторизации':            
               try:
                  spost = ses.post(f'http://{url}/login.cgi', params=payload) 
               except Exception: # Исключение.
                  ses.close() # Закрываем сессию.
                  mistake_ip = 'Ошибка авторизации повторно'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
                  text = f'{timewrite} --> Ошибка авторизации повторно в IP_{url}'
                  write_txt(text)
# Формируем кортеж data для записи в БД.
                  urlrem = access_db(dbn, url, marker=1)
                  data = (0, 0, 0, 0, 0.0, 0.0, url, urlrem, mistake_ip,
                          '', timewrite)                            
# Записываем ошибку в БД.       
                  access_db(dbn, data) 
                  continue # Пропускаем эту итерацию цикла и переходим к следующему IP.        
#----------------------------------------END--------------------------------------

#-----------------------------------ПОЛУЧЕНИЕ JSON--------------------------------
         try:
            sgetjson = ses.get(f'http://{url}/status.cgi').json()
#            print(sgetjson)
         except Exception: # Исключение.
            mistake_ip = 'Ошибка получения json'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
            text = f'{timewrite} --> Ошибка получения json в IP_{url}'
            write_txt(text)
            
# Формируем кортеж data для записи в БД.
            urlrem = access_db(dbn, url, marker=1)
            data = (0, 0, 0, 0, 0.0, 0.0, url, urlrem, mistake_ip,
                    '', timewrite)                    
# Записываем ошибку в БД.        
            access_db(dbn, data)

            if mistake_ip == 'Ошибка получения json':   
               try:
                  sgetjson = ses.get(f'http://{url}/status.cgi').json()
               except Exception: # Исключение.
                  ses.close() # Закрываем сессию.
                  mistake_ip = 'Ошибка получения json повторно'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
                  text = f'{timewrite} --> Ошибка получения json повторно в IP_{url}'
                  write_txt(text)

# Формируем кортеж data для записи в БД.
                  urlrem = access_db(dbn, url, marker=1)
                  data = (0, 0, 0, 0, 0.0, 0.0, url, urlrem, mistake_ip,
                          '', timewrite)                    
# Записываем ошибку в БД.        
                  access_db(dbn, data)
                  continue # Пропускаем эту итерацию цикла и переходим к следующему IP.
         ses.close() # Закрываем сессию.  
#----------------------------------------END--------------------------------------            

#----------------------------ОБРАБАТЫВАЕМ ПОЛУЧЕННЫЙ JSON-------------------------
         try:
            udprml0 = sgetjson['airfiber']['rxpower0']   # -54
            udprml1 = sgetjson['airfiber']['rxpower1']   # -53
            udprmr0flag = sgetjson['airfiber']['remote_rxpower0']  # -57
            udprmr1flag = sgetjson['airfiber']['remote_rxpower1']  # -58
            if udprmr0flag == -1000:
               udprmr0 = 0
            elif udprmr1flag == -1000:
               udprmr1 = 0
            else:
               udprmr0 = udprmr0flag
               udprmr1 = udprmr1flag
               
            udspeedl = round(sgetjson['airfiber']['rxcapacity']/1000000, 2)   # 301.60
            udspeedr = round(sgetjson['airfiber']['txcapacity']/1000000, 2)  # 302.30
            ipubnttwo = url
            
            ipubnttworemflag = sgetjson['airfiber']['remote_ip']
            if ipubnttworemflag == 'n/a':
               ipubnttworem = access_db(dbn, url, marker=1)
            else:
               ipubnttworem = ipubnttworemflag
               
            namerrl = sgetjson['wireless']['essid']
            namerrs = sgetjson['host']['hostname']
            distrrl = str(sgetjson['wireless']['distance']/1000)
            rx_freq = str(sgetjson['airfiber']['rx_frequency']/1000)
            tx_freq = str(sgetjson['airfiber']['tx_frequency']/1000)
            rxchanbw = sgetjson['airfiber']['rxchanbw']
            txmodrate = sgetjson['airfiber']['txmodrate']
            linkmode = sgetjson['airfiber']['linkmode']
               
            detail_txt = namerrl + ' ' + namerrs + ' ' + distrrl + ' ' + rx_freq + ' ' +\
                         tx_freq + ' ' + rxchanbw + ' ' + txmodrate + ' ' + linkmode + ' ' + ipubnttworem
# Записываем собранные данные в txt-файл detail.txt.         
            with open(f'/home/zarya/project/ubntserver/sell/ip{url}_detail.txt'', 'w', encoding='utf-8') as f:
               f.write(detail_txt)
         except Exception: # Исключение.
            mistake_ip = 'Ошибка формирования данных для записи в БД'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
            text = f'{timewrite} --> Ошибка формирования данных для записи в БД в IP_{url}'
            write_txt(text)

# Формируем кортеж data для записи в БД.
            urlrem = access_db(dbn, url, marker=1)
            data = (0, 0, 0, 0, 0.0, 0.0, url, urlrem, mistake_ip,
                    '', timewrite)                    
# Записываем ошибку в БД.        
            access_db(dbn, data)

            if mistake_ip == 'Ошибка формирования данных для записи в БД':   
               try:
                  udprml0 = sgetjson['airfiber']['rxpower0']   # -54               
                  udprml1 = sgetjson['airfiber']['rxpower1']   # -53
                  udprmr0flag = sgetjson['airfiber']['remote_rxpower0']  # -57
                  udprmr1flag = sgetjson['airfiber']['remote_rxpower1']  # -58
                  if udprmr0flag == -1000:
                     udprmr0 = 0
                  elif udprmr1flag == -1000:
                     udprmr1 = 0
                  else:
                     udprmr0 = udprmr0flag
                     udprmr1 = udprmr1flag
                     
                  udspeedl = round(sgetjson['airfiber']['rxcapacity']/1000000, 2)   # 301.60        
                  udspeedr = round(sgetjson['airfiber']['txcapacity']/1000000, 2)  # 302.30
                  ipubnttwo = url
                  
                  ipubnttworemflag = sgetjson['airfiber']['remote_ip']
                  if ipubnttworemflag == 'n/a':
                     ipubnttworem = access_db(dbn, url, marker=1)
                  else:
                     ipubnttworem = ipubnttworemflag
                        
                  namerrl = sgetjson['wireless']['essid']
                  namerrs = sgetjson['host']['hostname']         
                  distrrl = str(sgetjson['wireless']['distance']/1000)         
                  rx_freq = str(sgetjson['airfiber']['rx_frequency']/1000)        
                  tx_freq = str(sgetjson['airfiber']['tx_frequency']/1000)
                  rxchanbw = sgetjson['airfiber']['rxchanbw']         
                  txmodrate = sgetjson['airfiber']['txmodrate']
                  linkmode = sgetjson['airfiber']['linkmode']
                      
                  detail_txt = namerrl + ' ' + namerrs + ' ' + distrrl + ' ' + rx_freq + ' ' +\
                               tx_freq + ' ' + rxchanbw + ' ' + txmodrate + ' ' + linkmode + ' ' + ipubnttworem

               except Exception: # Исключение.
# Записываем ошибку в txt-файл logmistakes.txt.               
                  mistake_ip = 'Ошибка формирования данных для записи в БД повторно'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
                  text = f'{timewrite} --> Ошибка формирования данных для записи в БД повторно в IP_{url}'
                  write_txt(text)

# Формируем кортеж data для записи в БД.
                  urlrem = access_db(dbn, url, marker=1)
                  data = (0, 0, 0, 0, 0.0, 0.0, url, urlrem, mistake_ip,
                          '', timewrite)                    
# Записываем собранные данные в txt-файл detail.txt.        
                  access_db(dbn, data)
                  with open(f'/home/zarya/project/ubntserver/sell/ip{url}_detail.txt'', 'r') as f:
                     detail_txt = f.read()
                  continue # Пропускаем эту итерацию цикла и переходим к следующему IP.
               
# Записываем данные РРЛ в БД.        
         try:   
            data = (udprml0, udprml1, udprmr0, udprmr1, udspeedl, udspeedr,
                    ipubnttwo, ipubnttworem, mistake_ip, detail_txt, timewrite)
            access_db(dbn, data)
         except Exception: # Исключение.
            mistake_ip = 'Ошибка записи данных в БД'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
            text = f'{timewrite} --> Ошибка записи данных в БД в IP_{url}'
            write_txt(text)
# Формируем кортеж data для записи в БД.
            urlrem = access_db(dbn, url, marker=1)
            data = (0, 0, 0, 0, 0.0, 0.0, url, urlrem, mistake_ip,
                    '', timewrite)                    
# Записываем ошибку в БД.        
            access_db(dbn, data)

            if mistake_ip == 'Ошибка записи данных в БД':   
               try:
                  data = (udprml0, udprml1, udprmr0, udprmr1, udspeedl, udspeedr, 
                          ipubnttwo, ipubnttworem, mistake_ip, detail_txt, timewrite)
                  access_db(dbn, data)                                
               except Exception: # Исключение.
                  mistake_ip = 'Ошибка записи данных в БД повторно'
# Записываем ошибку в текстовый файл logmistakes.txt.
                  text = f'{timewrite} --> Ошибка записи данных в БД повторно в IP_{url}'
                  write_txt(text)
# Формируем кортеж data для записи в БД.
                  urlrem = access_db(dbn, url, marker=1)
                  data = (0, 0, 0, 0, 0.0, 0.0, url, urlrem, mistake_ip,
                          '', timewrite)                    
# Записываем ошибку в БД.        
                  access_db(dbn, data)
                  
                  continue # Пропускаем эту итерацию цикла и переходим к следующему IP.                   
#----------------------------------------END--------------------------------------    
      elif subprocess.call(command) != 0: # Если url на ping не отозвался,
                                        # ПО ЛОКАЛЬНОМУ АДРЕСУ НЕТ ДОСТУПА.
#--ИЗМЕНЕНИЯ--------------------END PING------------------------------------------

# В переменную mistake_ip записываем название ошибки.
         mistake_ip = f'Нет доступа к локальному IP_{url}'
        
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
         text = f'{timewrite} --> Нет доступа к локальному IP_{url}'
         write_txt(text)
            
         if mistake_ip != 'Ошибок нет':         
# Получаем из БД IP адрес удалённой станции
# предполагаем, что к локальной станции нет доступа.

            url = access_db(dbn, urlloc, marker=1)
#--ИЗМЕНЕНИЯ--------------------ПИНГУЕМ IP(url)удалённый--------------------------
            command = ['ping', '-c', '1', url]
            if subprocess.call(command) == 0: # Если удалённый url на ping отозвался.
#----------------------------------АВТОРИЗАЦИЯ------------------------------------
               ses = r.Session()
               sget = ses.get(f'http://{url}/login.cgi?uri=/')
               try:         
                  spost = ses.post(f'http://{url}/login.cgi', params=payload)                                  
               except Exception: # Исключение.
                  mistake_ip = 'Ошибка авторизации'
# Записываем ошибку в текстовы файл  logmistakes.txt.
                  text = f'{timewrite} --> Ошибка авторизации в IP_{url}'
                  write_txt(text)
# Формируем кортеж data для записи в БД.
                  data = (0, 0, 0, 0, 0.0, 0.0, urlloc, url, mistake_ip,
                          '', timewrite)                    
# Записываем ошибку в БД.       
                  access_db(dbn, data)
                  if mistake_ip == 'Ошибка авторизации':            
                     try:
                        spost = ses.post(f'http://{url}/login.cgi', params=payload) 
                     except Exception: # Исключение.
                        ses.close() # Закрываем сессию.
                        mistake_ip = 'Ошибка авторизации повторно'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
                        text = f'{timewrite} --> Ошибка авторизации повторно в IP_{url}'
                        write_txt(text)
# Формируем кортеж data для записи в БД.
                        data = (0, 0, 0, 0, 0.0, 0.0, urlloc, url, mistake_ip,
                                '', timewrite)                            
# Записываем ошибку в БД.       
                        access_db(dbn, data) 
                        continue # Пропускаем эту итерацию цикла и переходим к следующему IP.        
#----------------------------------------END--------------------------------------

#-----------------------------------ПОЛУЧЕНИЕ JSON--------------------------------
               try:
                  sgetjson = ses.get(f'http://{url}/status.cgi').json()
#                 print(sgetjson)
               except Exception: # Исключение.
                  mistake_ip = 'Ошибка получения json'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
                  text = f'{timewrite} --> Ошибка получения json в IP_{url}'
                  write_txt(text)
            
# Формируем кортеж data для записи в БД.
                  data = (0, 0, 0, 0, 0.0, 0.0, urlloc, url, mistake_ip,
                          '', timewrite)                    
# Записываем ошибку в БД.        
                  access_db(dbn, data)

                  if mistake_ip == 'Ошибка получения json':   
                     try:
                        sgetjson = ses.get(f'http://{url}/status.cgi').json()
                     except Exception: # Исключение.
                        ses.close() # Закрываем сессию.
                        mistake_ip = 'Ошибка получения json повторно'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
                        text = f'{timewrite} --> Ошибка получения json повторно в IP_{url}'
                        write_txt(text)

# Формируем кортеж data для записи в БД.
                        data = (0, 0, 0, 0, 0.0, 0.0, urlloc, url, mistake_ip,
                                '', timewrite)                    
# Записываем ошибку в БД.        
                        access_db(dbn, data)
                        continue # Пропускаем эту итерацию цикла и переходим к следующему IP.
               ses.close() # Закрываем сессию.  
#----------------------------------------END--------------------------------------            

#----------------------------ОБРАБАТЫВАЕМ ПОЛУЧЕННЫЙ JSON-------------------------
               try:
                  udprml0flag = sgetjson['airfiber']['remote_rxpower0']  # -57
                  udprml1flag = sgetjson['airfiber']['remote_rxpower1']  # -58
                  
                  udprmr0 = sgetjson['airfiber']['rxpower0']   # -54
                  udprmr1 = sgetjson['airfiber']['rxpower1']   # -53
                  
                  if udprml0flag == -1000:
                     udprml0 = 0
                  elif udprml1flag == -1000:
                     udprml1 = 0
                  else:
                     udprml0 = udprml0flag
                     udprml1 = udprml1flag

                  udspeedr = round(sgetjson['airfiber']['txcapacity']/1000000, 2)   # 302.30
                  udspeedl = round(sgetjson['airfiber']['rxcapacity']/1000000, 2)   # 301.60
                  ipubnttwo = urlloc
            
                  ipubnttworemflag = sgetjson['airfiber']['remote_ip']
                  if ipubnttworemflag == 'n/a':
                     ipubnttworem = url
                  else:
                     ipubnttworem = ipubnttworemflag
              
                  namerrl = sgetjson['wireless']['essid']
                  namerrs = sgetjson['host']['hostname']
                  distrrl = str(sgetjson['wireless']['distance']/1000)
                  rx_freq = str(sgetjson['airfiber']['rx_frequency']/1000)
                  tx_freq = str(sgetjson['airfiber']['tx_frequency']/1000)
                  rxchanbw = sgetjson['airfiber']['rxchanbw']
                  txmodrate = sgetjson['airfiber']['txmodrate']
                  linkmode = sgetjson['airfiber']['linkmode']
               
                  detail_txt = namerrl + ' ' + namerrs + ' ' + distrrl + ' ' + rx_freq + ' ' +\
                               tx_freq + ' ' + rxchanbw + ' ' + txmodrate + ' ' + linkmode + ' ' + ipubnttworem
# Записываем собранные данные в txt-файл detail.txt.         
                  with open(f'/home/zarya/project/ubntserver/sell/ip{url}_detail.txt'', 'w', encoding='utf-8') as f:
                     f.write(detail_txt)
               except Exception: # Исключение.
                  mistake_ip = 'Ошибка формирования данных для записи в БД'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
                  text = f'{timewrite} --> Ошибка формирования данных для записи в БД в IP_{url}'
                  write_txt(text)

# Формируем кортеж data для записи в БД.
                  data = (0, 0, 0, 0, 0.0, 0.0, urlloc, url, mistake_ip,
                          '', timewrite)                    
# Записываем ошибку в БД.        
                  access_db(dbn, data)

                  continue # Пропускаем эту итерацию цикла и переходим к следующему IP.
               
# Записываем данные РРЛ в БД.        
               try:   
                  data = (udprml0, udprml1, udprmr0, udprmr1, udspeedl, udspeedr,
                          ipubnttwo, ipubnttworem, mistake_ip, detail_txt, timewrite)
#                  print(data)
                  access_db(dbn, data)
               except Exception: # Исключение.
                  mistake_ip = 'Ошибка записи данных в БД'
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
                  text = f'{timewrite} --> Ошибка записи данных в БД в IP_{url}'
                  write_txt(text)
# Формируем кортеж data для записи в БД.
                  data = (0, 0, 0, 0, 0.0, 0.0, urlloc, url, mistake_ip,
                          '', timewrite)                    
# Записываем ошибку в БД.        
                  access_db(dbn, data)

                  continue # Пропускаем эту итерацию цикла и переходим к следующему IP.                   
#----------------------------------------END--------------------------------------    
   
            elif subprocess.call(command) != 0: # Если url на ping не отозвался,
                                                # ПО УДАЛЁННОМУ АДРЕСУ НЕТ ДОСТУПА.
#--ИЗМЕНЕНИЯ--------------------END PING----------------------------------------

# В переменную mistake_ip записываем название ошибки.
               mistake_ip = f'Нет доступа к удалённому IP_{url}'
        
# Записываем ошибку в текстовы йфайл  logmistakes.txt.
               text = f'{timewrite} --> Нет доступа к удалённому IP_{url}'
               write_txt(text)
# Формируем кортеж data для записи в БД.
               data = (0, 0, 0, 0, 0.0, 0.0, urlloc, url, mistake_ip,
                       '', timewrite)                            
# Записываем ошибку в БД.
               access_db(dbn, data)
               continue # Пропускаем эту итерацию цикла и переходим к следующему IP.
      time.sleep(1)                  
#----------------------------------------END-------------------------------------- 
















