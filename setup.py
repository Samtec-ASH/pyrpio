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
        'pyrpio/lib/module.c',
        'pyrpio/lib/bcm2835.c'
    ]
)

mdiolib = Extension('mdiolib',
    define_macros = [
        ('MAJOR_VERSION', '1'),
        ('MINOR_VERSION', '0')\
    ],
    include_dirs = ['/usr/local/include', 'pyrpio/lib'],
    library_dirs = ['/usr/local/lib'],
    sources = [
        'pyrpio/mdio/module.c',
        'pyrpio/mdio/mdio.c',
        'pyrpio/lib/bcm2835.c'
    ]
)

setup (name = 'PyRPIO',
       version = '1.0.0',
       description = 'Python-wrapped RPIO',
       author = 'Samtec - ASH',
       author_email = 'samtec-ash@samtec.com',
       url = 'https://docs.python.org/extending/building',
       long_description = '''Python-wrapped RPIO.''',
       ext_package='pyrpio',
       ext_modules = [rpiolib, mdiolib],
       packages = find_packages()
)