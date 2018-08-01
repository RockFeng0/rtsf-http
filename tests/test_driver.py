#! python3
# -*- encoding: utf-8 -*-
'''
Current module: tests.test_driver

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      tests.test_driver,  v1.0 2018年7月24日
    FROM:   2018年7月24日
********************************************************************
======================================================================

Provide a function for the automation test

'''



import unittest,os
from rtsf.p_executer import TestRunner,Runner,TaskSuite
from rtsf.p_report import HtmlReporter
from rtsf.p_testcase import TestCaseParser
from rtsf.p_applog import logger
from httpdriver.driver import Driver 

# 分层用例       
case_file1 = r'data\test_case.yaml'

# 用例模型
case_file2 = r'data\case_model.yaml'

class TestTestRunner(unittest.TestCase):
    
    def test_run_and_gen_hetml_report(self):
#         logger.setup_logger("debug")
        
        runner = TestRunner(runner = Driver).run(case_file2)        
        html_report = runner.gen_html_report()
        
        
        self.assertEqual(isinstance(runner.text_test_result, unittest.TextTestResult), True)        
        self.assertEqual(isinstance(runner._task_suite, TaskSuite), True)
        
        suite = runner._task_suite.tasks[0]
        self.assertEqual(isinstance(suite.test_runner, Runner), True)
        self.assertEqual(isinstance(suite.test_runner.tracer, HtmlReporter), True)
        self.assertEqual(isinstance(suite.test_runner.parser, TestCaseParser), True)
        
        self.assertEqual(os.path.isfile(html_report[0]), True)
        
        
        
        
if __name__ == "__main__":
#     unittest.main()
#     logger.setup_logger("debug")
    runner = TestRunner(runner = Driver).run(case_file1)
    html_report = runner.gen_html_report()
    
    