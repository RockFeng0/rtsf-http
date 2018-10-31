#! python3
# -*- encoding: utf-8 -*-
'''
Current module: httpdriver.driver

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      httpdriver.driver,  v1.0 2018年7月24日
    FROM:   2018年7月24日
********************************************************************
======================================================================

Provide a function for the automation test

'''


import re,json
from requests import Session
from rtsf.p_executer import Runner
from rtsf.p_common import CommonUtils,ModuleUtils,FileSystemUtils
from rtsf.p_exception import FunctionNotFound,VariableNotFound

class _Driver(Runner):      
    
    def __init__(self):
        super(_Driver,self).__init__()
        
    def run_test(self, testcase_dict, variables, driver_map):
        fn, fn_driver = driver_map
        parser = self.parser
        tracer = self.tracers[fn]
        
        _Actions = ModuleUtils.get_imported_module("httpdriver.actions")
        _Actions.WebHttp.session = fn_driver
        parser.bind_functions(ModuleUtils.get_callable_class_method_names(_Actions.WebHttp))
        
        _Actions.WebHttp.glob.update(variables)
        parser.update_binded_variables(_Actions.WebHttp.glob)
         
        case_name = FileSystemUtils.get_legal_filename(parser.eval_content_with_bind_actions(testcase_dict["name"]))
        tracer.start(self.proj_info["module"], case_name, testcase_dict.get("responsible","Administrator"), testcase_dict.get("tester","Administrator"))        
        tracer.section(case_name)
         
        try:
            tracer.normal("**** bind glob variables")                
            glob_vars = parser.eval_content_with_bind_actions(testcase_dict.get("glob_var",{}))
            tracer.step("set global variables: {}".format(glob_vars))                
            _Actions.WebHttp.glob.update(glob_vars)            
             
            tracer.normal("**** bind glob regular expression")
            globregx = {k: re.compile(v) for k,v in testcase_dict.get("glob_regx",{}).items()}
            tracer.step("set global regular: {}".format(globregx))            
            _Actions.WebHttp.glob.update(globregx)
                             
            tracer.normal("**** precommand")
            precommand = testcase_dict.get("pre_command",[])    
            parser.eval_content_with_bind_actions(precommand)
            for i in precommand:
                tracer.step("{}".format(i))
             
            tracer.normal("**** steps")
            steps = testcase_dict["steps"]
            for step in steps:
                if not "request" in step:
                    continue
                
                raw_requests = step["request"].copy()
                url     = parser.eval_content_with_bind_actions(raw_requests.pop("url"))                                                                
                method  = parser.eval_content_with_bind_actions(raw_requests.pop("method"))
                if not method.upper() in ("GET", "POST"):
                    raise FunctionNotFound("Not found method('%s')" %method)
                
                tracer.step("requests url: \n\t{} {}".format(method.upper(), url))
                req = parser.get_bind_function(method.upper())
                
                kwargs = {}
                for k,v in raw_requests.items():
                    kwargs[k] = parser.eval_content_with_bind_actions(v)
                    tracer.step("requests {} -> \n\t{}".format(k, json.dumps(kwargs[k], indent=4, separators=(',', ': '))))
                
                req(url, **kwargs)
             
                resp_headers = parser.get_bind_function("GetRespHeaders")()
                tracer.step("response headers: \n\t{}".format(json.dumps(dict(resp_headers), indent=4, separators=(',', ': '))))
             
                resp_text = parser.get_bind_function("GetRespText")()
                tracer.step(u"response body: \n\t{}".format(resp_text))
            
            tracer.normal("**** postcommand")
            postcommand = testcase_dict.get("post_command", [])        
            parser.eval_content_with_bind_actions(postcommand)
            for i in postcommand:
                tracer.step("{}".format(i))
            
            tracer.normal("**** verify")
            verify = testcase_dict.get("verify",[])
            result = parser.eval_content_with_bind_actions(verify)
            for v, r in zip(verify,result):
                if r == False:
                    tracer.fail(u"{} --> {}".format(v,r))
                else:
                    tracer.ok(u"{} --> {}".format(v,r))
                        
        except KeyError as e:
            tracer.error("Can't find key[%s] in your testcase." %e)
        except FunctionNotFound as e:
            tracer.error(e)
        except VariableNotFound as e:
            tracer.error(e)
        except Exception as e:
            tracer.error("%s\t%s" %(e,CommonUtils.get_exception_error()))
        finally:
#             tracer.normal("globals:\n\t{}".format(parser._variables)) 
            tracer.stop()

class HttpDriver(_Driver):    
    def __init__(self):
        super(HttpDriver,self).__init__()
        self._default_drivers = [("", Session())]        
        
class LocustDriver(_Driver):
    def __init__(self, locust_client):
        super(LocustDriver,self).__init__()
        self._default_drivers = [("", locust_client)]
        
