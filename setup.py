from setuptools import setup, find_packages

setup(
    name='resonance',
    version='1.1.0',
    packages=find_packages(),
    url='',
    license='LGPL',
    author='Yury Nuzhdin',
    author_email='nuzhdin.urii@gmail.com',
    description='',
    install_requires=[
        'numpy',
        'scipy',
        'numpy_ringbuffer'
    ]
)
