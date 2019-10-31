from setuptools import find_packages
from distutils.core import setup, Extension

rpiolib = Extension('rpiolib',
    define_macros = [
        ('MAJOR_VERSION', '1'),
        ('MINOR_VERSION', '0')\
    ],
    include_dirs = ['/usr/local/include', 'pyrpio/lib'],
    library_dirs = ['/usr/local/lib'],
    sources = [
        'pyrpio/lib/bcm2835.c',
        'pyrpio/lib/mdio.c',
        'pyrpio/lib/module.c'
    ]
)

setup (name = 'PyRPIO',
       version = '0.0.1',
       description = 'Python-wrapped RPIO',
       author = 'Samtec - ASH',
       author_email = 'samtec-ash@samtec.com',
       url = 'https://github.com/Samtec-ASH/pyrpio',
       long_description = '''Python-wrapped RPIO.''',
       ext_package='pyrpio',
       ext_modules = [rpiolib],
       packages = find_packages()
)