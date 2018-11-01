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
from requests import Session
from requests.auth import HTTPBasicAuth,HTTPDigestAuth

def _parse_string_value(str_value):
    try:
        return ast.literal_eval(str_value)
    except ValueError:
        return str_value
    except SyntaxError:
        return str_value
        
class WebHttp():
    head, data, session, glob = None, None, None, {}
    
    __resp = None
    __auth = None    
    __test = {"a":1,
               "b":[1,2,3,4],
               "c":{"d":5,"e":6},
               "f":{"g":[7,8,9]},
               "h":[{"i":10,"j":11},{"k":12}]
               }
    
    @classmethod
    def SetVar(cls, name, value):
        ''' set static value
        :param name: glob parameter name
        :param value: parameter value
        '''
        cls.glob.update({name:value})
            
    @classmethod
    def DyStrData(cls,name, regx, index = 0):
        ''' set dynamic value from the string data of response  
        @param name: glob parameter name
        @param regx: re._pattern_type
            e.g.
            DyStrData("a",re.compile('123'))
        '''
        text = cls.GetRespText()
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
        text = cls.GetRespText()        
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
        
                    
    @classmethod
    def GetVar(cls, name):
        return cls.glob.get(name)
    
    @classmethod
    def PopVar(cls, name):
        return cls.glob.pop(name, None)
    
    @classmethod
    def LoginAuth(cls,username,password,auth):
        '''
        :auth: [basic/digest] encrypt to base64 or md5
        '''
        
        if auth == "basic":
            cls.__auth = HTTPBasicAuth(username, password)
        elif auth == "digest":
            cls.__auth = HTTPDigestAuth(username, password)        
            
    @classmethod
    def GET(cls, url, **kwargs):     
        if isinstance(cls.session,Session):
            cls.__resp = cls.session.get(url, auth = cls.__auth, **kwargs)
        else:
            cls.__resp = cls.session.get(url, auth = cls.__auth, catch_response = True, **kwargs)
        cls.__auth = None
                
    @classmethod
    def POST(cls, url, data=None, json=None, **kwargs):
        '''
        :简化post
        :param data/json: [raw/json] request the data with Content-type[x-www-form-urlencoded] or Content-type[json]         
        '''
        headers = kwargs.pop("headers", None)
        if headers and not isinstance(headers, dict):
            try:
                headers = json.loads(headers)
            except:
                headers = None
        if isinstance(cls.session,Session):
            cls.__resp = cls.session.post(url, headers = headers, data = data, json = json, auth = cls.__auth, **kwargs)
        else:
            cls.__resp = cls.session.post(url, headers = headers, data = data, json = json, auth = cls.__auth, catch_response = True, **kwargs)            
        cls.__auth = None

    @classmethod
    def Download(cls, url, dst, stream = None, **kwargs):
        ''' save response body/content/text to a file
        :param url: download url
        :param stream: True/False or None, if False or None, response body will be immediately download; if True, will be hung up untill the all data in Response.content is read.
        :param dst: the full path or the full path file  
        '''
        if isinstance(cls.session,Session):
            cls.__resp = cls.session.get(url,stream = stream, auth = cls.__auth, **kwargs)
        else:
            cls.__resp = cls.session.get(url,stream = stream, auth = cls.__auth, catch_response = True, **kwargs)
        cls.__auth = None
        
        if os.path.isdir(dst):
            f_abspath = os.path.join(dst, os.path.basename(url))
        else:
            f_abspath = dst
        with open(f_abspath, 'wb') as fd:
            if stream: 
                for chunk in cls.__resp.iter_content():
                    fd.write(chunk)
            else:
                fd.write(cls.__resp.text.encode(cls.__resp.encoding))   
    
    @classmethod
    def Upload(cls,url, upload_files_params, data=None, **kwargs):
        ''' upload files to server
        @param url: upload url
        @param upload_files_params:  dict type, format is 'alias_name: file_path'
        @param data: dict type, formdata of upload files
        @param kwargs: others paramter of requests.post
        
        e.g.
            url = 'http://192.168.102.241:8008/dls/FileStorage/httpUploadFile'
            upload_files_params = {
                'pic1': r'C:\d_disk\auto\buffer\800x600.png',
                'pic2': "",
                'pic3': "",
                'pic4': "",
                'pic5': "",
                'pic6': "",
                'pic7': "",
                'pic8': ""
            }
            data = {'unzip': 0, 'dirType': 1}
            
            Upload(url, upload_files_params, data, verify=False)
        '''        
        multiple_files = {}
        for param_name, upload_file in upload_files_params.items():
            if not os.path.isfile(upload_file):
                multiple_files[param_name] = ("","")
                continue
            multiple_files[param_name] = (os.path.basename(upload_file), open(upload_file, 'rb'))
        
        if isinstance(cls.session,Session): 
            cls.__resp = cls.session.post(url, data = data, files = multiple_files, auth = cls.__auth, **kwargs)
        else:
            cls.__resp = cls.session.post(url, data = data, files = multiple_files, auth = cls.__auth, catch_response = True, **kwargs)
        cls.__auth = None 
    
    
    @classmethod
    def VerifyContain(cls, strs):
        if strs in cls.GetRespText():
            return True
        else:
            return False
    
    @classmethod
    def VerifyCode(cls, code):
        try:
            code = int(code)
        except:
            return False
        
        if cls.GetRespCode() == code:
            return True
        else:
            return False
    
    @classmethod
    def VerifyVar(cls, name, expect_value=None):
        value = cls.glob.get(name)
        
        if expect_value == None:
            return False if value == None else True
        else:
            return value == expect_value
    
    @classmethod
    def LocustSuccess(cls):
        ''' Report the response as successful, if session is locust'''
        if not isinstance(cls.session,Session):
            cls.__resp.success()
    
    @classmethod
    def LocustFailure(cls,exc):
        ''' Report the response as a failure, if session is locust'''
        if not isinstance(cls.session,Session):
            cls.__resp.failure(exc)
                            
    
    @classmethod
    def GetRespCode(cls):
        ''' HTTP-code'''
        return cls.__resp.status_code
    
    @classmethod
    def GetRespReason(cls):
        '''Textual reason of responded HTTP Status, e.g. "Not Found" or "OK". '''
        return cls.__resp.reason
    
    @classmethod
    def GetRespCookie(cls):
        ''' will print the cookie dict '''
        return dict(cls.__resp.cookies.items())

    @classmethod
    def GetRespHeaders(cls, name = None):
        ''' response headers '''
        if name:
            return cls.__resp.headers.get(name)
        return cls.__resp.headers
    
    @classmethod
    def GetRespEncoding(cls):
        ''' response encoding '''
        return cls.__resp.encoding
    
    @classmethod
    def GetRespText(cls):
        ''' Content of the response, in unicode '''
#         cls.__resp.encoding = requests.utils.get_encodings_from_content(cls.__resp.text)
#         cls.__resp.encoding = cls.__resp.apparent_encoding
        cls.__resp.encoding = None
        return cls.__resp.text
    
    @classmethod
    def GetRespContent(cls):
        ''' Content of the response, in bytes '''
        return cls.__resp.content
    
    @classmethod
    def GetRespElapsed(cls):
        ''' the time between sending request and the arrival of the response '''
        return cls.__resp.elapsed
    
    @classmethod
    def GetReqMethod(cls):
        ''' request method'''
        return cls.__resp.request.method
     
    @classmethod
    def GetReqUrl(cls):
        ''' request url'''
        return cls.__resp.request.url
    
    @classmethod
    def GetReqHeaders(cls, name = None):
        ''' request headers '''
        if name:
            return cls.__resp.request.headers.get(name)
        return cls.__resp.request.headers
    
    @classmethod
    def GetReqData(cls):
        ''' request body '''
        return cls.__resp.request.body