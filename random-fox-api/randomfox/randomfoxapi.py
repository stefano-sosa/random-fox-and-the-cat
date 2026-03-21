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
    fetch_image()
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
        self._imgurl = None
        self.img = None
        self.imgsize = None
        self._baseurl = 'https://randomfox.ca/floof/'
    
    def fetch_image(self):
        """
        Parameters
        ----------
        No parameters
        
        Description:
        -----------
        Performs a GET request to the API, and stores the image
        """
        try:
            response = requests.get(self._baseurl)
            response.raise_for_status()
            data = response.json()
            self._imgurl = data['image']
            img_response = requests.get(data['image'])
            img_response.raise_for_status()
            self._original = Image.open(BytesIO(img_response.content))
            self.img = self._original
            self.imgsize = self.img.size
        except requests.exceptions.RequestException as e:
            print(f'Network error while fetching image: {e}')
            raise
        except (json.JSONDecodeError, KeyError) as e:
            print(f'Unexpected API response: {e}')
        except Exception as e:
            print(f'Failed to open image: {e}')
            raise
        
    def resize_image(self, size=()):
        """
        Parameters
        ----------
        size: int, tuple, list
        
        Description:
        -----------
        Resize the existing image with the size specified in 'size', and then replaces it.
        """
        if isinstance(size, int):
            new_size = (size, size)
        elif isinstance(size, (list, tuple)) and len(size) == 2:
            new_size = (size[0], size[1])
        else:
            print('Error: size must be an int or a tuple/list of two positive ints')
            return
        
        if not all(isinstance(x, int) and x > 0 for x in new_size):
            print("Error: dimensions must be positive integers")
            return

        self.img = self.img.resize(new_size)
            
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