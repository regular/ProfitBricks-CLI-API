import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
      name='pbapi',
      version='1.2.2',
      url='https://github.com/profitbricks/ProfitBricks-CLI-API',
      author='ProfitBricks',
      author_email='support@profitbricks.com',
      license='Apache',
      keywords='profitbricks IaaS cloud',
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
                   'Topic :: Software Development :: Libraries',
                   'License :: OSI Approved :: Apache Software License',
                  ],
      description='ProfitBricks API',
      long_description=read('README'),
      package_dir={'': 'src'},
      packages=['pb'],
      install_requires=['suds']
     )
