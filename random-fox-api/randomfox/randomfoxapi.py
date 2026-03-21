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
    
class RandomFoxAPI:
    """
    Class used to request a random image of an fox

    Attributes
    ----------
    img : Image
        Image requested
    imgsize : tuple
        the dimensions of the image

    Methods
    -------
    req_image()
        Request the image
        
    resize_image(size)
        Replaces the existing image with a new one with the dimensions indicated in 'size'
        
    save_image(name, path)
        Saves the existing
    """
    
    def __init__(self):
        """
        Parameters:
        ----------
        No parameters
        
        Description:
        -----------
        Inits the class
        """
        self.__imgurl = None
        self.img = None
        self.imgsize = None
        self.__baseurl = 'https://randomfox.ca/floof/'
    
    def req_image(self):
        """
        Parameters
        ----------
        No parameters
        
        Description:
        -----------
        Performs a GET HTTP request to the endpoint of the API, and stores the image in the img attribute
        """
        req = requests.get(self.__baseurl)
        load = json.loads(req.content)
        self.__imgurl = load['image']
        imagereq = requests.get(load['image'])
        self.__original = Image.open(BytesIO(imagereq.content)) 
        self.img = self.__original
        self.imgsize = self.img.size
       
    def __str_msg(self, arg):
        return f'{arg} is string, and must be a positive integer'
    
    def __list_msg(self, arg):
        a, b = arg
        return f'{a} is {type(a)}, {b} is {type(b)}, and both must be positive integers'
    
    def __tuple_msg(self, arg):
        a, b = arg
        return f'{a} is {type(a)}, {b} is {type(b)}, and both must be positive integers'
    
    def __switch_msg(self, arg):
        tipo = type(arg)
        argdecode = {
            str : self.__str_msg,
            list : self.__list_msg, 
            tuple : self.__tuple_msg
        }
        return argdecode[tipo](arg)
        
    def resize_image(self, size=()):
        """
        Parameters
        ----------
        size: int, tuple, list
        
        Description:
        -----------
        Resize the existing image with the size specified in 'size', and then replaces it.
        """
        try:
            if isinstance(size, int):
                isize = size, size
            else:
                isize = size[0], size[1]
            self.img = self.img.resize(isize)
        except TypeError:
            print(self.__switch_msg(size))
            
    def restore_image(self):
        """
        Parameters
        ----------
        No parameters
        
        Description:
        -----------
        Replaces the existing image with the original one.
        """
        self.img = self.__original
        
    def save_image(self, *, name='', path=''):
        """
        Parameters
        ----------
        path: str
        name: str
        
        Description:
        -----------
        Saves the image requested  in the path indicated in path, with name indicated in name.
        If no name is indicated, the class will use the name indicated in the response of the API.
        If no path is indicated the class will save the image in /tmp
        """
        img = self.img.convert('RGB')

        if name:
            ext = self.__imgurl.split('/')[-1].split('.')[-1]
            imgname = name + '.' + ext
        else:
            imgname = self.__imgurl.split('/')[-1]
        
        ipath = ''
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
                return 
        else:
            ipath = os.path.join('/','tmp')
            img.save(os.path.join(ipath,imgname))
            
        print(f'{imgname} saved at {ipath}')