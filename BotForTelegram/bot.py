import json
import urllib
import urllib.parse
import urllib.request
import time

token = '286467152:AAHoaIuKHfLgauyqSHfahbT9ZVguHPIoeU4'
api = 'https://api.telegram.org/bot'
boturl = api + token

chatid = 313057158

lastoffset = 209649278

class bot(object):
  API = 'https://api.telegram.org/bot'

  def __init__(self, atoken):
    self.url = bot.API + atoken

  def sendmsg(self, chat_id, text):
    query = dict(chat_id=chat_id, text=text)
    get = self.url + '/sendMessage?' + urllib.parse.urlencode(query)
    response = urllib.request.urlopen(get)
    self.checkresponse(response)

  def checkresponse(self, response):
    res_js = json.loads(response)
    if not res_js['ok']:
      raise RuntimeError('checkResponse error')
      
def getUpdates(offset):
  get = boturl + '/getUpdates?offset=' + str(offset)
  response = urllib.request.urlopen(get)
  return response.read().decode('utf-8')

mybot = bot(token)  
  
#print(getUpdates())
#mybot.sendmsg(chatid, 'Ddddd') 
cmd = ''
upd_respons = True
#todo need to use webhooks 
while cmd != '/end2':
  upd = getUpdates(lastoffset) 
  upd = json.loads(upd)
  #upd_respons = upd['ok']
  for elem in upd['result']:
    lastoffset = elem['update_id']
    cmd = elem['message']['text']
    chatid = elem['message']['chat']['id']
    print(cmd)
    if cmd == 'Hi!':
      mybot.sendmsg(chatid, 'Hello man!! I think i am alone here!')
  lastoffset = elem['update_id'] + 1    
  #time.sleep(500)

#print(cmd)  

