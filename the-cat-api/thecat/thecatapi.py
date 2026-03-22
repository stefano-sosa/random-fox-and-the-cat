def message(moduleName):
    print(f'Install {moduleName}')
    print('If you are using pipenv:')
    print(f'\tpipenv install {moduleName}')
    print('If you want to install it globally:')
    print(f'\tpip install {moduleName}')

import os

import random

import json

from io import BytesIO

from collections import namedtuple

from urllib.parse import urljoin, urlencode, urlparse, urlunparse

try:
    from PIL import Image
except ModuleNotFoundError:
    message('image')
    message('pillow')

try:
    import requests
except ModuleNotFoundError:
    message('requests')

class CatAPI:
    
    def __init__(self):
        self._baseurl = 'https://api.thecatapi.com'
        self.data = []
        self.collage = None
        self.breeds = []
        self.version = None
        self.images = []
    
    def fetch_version(self):
        """
        Parameters
        ----------
        No parameters
        
        Description:
        -----------
        Performs a GET request to the API, and stores the version

        Raises
        ------
        requests.RequestException
            If the network request fails.
        """
        try:
            response = requests.get(self._baseurl)
            response.raise_for_status()
            data = response.json()
            self.version = f'{data["message"]} {data["version"]}'
        except requests.exceptions.RequestException as e:
            print(f'Network error while fetching data: {e}')
            raise
        except (json.JSONDecodeError, KeyError) as e:
            print(f'Unexpected API response: {e}')
        except Exception as e:
            print(f'Error: {e}')
            raise
        
    def fetch_breeds(self):
        """
        Parameters
        ----------
        No parameters
        
        Description:
        -----------
        Performs a GET request to the API, and stores the cat breeds

        Raises
        ------
        requests.RequestException
            If the network request fails.
        """
        try:
            url = urljoin(self._baseurl, '/v1/breeds')
            response = requests.get(url)
            response.raise_for_status()
            breeds = response.json()
            self.breeds = [{'id':breed['id'], 'name':breed['name']} for breed in breeds]
        except requests.exceptions.RequestException as e:
            print(f'Network error while fetching data: {e}')
            raise
        except (json.JSONDecodeError, KeyError) as e:
            print(f'Unexpected API response: {e}')
        except Exception as e:
            print(f'Error: {e}')
            raise
            
    def fetch_images(self, *, limit=1, breed='', size='small'):
        """
        Parameters
        ----------
        limit: int
            Maximum number of images to request
        breed: str
            Breed name (must be one of the available breeds)
        size : str
            Image size ('small', 'med', 'full')
        
        Description:
        -----------
        Performs a GET request to the API, and fetch the cat images

        Raises
        ------
        requests.RequestException
            If the network request fails.
        """
        breed_id = ''
        if breed:
            for b in self.breeds:
                if b['name'].lower() == breed.lower():
                    breed_id = b['id']
                    break
            if not breed_id:
                raise ValueError(f'Breed {breed} not found. Call fetch_breeds() first or check spelling')
        
        if not isinstance(limit, int):
            raise ValueError(f'Invalid limit {limit}. It should be an integer')

        if limit < 0:
            raise ValueError(f'Invalid limit {limit}. It should be a positive integer')

        allowed_sizes = ('small', 'med', 'full')
        if size not in allowed_sizes:
            raise ValueError(f'Invalid size "{size}". Allowed values: {", ".join(allowed_sizes)}')
        
        try:
            url = urljoin(self._baseurl, '/v1/images/search')
            params = {
                'limit': limit,
                'size': size,
                'breed_ids': breed_id
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if len(data) > limit:
                data = random.sample(data, limit)
            self.data = data
        except requests.exceptions.RequestException as e:
            print(f'Network error while fetching data: {e}')
            raise
        except (json.JSONDecodeError, KeyError) as e:
            print(f'Unexpected API response: {e}')
        except Exception as e:
            print(f'Error: {e}')
            raise

    def download_images(self):
        """
        Parameters
        ----------
        No parameters

        Description:
        -----------
        Download all images from the current data

        Raises
        ------
        ValueError
            If no data has been fetched.
        requests.RequestException
            If any download fails.
        """
        if not self.data:
            raise ValueError('No images. Call fetch_images() first')

        self.images = []
        for item in self.data:
            img_url = item.get('url')
            if not img_url:
                continue
            try:
                img_response = requests.get(img_url)
                img_response.raise_for_status()
                img = Image.open(BytesIO(img_response.content)).convert('RGB')
                self.images.append(img)
            except Exception as e:
                print(f'Could not download image {img_url}: {e}')
                continue
        
    def resize_images(self, factor):
        """
        Parameters
        ----------
        factor : float
            Scaling factor (must be > 0). If factor < 1, images shrink

        Description:
        -----------
        Resize all downloaded images by a factor

        Raises
        ------
        ValueError
            If no data has been fetched.
            If factor is not a floating point number
            If factor is negative
        """
        if not self.data:
            raise ValueError('No images. Call fetch_images() first')

        if not isinstance(factor, float):
            raise ValueError('Factor must be a float number')

        if factor <= 0:
            raise ValueError('Factor must be positive')

        resized_images = []
        for img in self.images:
            rows, cols = img.size
            resized_images.append(img.resize((rows * factor, cols * factor)))

        self.images = resized_images
            
    def __getitem__(self, args):    
        if not isinstance(args, int):
            raise ValueError(f'{args} has to be an integer')
        try:
            return Image.open(BytesIO(self.__imgs[args])).resize((256, 256))
        except IndexError:
            numel = len(self.__urls)
            print(f"There are only {numel} {'element' if numel==1 else 'elements'}")
    
    def create_collage(self, tam=256):
        nrows = 1
        ncols = 1
        numel = len(self.data)
        
        if not numel:
            print('No collage can be made without images')
            return 
        
        for i in range(2,numel):
            if numel % i == 0:
                nrows = i
                break
                
        ncols = numel // nrows
        
        collage = Image.new("RGBA", (nrows*tam, ncols*tam), color=(255,255,255,255))
        
        x = 0
        for i in range(nrows):
            y = 0
            for j in range(ncols):
                imgdata = self.__imgs[i*ncols+j]
                cat = Image.open(BytesIO(imgdata)).convert("RGBA")
                photo = cat.resize((tam, tam))        
                collage.paste(photo, (x,y))
                y += tam
            x += tam
        self.collage = collage
        
    def save(self):
        for data, img in zip(self.data,self.__imgs):
            name = data['url'].split('/')[-1]
            img.save(os.path.join(os.environ['HOME'],'pics',name))
    
    def save_collage(self, name=''):
        im = self.collage.convert('RGB')
        if not name:
            im.save(os.path.join(os.environ['HOME'],'pics','collage-'+self.queries['breed_ids']+'.jpg'))
        else:
            im.save(os.path.join(os.environ['HOME'],'pics',f'{name}-'+self.queries['breed_ids']+'.jpg'))