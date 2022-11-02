from ._hello import print_hello
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

__all__ = ['print_hello']
