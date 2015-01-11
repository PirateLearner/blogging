import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__),'README.rst')) as readme:
	README = readme.read()

#allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name='pi-blogging',
	version='0.1-beta',
	packages=['blogging'],
	include_package_data=True,
	license='GPL v2',
	description='A Simple Blogging App that enables you to create content and content types from frontend itself.',
	author=['Abhishek Rai','Anshul Thakur'],
	author_email=['captain@piratelearner.com'],
	long_description=README,
	url='http://piratelearner.com',
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GPL v2 License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
)


