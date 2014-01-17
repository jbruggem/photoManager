'''
Created on Jan 31, 2011

@author: jehan
'''
import yaml
import os.path


class Config():
    _config = None
    _cache={}
    
    def __init__(self,configfile):
        self._config = yaml.load(open(configfile))
        print "[config] loading config"
        print len(self._config)," keys"
        #print self._config
        
    def  __getitem__(self,key):
        path = key.split('.')
        ret = self._config
        for k in path:
            ret = ret[k]
            
        return ret
    
    def g(self,keypath):
        d = self._config
        try:
            for k in keypath:
                d = d[k]
            return d
        except KeyError as e:
            print "KeyError:",e
            print "Key not found:",keypath
            return ''
        
            
    def __getattr__(self,name):
        try:
            return self._cache[name]
        except KeyError:
            pass
        
        print "[config] reading ",name
        
        if name == 'make_fusioned_folder_names':
            value = self._config['config']['make_fusioned_folder_names']

        elif name == 'use_original_folder_names':
            value = self._config['config']['use_original_folder_names']
        
        elif name == 'dump_folder':
            value = os.path.join(self.import_folder,self._config['paths']['dump']) 
                     
        elif name == 'move_folder':
            value = os.path.join(self.import_folder,self._config['paths']['to_move'])
         
        elif name == 'rename_folder':
            value = os.path.join(self.import_folder,self._config['paths']['to_rename'])
                  
        elif name == 'root_folder':
            value = os.path.join(self._config['config']['root_photos_folder'])
         
        elif name == 'import_folder':
            value = os.path.join(self.root_folder,self._config['paths']['import'])       
                
        elif name == 'jpeg_folder':
            value = os.path.join(self.root_folder,self._config['paths']['jpeg']) 
                 
        elif name == 'film_folder':
            value = os.path.join(self.root_folder,self._config['paths']['film']) 
                
        elif name == 'raw_folder':
            value = os.path.join(self.root_folder,self._config['paths']['raw']) 
                         
        else:
            print "key name unknown."
            value = None
        
        if value != None:
            print "[config] found value:",value
        else:
            print "[config] key not in config."
        
        self._cache[name] = value
        return value
        

