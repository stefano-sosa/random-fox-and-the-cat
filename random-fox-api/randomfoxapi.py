def message(moduleName):
    print(f'Install {moduleName}')
    print('If you are using pipenv:')
    print(f'\tpipenv install {moduleName}')
    print('If you want to install it globally:')
    print(f'\tpip install {moduleName}')
    
import os

import json

import urllib.parse

from io import BytesIO

try:
    from PIL import Image
except ModuleNotFoundError:
    message('image')
    message('pillow')

try:
    import requests
except ModuleNotFoundError:
    message('requests')
    
class randomfoxAPI:
    
    def __init__(self):
        self.__imgurl = None
        self.__imgname = None
        self.img = None
        self.imgsize = None
        self.__baseurl = 'https://randomfox.ca/floof/'
    
    def req_image(self):
        req = requests.get(self.__baseurl)
        load = json.loads(req.content)
        self.__imgurl = load['image']
        imagereq = requests.get(load['image'])
        self.img = Image.open(BytesIO(imagereq.content))
        self.imgsize = self.img.size

    def __arg_int(self, myint):
        return myint, myint
    
    def __arg_list(self, mylist):
        return mylist[0], mylist[1]

    def __arg_tuple(self, mytuple):
        return mytuple[0], mytuple[1]
    
    def __switch_arg(self, arg):
        #tipo = type(arg)
        #argdecode = {int : self.__arg_int(arg), list : self.__arg_list(arg), tuple : self.__arg_tuple(arg)}
        #isize = argdecode[tipo]
        #return isize
        #print(isize)
        if isinstance(arg, int):
            return self.__arg_int(arg)
        
        if isinstance(arg, list):
            return self.__arg_list(arg)
        
        if isinstance(arg, tuple):
            return self.__arg_tuple(arg)
        
        raise ValueError(f'{arg} is {type(arg)}. The argument must an integer, a list, or a tuple.')
        
    def resize_image(self, size=()):
        try:
            isize = self.__switch_arg(size)
            self.img = self.img.resize(isize)
        except TypeError:
            a, b = size
            print(f'{a} is {type(a)}, {b} is {type(b)}, and both must be integers')
        
    def save_image(self, *, path='', name=''):
        img = self.img.convert('RGB')

        if name:
            ext = self.__imgurl.split('/')[-1].split('.')[-1]
            imgname = name + '.' + ext
        else:
            imgname = self.__imgurl.split('/')[-1]
            
        if path:
            istilde = path.split('/')[0] == '~'
            if istilde:
                ipath = os.path.join(os.environ['HOME'], *(path[1:].split('/')))
            else:
                ipath = path
                
            if os.path.exists(ipath):
                img.save(os.path.join(ipath,imgname))
            else:
                print(f'{ipath} does not exist')
        else:
            img.save(os.path.join('/','tmp',imgname))