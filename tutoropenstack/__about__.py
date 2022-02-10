"""Convenience facility to return the installed package version.

Sets the __version__ attribute as suggested by (deferred) PEP 396:
https://www.python.org/dev/peps/pep-0396/

Single-source package definition as suggested (among several
options) by:
https://packaging.python.org/guides/single-sourcing-package-version/
"""

import pkg_resources
__version__ = pkg_resources.get_distribution(
    'tutor-contrib-openstack').version
