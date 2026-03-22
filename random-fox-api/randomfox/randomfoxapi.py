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
        self._original = None
        self._baseurl = 'https://randomfox.ca/floof/'
    
    def fetch_image(self):
        """
        Parameters
        ----------
        No parameters
        
        Description:
        -----------
        Performs a GET request to the API, and stores the image

        Raises
        ------
        requests.RequestException
            If the network request fails.
        PIL.UnidentifiedImageError
            If the response content is not a valid image.
        """
        try:
            response = requests.get(self._baseurl)
            response.raise_for_status()
            data = response.json()
            self._imgurl = data['image']
            img_response = requests.get(data['image'])
            img_response.raise_for_status()
            tmp = Image.open(BytesIO(img_response.content))
            self._original = tmp
            self.img = tmp
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

        Raises
        ------
        ValueError
            If size is invalid or no image has been fetched.
        """
        if self.img is None:
            raise ValueError('No image to resize. Call fetch_image() first.')

        if isinstance(size, int):
            new_size = (size, size)
        elif isinstance(size, (list, tuple)) and len(size) == 2:
            w, h = size
            if not (isinstance(w, int) and isinstance(h, int)):
                raise ValueError('Both dimensions must be integers.')
            new_size = w, h
        else:
            raise ValueError('Error: size must be an int or a tuple/list of two positive ints')
        
        if not all(isinstance(x, int) and x > 0 for x in new_size):
            raise ValueError('Error: dimensions must be positive integers')

        self.img = self._original.resize(new_size)
        self.imgsize = self.img.size
            
    def restore_image(self):
        """
        Parameters
        ----------
        No parameters
        
        Description:
        -----------
        Replaces the existing image with the original one.

        Raises
        ------
        ValueError
            If no original image exists (fetch_image not called yet).
        """
        if self._original is None:
            raise ValueError("No original image to restore. Call fetch_image() first.")
        self.img = self._original
        self.imgsize = self.img.size
        
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
        if self.img is None:
            raise ValueError('No image to save. Call fetch_image() first.')

        img = self.img.convert('RGB')

        if name:
            if self._imgurl:
                ext = self._imgurl.split('/')[-1].split('.')[-1]
            else:
                ext = '.jpg'
            imgname = f'{name}.{ext}'
        else:
            imgname = 'fox.jpg'
        
        if path:
            expanded_path = os.path.expanduser(path)
            if not os.path.exists(expanded_path):
                print(f'Directory {expanded_path} does not exist.')
                return
            full_path = os.path.join(expanded_path, imgname)
        else:
            full_path = os.path.join('/tmp', imgname)
        
        img.save(full_path)
        print(f'{imgname} saved at {os.path.dirname(full_path)}')