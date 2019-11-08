from setuptools import find_packages, setup, Extension
import io
import re

with open('README.md', 'r') as fp:
    long_description = fp.read()

with io.open("pyrpio/__init__.py", "rt", encoding="utf8") as fp:
    version = re.search(r'__version__ = "(.*?)"', fp.read()).group(1)
    (major_version, minor_version, revision) = version.split('.')

rpiolib = Extension('rpiolib',
    define_macros = [
        ('MAJOR_VERSION', major_version),
        ('MINOR_VERSION', minor_version)\
    ],
    include_dirs = ['/usr/local/include', 'pyrpio/lib'],
    library_dirs = ['/usr/local/lib'],
    sources = [
        'pyrpio/lib/bcm2835.c',
        'pyrpio/lib/mdio.c',
        'pyrpio/lib/module.c'
    ]
)

setup(
    name = 'PyRPIO',
    version=version,
    description = 'Python-wrapped RPIO',
    long_description = long_description,
    long_description_content_type="text/markdown",
    author = 'Samtec - ASH',
    author_email = 'samtec-ash@samtec.com',
    url = 'https://github.com/Samtec-ASH/pyrpio',
    ext_package='pyrpio',
    ext_modules = [rpiolib],
    packages = find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
)