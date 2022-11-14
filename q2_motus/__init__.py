from ._taxonomy import profile, import_table
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

__all__ = ['profile', 'import_table']

from .plugin_setup import (
    MotusMergedAbundanceTable,
    MotusMergedAbundanceFormat, 
    MotusMergedAbundanceDirectoryFormat
    )
