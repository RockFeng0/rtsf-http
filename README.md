# rtsf-http
基于rtsf测试框架，关键字驱动测试http/https等api


## 编写测试用例，模板基于rtsf

> 变量引用-> $var    关键字(函数)引用-> ${function}

```
# 示例如   test.yml：
- project:
    name: xxx系统
    module: 登陆模块-功能测试
    
- case:
    id: ATP-1
    desc: 打开百度
    glob_var:
        passwd: 123@Qwe
    glob_regx:
        rex_name: 'id=su value=([\w\-\.\+/=]+)'
    pre_command: 
        - ${SetVar(username, luokefeng)}
        - ${SetVar(password, $passwd)}
    steps:
        - request:
            url: https://www.baidu.com          
            method: GET
    post_command:
        - ${DyStrData(baidu_name,$rex_name)}
    verify:
        - ${VerifyCode(200)}
        - ${VerifyVar(baidu_name, 百度一下)}
        - ${VerifyVar(baidu_name, 123)}

```

## 基于rtsf，封装的关键字(内置函数)

```
DyJsonData(name,sequence)                   # -> resp.text or resp.content 返回json格式时，依据sequence，保存至变量name
DyStrData(name,regx,index=0)                # -> resp.text or resp.content 返回html/xml等格式时， 依据正则regx和下标index，保存至变量name                                           

GetReqData()                                # ->resp.request.body
GetReqHeaders()                             # ->resp.request.headers
GetReqMethod()                              # ->resp.request.method
GetReqUrl()                                 # ->resp.request.url

GetRespCode                                 # ->resp.status_code
GetRespContent                              # ->resp.content
GetRespText                                 # ->resp.text 
GetRespCookie                               # ->resp.cookies   返回字典
GetRespElapsed                              # ->resp.elapsed
GetRespEncoding                             # ->resp.encoding
GetRespHeaders                              # ->resp.headers
GetRespReason                               # ->resp.reason

SetVar(name, value)
GetVar(name)
Upload(url, upload_files, **formdata)       # -> e.g.  Upload('http://127.0.0.1/filestorage/httpUploadFile',
                                                            [r'd:\auto\buffer\t.jpg',r'd:\auto\buffer\t.zip'],
                                                            dirType = 1, unzip = 0)
Download(url, dst, stream = None)           # -> e.g.  Download('http://127.0.0.1/filestorage/httpUploadFile/t.zip',
                                                            r'c:\download') 

VerifyCode(code)                            #  验证响应码为code
VerifyContain(strs)                         #  验证相应的body中，包含字符串
VerifyVar(name, expect_value=None)          #  验证变量的值是否为期望值；如果期望值为None，则仅验证变量是否被赋值
```

## 自定义，关键字(函数、变量)
> 在case同级目录中，创建  preference.py, 该文件所定义的 变量、函数，可以被动态加载和引用

```
# preference.py 示例

test_var = "hello rtsf."
def test_func():
    return "nihao rtsf."
 
```

执行用例的时候，可以使用 变量引用 或者关键字引用的方法，调用，自定义的函数和变量

## 执行测试用例

执行命令：

```
#示例，执行 test.yml测试用例
hdriver test.yml
#或者
httpdriver test.yml

```
## 测试报告及日志

> 执行结束后，测试用例所在路径，就是report生成的路径





