from distribute_setup import use_setuptools; use_setuptools()
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-sass',
    version='0.1.0',
    packages = find_packages(),
    author='Ash Christopher',
    author_email='ash@newthink.net',
    description='Django library that integrates Sass into your project.',
    license='LICENSE.txt',
    url='http://github.com/ashchristopher/django-sass',
    keywords='django sass ',
    long_description=read('README'),
    
)