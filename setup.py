from setuptools import setup

setup(name='repostat',
      version='0.1',
      description='A tool to store custom repository statistics and issues with commit level resolution in a redis store.',
      url='http://github.com/JamesJeffryes/repo-stat-stash',
      author='James Jeffryes',
      author_email='jamesgjeffryes@gmail.com',
      license='MIT',
      packages=['repostat'],
      install_requires=['redis'],
      keywords=['testing', 'code quality', 'github']
      )
