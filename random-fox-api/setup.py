from setuptools import setup, find_packages

setup(
    name='randomfox',                    
    version='0.1.1',
    packages=find_packages(),
    install_requires=['requests', 'Pillow'],
    author='Stefano Sosa',
    description='API client to get random fox images',
    url='https://github.com/stefano-sosa/random-fox-and-the-cat',
    license='MIT',
    python_requires='>=3.6',
)