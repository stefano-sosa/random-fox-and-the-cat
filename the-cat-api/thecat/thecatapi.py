def message(moduleName):
    print(f'Install {moduleName}')
    print('If you are using pipenv:')
    print(f'\tpipenv install {moduleName}')
    print('If you want to install it globally:')
    print(f'\tpip install {moduleName}')

import os

import json

import random

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

try:
    import numpy
except ModuleNotFoundError:
    message('numpy')
    
try:
    import pandas as pd
except ModuleNotFoundError:
    message('pandas')

class catAPI:
    
    def __init__(self):
        self.data = []
        self.collage = None
        self.breeds = None
        self.__urls = []
        self.__imgs = []
        self.__breedsdeco = {}
        self.__scheme = 'https'
        self.__netloc = 'api.thecatapi.com'
        self.version = ''
    
    def __buildURL(self, *, scheme='', netloc='', path='', url='', query_params={}, fragment=''):
        Components = namedtuple(
            typename='Components', 
            field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
        )
        
        return urlunparse(
            Components(
                scheme=scheme,
                netloc=netloc,
                query=urlencode(query_params),
                path=path,
                url=url,
                fragment=fragment
            )
        )
    
    def req_version(self):
        url = self.__buildURL(scheme=self.__scheme, netloc=self.__netloc)
        req = requests.get(url)
        loads = json.loads(req.content)
        self.version = f"{loads['message']} {loads['version']}"
        
    def req_breeds(self):
        url = self.__buildURL(
            scheme = self.__scheme, 
            netloc = self.__netloc, 
            path = '', 
            url = '/v1/breeds', 
            query_params={}, 
            fragment=''
        )
        req = requests.get(url)
        loads = json.loads(req.content.decode('utf8'))
        idsandnames = []
        for load in loads:
            self.__breedsdeco[load['name']] = load['id']
            idsandnames.append({'Name':load['name'], 'id':load['id']})
        self.breeds  = pd.DataFrame(idsandnames)
        
    def __storeurls(self):
        self.__urls = []
        for load in self.data:
            if load['url'] not in self.__urls:
                self.__urls.append(load['url'])
            
    def __storeimgs(self):
        self.__imgs = []
        for url in self.__urls:
            dataurlres = requests.get(url)
            if dataurlres not in self.__imgs:
                self.__imgs.append(dataurlres.content)
            
    def req_images(self, *, limit=1, breed='', size='small'):
        query_params = {
            'limit' : limit,
            'size' : size,
            'breed_ids' : self.__breedsdeco.get(breed, '')
        }
        url = self.__buildURL(
            scheme = self.__scheme, 
            netloc = self.__netloc, 
            path = '', 
            url = 'v1/images/search', 
            query_params = query_params, 
            fragment = ''
        )
        req = requests.get(url)
        data = json.loads(req.content)
        if len(data) > limit:
            data = random.sample(data, limit)
        self.data = data
        self.__storeurls()
        self.__storeimgs()
        
    def resize(self, factor):
        try:
            for i, img in enumerate(self.__imgs):
                rows, cols = img.size
                self.__imgs[i] = img.resize((rows // factor, cols // factor))
        except:
            raise ValueError(f'{factor} is not a valid factor')
            
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