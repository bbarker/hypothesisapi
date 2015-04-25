# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__ = 'Raymond Yee'
__email__ = 'raymond.yee@gmail.com'
__version__ = '0.2.0'

import requests
import json

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode



APP_URL = "https://hypothes.is/app"
API_URL = "https://hypothes.is/api"

# We can probably learn a lot from https://h.readthedocs.org/en/latest/api.html

def remove_none(d):
    return dict([(k,v) for (k, v) in d.items() if v is not None])

class API(object):
    """
    currently a wrapper for the nascent web API for 
    """
    
    def __init__(self, username, password, api_url=API_URL, app_url=APP_URL):
        """
        I think at this point, a hypothes.is username/password required for API to work
        """
        self.api_url = api_url
        self.app_url = app_url
        self.username = username
        self.password = password
        self.csrf_token = None
        self.token = None
        
    def login(self):
        
        # pick up some cookies to start the session
        
        r = requests.get(self.app_url)
        cookies = r.cookies

        # make call to https://hypothes.is/app?__formid__=login
        
        payload = {"username":self.username,"password":self.password}
        self.csrf_token = cookies['XSRF-TOKEN']
        data = json.dumps(payload)
        headers = {'content-type':'application/json;charset=UTF-8', 'x-csrf-token': self.csrf_token}
        
        r = requests.post(url=self.app_url  + "?__formid__=login", data=data, cookies=cookies, headers=headers)
        
        # get token

        url = self.api_url + "/token?" + urlencode({'assertion':self.csrf_token})
        r = (requests.get(url=url,
                         cookies=cookies, headers=headers))
        
 
        self.token =  r.content
        
        
    def get_annotation(self, _id):
        """
        https://hypothes.is/api/annotations/:id
        """
        url = self.api_url + "/annotations/" + _id
        headers = {"X-Annotator-Auth-Token": self.token, "x-csrf-token":self.csrf_token}
        r = requests.get(url, headers = headers)
        
        if r.status_code == 200:
            return r.json()
        else:
            return None      
            
    
    def search_id (self, _id):
        
        url = self.api_url + "/search?_id=" + _id
        
        headers = {"X-Annotator-Auth-Token": self.token, "x-csrf-token":self.csrf_token}
        r = requests.get(url, headers = headers)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    
        
    def search  (self, user=None, sort=None, order="asc", offset=0, limit=10, uri=None, **kw):
        
        headers = {"X-Annotator-Auth-Token": self.token, "x-csrf-token":self.csrf_token}
        user_acct = "acct:{user}@hypothes.is".format(user=user) if user is not None else None

        search_dict = ({'user':user_acct,
         'sort':sort,
         'order':order,
         'offset':offset,
         'uri':uri,
         'limit':limit})
    
        search_dict.update(kw)
        search_dict = remove_none(search_dict)
        
        more_results = True
    
        while more_results:
    
            url = self.api_url + "/search?{query}".format(query=urlencode(search_dict))
            
            r = requests.get(url, headers=headers)
            rows = r.json().get("rows")
            
            if len(rows):
                for row in rows:
                    yield row
                search_dict['offset'] += limit
            else:
                more_results = False

    
    
        
        