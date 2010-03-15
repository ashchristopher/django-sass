import os
from distutils.core import setup
# from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='django-sass',
    version='0.1.0',
    author='Ash Christopher',
    author_email='ash@newthink.net',
    description='Sass library for django.',
    packages=['sass', ],
    scripts=[],
    url='http://github.com/ashchristopher/django-sass',
    license='LICENSE.txt',
    keywords = "example documentation tutorial",
    long_description=read('README'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: Linux, BSD, OSX",
        "Natural Language :: English",
        "Topic :: Utilities",
        "Topic :: Django",
    ],
)