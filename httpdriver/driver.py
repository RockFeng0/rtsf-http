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

from rtsf.p_executer import Runner
from rtsf.p_common import CommonUtils,ModuleUtils
from rtsf.p_exception import FunctionNotFound,VariableNotFound

class Driver(Runner):      
    
    def __init__(self):
        self._Actions = ModuleUtils.get_imported_module("httpdriver.actions")
    
    def run_test(self, testcase_dict):
        parser = self.parser
        parser.bind_functions(ModuleUtils.get_callable_class_method_names(self._Actions.WebHttp))
        parser.update_binded_variables(self._Actions.WebHttp.glob)        
         
        case_name = testcase_dict["name"]                 
        self.tracer.start(self.proj_info["module"], case_name, testcase_dict.get("responsible","Administrator"), testcase_dict.get("tester","Administrator"))        
        self.tracer.section(case_name)
         
        try:
            self.tracer.normal("**** bind glob variables")                
            glob_vars = parser.eval_content_with_bind_actions(testcase_dict.get("glob_var",{}))
            self.tracer.step("set global variables: {}".format(glob_vars))                
            self._Actions.WebHttp.glob.update(glob_vars)            
             
            self.tracer.normal("**** bind glob regular expression")
            globregx = {k: re.compile(v) for k,v in testcase_dict.get("glob_regx",{}).items()}
            self.tracer.step("set global regular: {}".format(globregx))            
            self._Actions.WebHttp.glob.update(globregx)
                             
            self.tracer.normal("**** precommand")
            precommand = testcase_dict.get("pre_command",[])    
            parser.eval_content_with_bind_actions(precommand)
            for i in precommand:
                self.tracer.step("{}".format(i))
             
            self.tracer.normal("**** steps")
            steps = testcase_dict["steps"]
            for step in steps:
                if not "request" in step:
                    continue
                 
                url = parser.eval_content_with_bind_actions(step["request"]["url"])           
                if not url:
                    raise VariableNotFound("Not found url('%s')" %url)
             
                method = parser.eval_content_with_bind_actions(step["request"]["method"])
                req = parser.get_bind_function(method.upper())
                if not req:
                    raise FunctionNotFound("Not found method('%s')" %method)
                self.tracer.step("requests url -> \n\t{} {}".format(method.upper(), url))
                                    
                head = parser.eval_content_with_bind_actions(step["request"].get("headers"))
                head = head if head else {}
                self.tracer.step("requests head -> \n\t{}".format(json.dumps(head,indent=4, separators=(',', ': '))))
                set_head = parser.get_bind_function("SetReqHead")
                 
                data = parser.eval_content_with_bind_actions(step["request"].get("data"))
                data = data if data else {}
                self.tracer.step("requests body -> \n\t{}".format(json.dumps(data,indent=4, separators=(',', ': '))))
                set_data =parser.get_bind_function("SetReqData")
             
                set_head(**head)
                set_data(**data)                
                req(url)
             
                resp_headers = parser.get_bind_function("GetRespHeaders")()
                self.tracer.step("response headers: \n\t{}".format(resp_headers))
             
                resp_text = parser.get_bind_function("GetRespText")()
                self.tracer.step(u"response body: \n\t{}".format(resp_text))                                 
            
            self.tracer.normal("**** postcommand")
            postcommand = testcase_dict.get("post_command", [])        
            parser.eval_content_with_bind_actions(postcommand)
            for i in postcommand:
                self.tracer.step("{}".format(i))
            
            self.tracer.normal("**** verify")
            verify = testcase_dict.get("verify",[])
            result = parser.eval_content_with_bind_actions(verify)
            for v, r in zip(verify,result):
                if r == False:
                    self.tracer.fail(u"{} --> {}".format(v,r))
                else:
                    self.tracer.ok(u"{} --> {}".format(v,r))
                        
        except KeyError as e:
            self.tracer.error("Can't find key[%s] in your testcase." %e)
        except FunctionNotFound as e:
            self.tracer.error(e)
        except VariableNotFound as e:
            self.tracer.error(e)
        except Exception as e:
            self.tracer.error("%s\t%s" %(e,CommonUtils.get_exception_error()))
        finally:
#             self.tracer.normal("globals:\n\t{}".format(parser._variables)) 
            self.tracer.stop()
            