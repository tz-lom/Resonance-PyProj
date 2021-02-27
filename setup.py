from setuptools import setup, find_packages

setup(name='resonance',
      version_config=True,
      packages=find_packages(),
      url='',
      license='MIT',
      author='Yury Nuzhdin',
      author_email='nuzhdin.urii@gmail.com',
      description='',
      install_requires=['numpy', 'scipy', 'numpy_ringbuffer'],
      setup_requires=['setuptools-git-versioning'])
