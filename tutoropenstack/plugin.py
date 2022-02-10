"""Plugin definition for the Tutor openstack plugin."""

from glob import glob
import os
import pkg_resources


templates = pkg_resources.resource_filename(
    "tutoropenstack", "templates"
)

config = {}

hooks = {}


def patches():
    """Collect Tutor patches from all available sources."""
    all_patches = {}
    patches_dir = pkg_resources.resource_filename(
        "tutoropenstack", "patches"
    )
    for path in glob(os.path.join(patches_dir, "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
