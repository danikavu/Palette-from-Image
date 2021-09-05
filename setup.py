from setuptools import setup

setup(
	name='imgpalette',
	version='1.0.0',
	author='Daniel Kavoulakos',
	author_email='dan_kavoulakos@hotmail.com',
	description='Creates a color palette based on a given Image.',
	license='MIT',
	packages=['.imgpalette'],
	install_requires=['numpy',
					  'requests',
					  'scikit-learn',
					  'pillow',
					  ],
	python_requires='>=3.7',
)
					  