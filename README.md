# rtsf-http
基于rtsf测试框架，关键字驱动测试http/https等api


## 环境准备

### 安装rtsf-http
pip install rtsf-http
 

## 编写测试用例，模板基于rtsf

> 变量引用-> $var    关键字(函数)引用-> ${function}

- 常量的定义， glob_var 和  glob_regx
- 模板常用的关键字，参见 [rtsf](https://github.com/RockFeng0/rtsf)介绍

### 基本用例

基本用例，是指没有分层的情况下，简单的测试用例

```
# 示例如   test.yml：
- project:
    # 模板遵循rtsf约定
    name: xxx系统
    module: 登陆模块-功能测试
    
- case:
    id: ATP-1
    desc: 打开百度
    
    name: demo_baidu1
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

### 分层用例

- 分层用例，是指模块功能测试的时候，对测试用例进行分层，最小的单元为api，其次为suite，最后组成用例
- 其存放路径、编写规则等，详见 [rtsf](https://github.com/RockFeng0/rtsf)相关介绍

示例场景1： 
     打开百度，搜索hello，打开bing
示例场景2： 
     打开bing, 打开百度，搜索hello，

应用分层： 
1. 打开百度 封装为 api_1, 搜索hello 封装为api_2, 打开bing封装为api_3;   

```
# api_test.yaml

- api:
    def: api_1()
    steps:
        - request:
            url: https://www.baidu.com          
            method: GET    
    verify:
        - ${VerifyCode(200)}

- api:
    def: api_2($keyword)
    steps:
        - request:
            url: https://www.baidu.com/s?wd=$keyword    
            method: GET    
    verify:
        - ${VerifyCode(200)}
        
- api:
    def: api_3()
    steps:
        - request:
            url: https://cn.bing.com   
            method: GET    
    verify:
        - ${VerifyCode(200)}
```

2. suite1排列api_1、api_2、api_3;  

```
# suite_test1.yaml
- project:
    def: suite1($keyword)
    
- case:
    name: suite1_demo_baidu
    api: api_1()

- case:
    name: suite1_demo_baidu_key
    api: api_2($keyword)

- case:
    name: suite1_demo_bing
    api: api_3()
       
```

3. suite2排列 api_3、api_1、api_2

```
# suite_test2.yaml
- project:
    def: suite2($keyword,$password,$username)

- case:
    name: suite2_demo_bing
    api: api_3()
    
- case:
    name: suite2_demo_baidu
    api: api_1()

- case:
    name: suite2_demo_baidu_key
    api: api_2($keyword)
       
```


3. 最后测试用例排列 suite1 & suite2  

```
# 测试用例 test_case.yaml：
- project:
    name: 分层用例
    module: 示例场景
    
- case:
    name: 示例场景-case1
    suite: suite1(hello)
        
- case:
    name: 示例场景-case2
    suite: suite2(hello,123456,luokefeng)

```

4. 执行
    hdriver.exe test_case.yaml

## 执行测试用例

> 执行有两个命令,  hdriver 或者   httpdriver

```
usage: hdriver [-h] [--log-level LOG_LEVEL] [--log-file LOG_FILE] case_file
usage: httpdriver [-h] [--log-level LOG_LEVEL] [--log-file LOG_FILE] case_file
```

![hdriver-command.png](https://raw.githubusercontent.com/RockFeng0/img-folder/master/rtsf-http-img/hdriver-command.png)

## 测试报告及日志

> 执行结束后，测试用例所在路径，就是report生成的路径


## 基于rtsf，封装的关键字(内置函数)

```
DyJsonData(name,sequence)                   # -> resp.text or resp.content 返回json格式时，依据sequence，保存至变量name
DyStrData(name,regx,index=0)                # -> resp.text or resp.content 返回html/xml等格式时， 依据正则regx和下标index，保存至变量name                                           

GetReqData()                                # ->resp.request.body
GetReqHeaders(name                          # ->resp.request.headers;默认name=None,返回所有的headers; 如果指定了name，那么返回headers中指定name的值；
GetReqMethod()                              # ->resp.request.method
GetReqUrl()                                 # ->resp.request.url

GetRespCode                                 # ->resp.status_code
GetRespContent                              # ->resp.content
GetRespText                                 # ->resp.text 
GetRespCookie                               # ->resp.cookies   返回字典
GetRespElapsed                              # ->resp.elapsed
GetRespEncoding                             # ->resp.encoding
GetRespHeaders(name)                        # ->resp.headers; 默认name=None,返回所有的headers; 如果指定了name，那么返回headers中指定name的值；
GetRespReason                               # ->resp.reason

SetVar(name, value)                         # -> 设置变量
GetVar(name)                                # -> 从变量空间中，获取变量的值
PopVar(name)                                # -> 从变量空间中，获取变量的值，然后删除该变量
Upload(url,upload_files_params,**formdata)  # -> e.g.  Upload('http://127.0.0.1/filestorage/httpUploadFile',
                                                            {'pic1': r'C:\d_disk\auto\buffer\800x600.png','pic2': "",'pic3': ""},
                                                            dirType = 1, unzip = 0) 
            
Download(url, dst, stream = None)           # -> e.g.  Download('http://127.0.0.1/filestorage/httpUploadFile/t.zip',
                                                            r'c:\download') 

VerifyCode(code)                            #  验证响应码为code
VerifyContain(strs)                         #  验证相应的body中，包含字符串
VerifyVar(name, expect_value=None)          #  验证变量的值是否为期望值；如果期望值为None，则仅验证变量是否被赋值
```

## 自定义，关键字(函数、变量)
> 在case同级目录中，创建  preference.py, 该文件所定义的 变量、函数，可以被动态加载和引用

执行用例的时候，可以使用 变量引用 或者关键字引用的方法，调用，自定义的函数和变量

```
# preference.py 示例

test_var = "hello rtsf."
def test_func():
    return "nihao rtsf."
 
```








