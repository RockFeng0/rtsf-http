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
from markupsafe import Markup
from rtsf.p_executer import Runner
from rtsf.p_common import CommonUtils,ModuleUtils
from rtsf.p_exception import FunctionNotFound,VariableNotFound

class _Driver(Runner):      
    
    def __init__(self, has_trace):
        super(_Driver,self).__init__()
        self.__has_trace = has_trace
        
    def run_test(self, testcase_dict, variables, driver_map):
        fn, fn_driver = driver_map
        parser = self.parser
        tracer = self.tracers[fn]
        if not self.__has_trace:
            tracer._switch_off()
        
        _Actions = ModuleUtils.get_imported_module("httpdriver.actions")
        _Actions.Request.session = fn_driver
        parser.bind_functions(ModuleUtils.get_callable_class_method_names(_Actions.Request))
        
        _Actions.Request.glob.update(variables)
        parser.update_binded_variables(_Actions.Request.glob)
        
        case_name = parser.eval_content_with_bind_actions(testcase_dict["name"])
        tracer.start(self.proj_info["module"], case_name, testcase_dict.get("responsible","Administrator"), testcase_dict.get("tester","Administrator"))        
        tracer.section(case_name)
         
        try:
            tracer.normal("**** bind glob variables")                
            glob_vars = parser.eval_content_with_bind_actions(testcase_dict.get("glob_var",{}))
            tracer.step("set global variables: {}".format(glob_vars))                
            _Actions.Request.glob.update(glob_vars)            
             
            tracer.normal("**** bind glob regular expression")
            globregx = {k: re.compile(v) for k,v in testcase_dict.get("glob_regx",{}).items()}
            tracer.step("set global regular: {}".format(globregx))            
            _Actions.Request.glob.update(globregx)
                             
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
                parsered_requests = parser.eval_content_with_bind_actions(raw_requests)
                
                url     = parsered_requests.pop("url")                                                             
                method  = parsered_requests.pop("method")
                if not method.capitalize() in ("Get", "Post"):
                    raise FunctionNotFound("Not found method('%s')" %method)
                
                tracer.step("requests url: \n\t{} {}".format(method.capitalize(), url))
                req = parser.get_bind_function(method.capitalize())
                
                for k,v in parsered_requests.items():
                    tracer.step("requests {} -> \n\t{}".format(k, json.dumps(v, indent=4, separators=(',', ': '))))
                
                #resp = req(url, **parsered_requests)
                req_track_obj = self._request(req, url, **parsered_requests)
                resp_info     = req_track_obj.trackinfo
                         
                tracer.step("response headers: \n\t{}".format(json.dumps(dict(resp_info["response_headers"]), indent=4, separators=(',', ': '))))             
                tracer.step(u"response body: \n\t{}".format(Markup(resp_info["response_body"]).unescape()))
            
            tracer.normal("**** postcommand")
            postcommand = testcase_dict.get("post_command", [])        
            parser.eval_content_with_bind_actions(postcommand)
            for i in postcommand:
                tracer.step("{}".format(i))
            
            tracer.normal("**** verify")
            verify = testcase_dict.get("verify",[])
            result = parser.eval_content_with_bind_actions(verify)
            
            self._verify(zip(verify,result), tracer, req_track_obj.response)
                        
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
    
    def _request(self, func, url, **kwargs):
        ''' Override'''
        pass
    
    def _verify(self, result, trace_obj, resp_obj):
        ''' Override'''
        pass

class HttpDriver(_Driver):    
    def __init__(self):
        super(HttpDriver,self).__init__(has_trace = True)
        self._default_drivers = [("", Session())]        
    
    def _request(self, func, url, **kwargs):
        return func(url, **kwargs)
    
    def _verify(self, result, trace_obj, resp_obj):
        _ = resp_obj
        for v, r in result:
            msg = u"{} --> {}".format(v,r)
            func = trace_obj.ok if r == True else trace_obj.fail
            func(msg)
                
class LocustDriver(_Driver):
    def __init__(self, locust_client):
        super(LocustDriver,self).__init__(has_trace = False)
        self._default_drivers = [("", locust_client)]
    
    def _request(self, func, url, **kwargs):
        kwargs["catch_response"] = True
        return func(url, **kwargs)
    
    def _verify(self, result, trace_obj, resp_obj):
        _ = trace_obj
        for v, r in result:
            if r == False:
                resp_obj.failure(u"{} --> {}".format(v,r))
                return
        resp_obj.success()
        