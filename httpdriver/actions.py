#! python3
# -*- encoding: utf-8 -*-
'''
Current module: httpdriver.actions

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      httpdriver.actions,  v1.0 2018年7月24日
    FROM:   2018年7月24日
********************************************************************
======================================================================

Provide a function for the automation test

'''


import os,re,json,ast
from base64 import b64encode
from jinja2 import escape
from markupsafe import Markup
from collections import Iterable
from rtsf.p_compat import basestring, bytes, numeric_types
from requests.structures import CaseInsensitiveDict
from requests.auth import HTTPBasicAuth,HTTPDigestAuth

def _parse_string_value(str_value):
    try:
        return ast.literal_eval(str_value)
    except ValueError:
        return str_value
    except SyntaxError:
        return str_value
        
class RequestTrackInfo(object):
    
    def __init__(self,resp_object):
        self.__response = resp_object
        self.__track_info = {
            "status_code": resp_object.status_code,
            "reason": resp_object.reason,            
            "elapsed": resp_object.elapsed, #the time between sending request and the arrival of the response
            
            "request_url": resp_object.request.url,
            "request_method": resp_object.request.method,
            "request_headers": resp_object.request.headers,
            "request_body": resp_object.request.body,
            
            "response_headers": resp_object.headers,
            "response_cookies": dict(resp_object.cookies.items()),
            "response_encoding": resp_object.encoding,
            }
        
        try:
            self.__track_info["response_body"] = resp_object.json()
        except ValueError:
            self.__track_info["response_body"] = resp_object.content        
    
    @property
    def response(self):
        return self.__response
    
    @property
    def trackinfo(self):
        self.__stringify_body('request')
        self.__stringify_body('response')
        return self.__track_info
        
    def __stringify_body(self, request_or_response):
        ''' this method reference from httprunner '''
        headers = self.__track_info['{}_headers'.format(request_or_response)]
        body = self.__track_info.get('{}_body'.format(request_or_response))
    
        if isinstance(body, CaseInsensitiveDict):
            body = json.dumps(dict(body), ensure_ascii=False)
    
        elif isinstance(body, (dict, list)):
            body = json.dumps(body, indent=2, ensure_ascii=False)
    
        elif isinstance(body, bytes):
            resp_content_type = headers.get("Content-Type", "")
            try:
                if "image" in resp_content_type:
                    self.__track_info["response_data_type"] = "image"
                    body = "data:{};base64,{}".format(
                        resp_content_type,
                        b64encode(body).decode('utf-8')
                    )
                else:
                    body = escape(body.decode("utf-8"))
            except UnicodeDecodeError:
                pass
    
        elif not isinstance(body, (basestring, numeric_types, Iterable)):
            # class instance, e.g. MultipartEncoder()
            body = repr(body)
    
        self.__track_info['{}_body'.format(request_or_response)] = body

