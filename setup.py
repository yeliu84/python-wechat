from setuptools import setup

import wechat

setup(name='wechat',
      description='Interfaces and utilities for WeChat database',
      packages=['wechat'],
      scripts=['scripts/wechatlog'],
      version=wechat.__version__,
      license=wechat.__license__,
      author=wechat.__author__,
      author_email=wechat.__contact__,
      url='http://wechatlog.com')
