#! python3
# -*- encoding: utf-8 -*-
'''
Current module: httpdriver.cli

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      httpdriver.cli,  v1.0 2018年7月25日
    FROM:   2018年7月25日
********************************************************************
======================================================================

Provide a function for the automation test

'''

import argparse
from rtsf.p_applog import color_print,logger
from rtsf.p_executer import TestRunner
from httpdriver.driver import HttpDriver
from httpdriver.__about__ import __version__
    
    
def main_hrun():
    """ parse command line options and run commands."""
    
    parser = argparse.ArgumentParser(description="Tools for http(s) test. Base on rtsf.")
            
    parser.add_argument(
        '--log-level', default='INFO',
        help="Specify logging level, default is INFO.")
    
    parser.add_argument(
        '--log-file',
        help="Write logs to specified file path.")
    
    parser.add_argument(
        'case_file', 
        help="yaml testcase file")
    
    color_print("httpdriver {}".format(__version__), "GREEN")
    args = parser.parse_args()
    logger.setup_logger(args.log_level, args.log_file)    
    
    runner = TestRunner(runner = HttpDriver).run(args.case_file)
    html_report = runner.gen_html_report()
    color_print("report: {}".format(html_report))

if __name__ == "__main__":
    main_hrun()