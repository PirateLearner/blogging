import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__),'README.rst')) as readme:
	README = readme.read()

#allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name='pi-blogging',
	version='0.1.0b1',
	packages=['blogging'],
	include_package_data=True,
	license='GPL v2',
	description='A Simple Blogging App that enables you to create content and content types from frontend itself.',
	author=['Abhishek Rai','Anshul Thakur'],
	author_email=['captain@piratelearner.com'],
	long_description=README,
	url='https://github.com/PirateLearner/blogging',
	download_url='https://github.com/PirateLearner/blogging/archive/0.1.1-beta.tar.gz',
	install_requires=[
			 "Django ==1.6.8",
			 "django-classy-tags ==0.4",
			'html5lib ==1.0b1',
			'django-mptt ==0.6',
			'django-sekizai ==0.7',
			'six ==1.3.0',
			'django-ckeditor ==4.4.4'],
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
)


