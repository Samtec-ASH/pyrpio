from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError
from distutils.command.build_ext import build_ext
from distutils.extension import Extension

ext_modules = [
    Extension(
        "rpiolib",
        include_dirs=['/usr/local/include', 'pyrpio/lib'],
        library_dirs=['/usr/local/lib'],
        sources=[
            'pyrpio/lib/bcm2835.c',
            'pyrpio/lib/mdio.c',
            'pyrpio/lib/module.c'
        ]
    )
]


class BuildFailed(Exception):
    pass


class ExtBuilder(build_ext):

    def run(self):
        try:
            build_ext.run(self)
        except (DistutilsPlatformError, FileNotFoundError):
            raise BuildFailed('File not found. Could not compile C extension.')

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError, DistutilsPlatformError, ValueError):
            raise BuildFailed('Could not compile C extension.')


def build(setup_kwargs):
    """
    This function is mandatory in order to build the extensions.
    """
    setup_kwargs.update(
        {"ext_modules": ext_modules, "cmdclass": {"build_ext": ExtBuilder}}
    )