class Request(object):
    session = None
    glob = {}
    __trackinfo = {}
    
    __test = {"a":1,
               "b":[1,2,3,4],
               "c":{"d":5,"e":6},
               "f":{"g":[7,8,9]},
               "h":[{"i":10,"j":11},{"k":12}]
               }
    
    #### glob_var
    @staticmethod
    def GetBasicAuth(username,password):
        ''' auth: basic encrypt to base64 '''
        return HTTPBasicAuth(username, password)
    
    @staticmethod
    def GetDigestAuth(username,password):
        ''' auth: digest encrypt to md5 '''
        return HTTPDigestAuth(username, password)
    
    @classmethod
    def GetVar(cls, name):
        return cls.glob.get(name)
    
    @classmethod
    def PopVar(cls, name):
        return cls.glob.pop(name, None)
    
    #### precommand
    @classmethod
    def SetVar(cls, name, value):
        ''' set static value
        :param name: glob parameter name
        :param value: parameter value
        '''
        cls.glob.update({name:value})
    
    #### steps            
    @classmethod
    def Get(cls, url, **kwargs):
        '''
        @param download_dir:  director or filepath, define a download request
        @param stream: True if large file, default is None 
        @param catch_response: locust parameter, raise a error if not a locust session. True/False, True if you want to define a locust request is success or fail
        '''
        if "download_dir" in kwargs:
            # download files
            dst = kwargs.pop("download_dir")
            stream = kwargs.get("stream")
            resp = Request.session.get(url, **kwargs)
            
            f_abspath = os.path.join(dst, os.path.basename(url) + ".html") if os.path.isdir(dst) else dst
            with open(f_abspath, 'wb') as fd:
                if stream: 
                    for chunk in resp.iter_content():
                        fd.write(chunk)
                else:
                    fd.write(resp.content)
                    #fd.write(resp.text.encode(cls.__resp.encoding))
            req_track_obj = RequestTrackInfo(resp)
            cls.__trackinfo = req_track_obj.trackinfo
        else:
            req_track_obj = RequestTrackInfo(Request.session.get(url, **kwargs))
            cls.__trackinfo = req_track_obj.trackinfo
            
        return req_track_obj
             
    
    @classmethod
    def Post(cls, url, data=None, json=None, **kwargs):
        '''        
        @param data/json: [raw/json] request the data with Content-type[x-www-form-urlencoded] or Content-type[json]         
        @param files:  dict type, define a upload request
        @param catch_response: locust parameter, raise a error if not a locust session. True/False, True if you want to define a locust request is success or fail
        e.g. 
            files = {
                'pic1': r'D:\auto\buffer\003.png',
                'pic2': "",
                'pic3': "",
                'pic4': "",
                'pic5': "",
                'pic6': "",
                'pic7': "",
                'pic8': ""
            }
            
        @note:  requests upload files
        e.g. upload files
            url = 'http://192.168.102.241:8008/dls/FileStorage/httpUploadFile'
            multiple_files = {'pic8': ('', ''), 
                              'pic2': ('', ''), 
                              'pic1': ('003.png', open(r'D:\auto\buffer\003.png', rb)), 
                              'pic6': ('', ''), 'pic4': ('', ''), 
                              'pic7': ('', ''), 
                              'pic3': ('', ''), 
                              'pic5': ('', '')
                              }
            data = {'unzip': 0, 'dirType': 1}
            requests.post(url, data = data, files = multiple_files)
        '''
        files = kwargs.pop("files",{})
        
        if files and isinstance(files, dict):
            # upload files
            multiple_files = {}
            for param_name, upload_file in files.items():
                
                if not upload_file or not os.path.isfile(upload_file):
                    multiple_files[param_name] = ("","")
                    continue
                multiple_files[param_name] = (os.path.basename(upload_file), open(upload_file, 'rb'))            
            kwargs["files"] = multiple_files
        
        req_track_obj = RequestTrackInfo(Request.session.post(url, data = data, json = json, **kwargs))
        cls.__trackinfo = req_track_obj.trackinfo
        return req_track_obj
    
    #### postcommand
            
    @classmethod
    def DyStrData(cls,name, regx, index = 0):
        ''' set dynamic value from the string data of response  
        @param name: glob parameter name
        @param regx: re._pattern_type
            e.g.
            DyStrData("a",re.compile('123'))
        '''
        text = Markup(cls.__trackinfo["response_body"]).unescape()
        
        if not text:
            return
        if not isinstance(regx, re._pattern_type):
            raise Exception("DyStrData need the arg which have compiled the regular expression.")
            
        values = regx.findall(text)
        result = ""
        if len(values)>index:
            result = values[index]        
        cls.glob.update({name:result})
    
    @classmethod
    def DyJsonData(cls,name, sequence):
        ''' set dynamic value from the json data of response  
        @param name: glob parameter name
        @param sequence: sequence for the json
            e.g.
            result={"a":1,
               "b":[1,2,3,4],
               "c":{"d":5,"e":6},
               "f":{"g":[7,8,9]},
               "h":[{"i":10,"j":11},{"k":12}]
               }
            
            sequence1 ="a" # -> 1
            sequence2 ="b.3" # -> 4
            sequence3 = "f.g.2" # -> 9
            sequence4 = "h.0.j" # -> 11
        '''
        text = Markup(cls.__trackinfo["response_body"]).unescape()
        if not text:
            return
                
        resp = json.loads(text)
#         resp = cls.__test.copy()                      
        sequence = [_parse_string_value(i) for i in sequence.split('.')]    
        for i in sequence:
            try:
                if isinstance(i, int):
                    resp = resp[i]   
                else:
                    resp = resp.get(i)
            except:            
                cls.glob.update({name:None})
                return        
        cls.glob.update({name:resp})    
    
    #### verify                
    
    @classmethod
    def VerifyContain(cls, strs):
        text = Markup(cls.__trackinfo["response_body"]).unescape()
        if strs in text:
            return True
        else:
            return False
    
    @classmethod
    def VerifyCode(cls, code):        
        if cls.__trackinfo["status_code"] == code:
            return True
        else:
            return False
    
    @classmethod
    def VerifyVar(cls, name, expect_value=None):
        value = cls.glob.get(name)
#         print(type(value),value)
#         print(type(expect_value),expect_value)
        if expect_value == None:
            return False if value == None else True
        elif type(value) == type(expect_value):            
            return value == expect_value
        else:
            return str(value) == str(expect_value)
        
    