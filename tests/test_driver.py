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
from httpdriver.driver import HttpDriver 

class TestTestRunner(unittest.TestCase):
    
    def setUp(self):
        # 分层用例       
        self.suite_api_case = r'data\suite_api_case.yaml'        
        # 用例模型
        self.case_model = r'data\case_model.yaml'
        # 数据驱动-用例
        self.data_driver_case = r'data\data_driver.yaml'
    
    def test_Driver_case_model(self):
        #logger.setup_logger("debug")
        
        runner = TestRunner(runner = HttpDriver).run(self.case_model)        
        html_report = runner.gen_html_report()
        #print(html_report)
        
        self.assertEqual(isinstance(runner.text_test_result, unittest.TextTestResult), True)        
        self.assertEqual(isinstance(runner._task_suite, TaskSuite), True)
        
        suite = runner._task_suite.tasks[0]
        self.assertEqual(isinstance(suite.test_runner, Runner), True)
        self.assertEqual(isinstance(suite.test_runner.tracers, dict), True)
        self.assertIsInstance(suite.test_runner.tracers[""], HtmlReporter)
        self.assertEqual(isinstance(suite.test_runner.parser, TestCaseParser), True)
        
        self.assertEqual(os.path.isfile(html_report[0]), True)
    
    def test_Driver_data_driver_case(self):
        #logger.setup_logger("debug")
        
        runner = TestRunner(runner = HttpDriver).run(self.data_driver_case)        
        html_report = runner.gen_html_report()
        self.assertEqual(os.path.isfile(html_report[0]), True)
        
        result = runner.text_test_result
        self.assertEqual(result.testsRun, 6)
      
            
    def test_Driver_suite_api_case(self):
        runner = TestRunner(runner = HttpDriver).run(self.suite_api_case)        
        html_report = runner.gen_html_report()
        #print(html_report)
                
        suite = runner._task_suite.tasks[0]
        self.assertEqual(isinstance(suite.test_runner, Runner), True)
        self.assertEqual(isinstance(suite.test_runner.tracers, dict), True)
        self.assertIsInstance(suite.test_runner.tracers[""], HtmlReporter)
        self.assertEqual(isinstance(suite.test_runner.parser, TestCaseParser), True)        
        self.assertEqual(os.path.isfile(html_report[0]), True)
                
        
if __name__ == "__main__":
    #logger.setup_logger("debug")
#     unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestTestRunner("test_Driver_data_driver_case"))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    
    

    