import os
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext

USE_CYTHON = True

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None
    if USE_CYTHON:
        raise RuntimeError("You've set USE_CYTHON=1 but don't have Cython installed!")

# https://stackoverflow.com/questions/54117786/add-numpy-get-include-argument-to-setuptools-without-preinstalled-numpy
class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        import numpy
        self.include_dirs.append(numpy.get_include())
        
        
# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                ext = ".c"
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions


extensions = [
    Extension(
        "qoi.qoi",
        sources=["src/qoi/qoi.pyx", "src/qoi/implementation.c"],
        define_macros=[("QOI_MALLOC", "PyMem_Malloc"), ("QOI_FREE", "PyMem_Free")],
    )
]


if USE_CYTHON:
    compiler_directives = {
        "language_level": 3,
        "embedsignature": True,
        "boundscheck": False,
        "wraparound": False,
        "cdivision": True,
    }
    extensions = cythonize(extensions, compiler_directives=compiler_directives)
else:
    extensions = no_cythonize(extensions)

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

with open("requirements-dev.txt") as f:
    dev_requires = f.read().strip().split("\n")

setup(
    ext_modules=extensions,
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
    },
    cmdclass={'build_ext': build_ext}
)
