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

try:
    import numpy
except ModuleNotFoundError:
    message('numpy')
    
try:
    import pandas as pd
except ModuleNotFoundError:
    message('pandas')

class catAPI:
    def __decodeparams(self):
        validparams = {'limit':'limit','breed':'breed_ids'}
        for param in self.params:
            try:
                self.queries[validparams[param]] = self.params[param]
            except:
                raise ValueError(f'{param} is not a valid parameter')
    
    def __buildurl(self): 
        self.__baseurl = (self.__url + '?' + urllib.parse.urlencode(self.queries))
    
    def __init__(self, *args, **params):
        self.data = []
        self.collage = None
        self.breeds = None
        self.__urls = []
        self.__imgs = []
        self.params = params
        self.queries = {}
        self.__url = 'https://api.thecatapi.com/v1/images/search'
        
    def __geturls(self):
        self.__urls = []
        for load in self.data:
            self.__urls.append(load['url'])
            
    def __getimgs(self):
        self.__imgs = []
        for url in self.__urls:
            dataurlres = requests.get(url)
            self.__imgs.append(Image.open(BytesIO(dataurlres.content)))
            
    def getdata(self):
        self.__decodeparams()
        self.__buildurl()
        reqs = requests.get(self.__baseurl)
        self.data = json.loads(reqs.content.decode('utf8').replace("'", '"'))
        self.__geturls()
        self.__getimgs()
        
    def getbreeds(self):
        breedurl = 'https://api.thecatapi.com/v1/breeds'
        req = requests.get(breedurl)
        loads = json.loads(req.content.decode('utf8'))
        idsandnames = []
        for load in loads:
            idsandnames.append({'Name':load['name'], 'id':load['id']})
        self.breeds  = pd.DataFrame(idsandnames)
        
    def resize(self, factor):
        try:
            for i, img in enumerate(self.__imgs):
                rows, cols = img.size
                self.__imgs[i] = img.resize((rows // factor, cols // factor))
        except:
            raise ValueError(f'{size} is not a valid size')
            
    def __getitem__(self, args):    
        if not isinstance(args, int):
            raise ValueError(f'{args} has to be an integer')
        return self.__imgs[args]
    
    def create_collage(self, tam=500):
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
                cat = self.__imgs[i*ncols+j].convert("RGBA")
                photo = cat.resize((500,500))        
                collage.paste(photo, (x,y))
                y += 500
            x += 500
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