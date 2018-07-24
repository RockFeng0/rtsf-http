#encoding:utf-8
''' 内置的函数

DyJsonData(name,sequence)       # -> resp.text or resp.content 返回json格式时，依据sequence，保存至变量name
DyStrData(name,regx,index=0)    # -> resp.text or resp.content 返回html/xml等格式时，
                                            依据正则regx和下标index，保存至变量name

GetReqData()    # ->resp.request.body
GetReqHeaders() # ->resp.request.headers
GetReqMethod()  # ->resp.request.method
GetReqUrl()     # ->resp.request.url

GetRespCode         # ->resp.status_code
GetRespContent      # ->resp.content
GetRespText         # ->resp.text 
GetRespCookie       # ->resp.cookies   返回字典
GetRespElapsed      # ->resp.elapsed
GetRespEncoding     # ->resp.encoding
GetRespHeaders      # ->resp.headers
GetRespReason       # ->resp.reason

SetVar(name, value)
GetVar(name)
Upload(url, upload_files, **formdata)   # -> e.g.  Upload('http://127.0.0.1/filestorage/httpUploadFile',
                                                            [r'd:\auto\buffer\t.jpg',r'd:\auto\buffer\t.zip'],
                                                            dirType = 1, unzip = 0)
Download(url, dst, stream = None)       # -> e.g.  Download('http://127.0.0.1/filestorage/httpUploadFile/t.zip',
                                                            r'c:\download') 

VerifyCode(code)
VerifyContain(strs)     #  wether strs in resp.text

'''

####  For unittest of p_testcase
test_var = "hello world"
def test_func():
    return "nihao"