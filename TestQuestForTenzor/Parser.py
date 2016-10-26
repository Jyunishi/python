import sys
import string
import re

class _Reader():#класс осуществляющий движение по строке
    def __init__(self, atext):
        buflist = atext.split('\n')
        self.text = ''.join(buflist)
        self.pos = 0
        self.completed = False
        #print(self.text)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            to_return = self.text[self.pos]
        except IndexError:
            self.completed = True
            raise StopIteration
        
        self.pos += 1
        return to_return
    
    def seek_back(self, num):
        self.pos += num

class TParser:#класс разбирающий пакет
    allowed_chars = '":},abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮйцукенгшщзхъфывапролджэячсмитьбюёЁ'
    allowed_types = ['integer', 'boolean', 'string']
    bool_vals = ['true', 'false', '1', '2', 'y', 'n']
    errflag = False
    errmsg = ''
    objects = {}#в этот словарь идет разбор пакета
    errordicts = {
        0:'Данные успешно обработаны',
        1:'Ошибка формата пакета: нарушена общая структура',
        2:'В процессе разбора пакета возникли ошибки'
        }
    objerrors = {}# в этот словарь идет запись ошибок
    def __init__(self, file, log):
        text = file.read() if type(file) != str else file
        self.i = _Reader(text)
        try:
            self.logfile = open(log, 'w')
        except IOError as e:
            self.errflag = True
            self.errmsg = u'Не удалось открыть файл лога'

    def startlog(self, errorcode):
        if not self.errflag:
            self.logfile.write('{\n')
            self.logfile.write('    "КодОшибки":' + str(errorcode) +'\n')
            self.logfile.write('    "Примечание":' + self.errordicts[errorcode] + '\n')
    def writelog(self, msg):
        if not self.errflag:        
            self.logfile.write(msg + '\n')
    def endlog(self):
        if not self.errflag:
            self.logfile.write('}')
            self.logfile.close()
    def tryint(self, i):
        try: 
            int(i)
            return True
        except ValueError:
            return False
            
    def checkobjects(self):#проверяет валидность разобранного пакета
        msg = []
        valuesnotfound = False
        typesnotfound = False
        for key in self.objects.keys():
            if not 'Данные' in self.objects[key]:
                msg.append('"Секция Данные отсутствует"')
                valuesnotfound = True
            if not 'Типы' in self.objects[key]:
                msg.append('"Секция Типы отсутствует"')
                typesnotfound = True
            if not valuesnotfound and not typesnotfound:
                tlen = len(self.objects[key]['Типы'])
                vlen = len(self.objects[key]['Данные'])
                if tlen > vlen:
                    msg.append('"Количество типов больше количества данных"')
                elif vlen > tlen:
                    msg.append('"Количество данных больше количества типов"')
                for vkey in self.objects[key]['Данные'].keys():
                    if not vkey in self.objects[key]['Типы'].keys():
                        msg.append('"Для поля ' + vkey + ' не определен тип"')
                        continue
                    if self.objects[key]['Типы'][vkey] == 'integer' and not self.tryint(self.objects[key]['Данные'][vkey]):
                        msg.append('"'+vkey + ' не соответствует integer')
                        continue
                    if self.objects[key]['Типы'][vkey] == 'boolean' and not self.objects[key]['Данные'][vkey].lower() in self.bool_vals:
                        msg.append('"'+vkey + ' не соответствует boolean')
                        continue
                    if self.objects[key]['Типы'][vkey] not in self.allowed_types:
                        msg.append('"' + vkey + ' имеет не соответствующий тип(int bool str)"')
                for tkey in self.objects[key]['Типы'].keys():        
                    if tkey not in self.objects[key]['Данные'].keys():
                        msg.append('"' + tkey + ' не имеет данных"')
            if len(msg)!=0:
                self.objerrors[key] = msg.copy()
            msg.clear()
            valuesnotfound = False
            typesnotfound = False
        if len(self.objerrors.keys()) != 0:
            self.startlog(2)
            for objkey in self.objerrors.keys():
                self.writelog(objkey + ':' + str(self.objerrors[objkey]))
            self.endlog()
        else:
            self.startlog(0)
            self.endlog()
        
    
            
    def Parse(self):#осуществляет разбор пакета
        bracer = 0
        bufch = ''
        typeisopen = True
        typesdict = {}
        valsdict = {}
        types = ''
        objname = ''
        vals = ''
        try:
            for ch in self.i:
                if ch =='{':
                    bracer += 1
                if ch =='}':
                    bracer -= 1
                if ch == '"':
                    if bracer == 1:
                        objname = self.readname()
                    elif bracer == 2:
                        if typeisopen:
                            types = self.readname()
                            typeisopen = False
                        else:
                            vals = self.readname()
                            typeisopen = True
                    elif bracer == 3:
                        ch = self.i.seek_back(-1)
                        if typeisopen:
                            valsdict = self.getvallist()
                        else:
                            typesdict = self.getvallist()
                if bracer == 1 and objname != '' and types != '' and vals !='':
                    self.objects[objname] = {types:typesdict.copy(), vals:valsdict.copy()}
                    objname = ''
                    types = ''
                    vals = ''
                    typesdict.clear()
                    valsdict.clear()
            print(self.objects)
        except Exception:
            self.errflag = True
            self.errmsg = u'Произошла ошибка разбора пакета.'
            self.startlog(1)
            self.endlog()
        
                    
    def getvallist(self):#получает список название поля-значение
        to_ret = {}
        valflag = False
        startharv = False
        field = ''
        value = ''
        for ch in self.i:
            if ch == '}':
                self.i.seek_back(-1)
                return to_ret
                break
            if ch == '"':
                startharv = True
                ch = next(self.i)
                if ch == ',':
                    valflag = False
                    startharv = False
                    field = field.strip()
                    value = value.strip()
                    to_ret[field] = value
                    field = ''
                    value = ''
                    continue
                if ch == ':':
                    valflag = True
                    continue
            if ch != '"' and startharv:
                if valflag == True:
                    value += ch
                else:
                    field += ch

                               
    def readname(self):#читает название элемента
        to_ret = ''
        for ch in self.i:
            if ch != '"':
                to_ret = to_ret + ch
            else:
                break
        return to_ret    

            
print(u'Введите путь к файлу пакета.')
NameFileImport = input()
print(u'Введите путь к файлу лога.')
log_file = input()
FileImport = ''
try:
    FileImport = open(NameFileImport)
except IOError as e:
    print(u'Не удалось открыть файл')
else:
    with FileImport:
        print(u'Нашли файл, начинаем обработку')
     #   print(FileImport.read())
        parser = TParser(FileImport, log_file)
        parser.Parse()
        if parser.errflag:
            print(parser.errmsg)
        else:
            parser.checkobjects();
            print(u'Обработка пакета завершилась, подробности в фале лога')
        #Parser.tprint()
        FileImport.close()
pause = input()        
#sys.exit()
