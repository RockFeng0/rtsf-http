#! python3
# -*- encoding: utf-8 -*-
'''
Current module: setup

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:    lkf20031988@163.com
    RCS:      setup,v 1.0 2018年7月24日
    FROM:   2018年7月24日
********************************************************************

======================================================================

UI and Web Http automation frame for python.

'''
from httpdriver import __about__
from setuptools import setup, find_packages

install_requires = [
    "requests",
    "rtsf",
]

# dependency_links=[
# "git+https://github.com/RockFeng0/rtsf.git#egg=rtsf-0"
# ]

setup(
        name = __about__.__title__,
        version=__about__.__version__,        
        description=__about__.__short_desc__,
        author=__about__.__autor__,
        author_email=__about__.__author_email__,
        url=__about__.HOME_PAGE,
        license=__about__.__license__,
        python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
        packages=find_packages(exclude=()),        
        keywords='test http api https',
        install_requires=install_requires,
#         dependency_links=dependency_links,
        extras_require={},
        entry_points={
        'console_scripts': [
            'httpdriver=httpdriver.cli:main_hrun',
            'hdriver=httpdriver.cli:main_hrun',
        ]
    },
    )
