from setuptools import setup

import os

# Put here required packages
packages = ['Django==1.8.3', 'mongoengine==0.9.0', 'pymongo==2.8', 'wheel==0.24.0']

#if 'REDISCLOUD_URL' in os.environ and 'REDISCLOUD_PORT' in os.environ and 'REDISCLOUD_PASSWORD' in os.environ:
#     packages.append('django-redis-cache')
#     packages.append('hiredis')

setup(name='AnnotationTool',
      version='1.0',
      description='OpenShift App',
      author='fensta',
      author_email='fensta.git@gmail.com',
      url='http://annotationtool-fensta.rhcloud.com/',
      install_requires=packages,
)

