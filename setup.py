from distutils.core import setup, Extension

mdio = Extension(
    'pyrpio.mdio',
    define_macros = [
        ('MAJOR_VERSION', '1'),
        ('MINOR_VERSION', '0')\
    ],
    include_dirs = ['/usr/local/include'],
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
       ext_modules = [mdio]
)