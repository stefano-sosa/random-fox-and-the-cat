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
        self._original_images = []
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

        self._original_images = self.images
        resized_images = []
        for img in self.images:
            rows, cols = img.size
            resized_images.append(img.resize((int(rows * factor), int(cols * factor))))

        self.images = resized_images

    def restore_images(self):
        """
        Parameters
        ----------
        No parameters
        
        Description:
        -----------
        Replaces the existing images with the originals.

        Raises
        ------
        ValueError
            If no original images exists.
        """
        if not self._original_images:
            raise ValueError('No original image to restore. Call resize_images() first')
        self.images = self._original_images
    
    def create_collage(self, cell_size=256):
        """
        Parameters
        ----------
        cell_size : int
            Size of each cell in pixels (width and height).

        Description:
        -----------
        Create a collage from downloaded images, arranging them as square as possible

        Raises
        ------
        ValueError
            If no images are available.
        """
        n = len(self.images)
        if n == 0:
            raise ValueError('No images to create collage. Call download_images() first.')

        rows = 1
        for i in range(2, n):
            if n % i == 0:
                rows = i
                break

        cols = n // rows

        collage_width = cols * cell_size
        collage_height = rows * cell_size
        collage = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))

        x = 0
        for i in range(rows):
            y = 0
            for j in range(cols):
                cat = self.images[i*cols+j].convert('RGB')
                photo = cat.resize((cell_size, cell_size))        
                collage.paste(photo, (x,y))
                y += cell_size
            x += cell_size

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