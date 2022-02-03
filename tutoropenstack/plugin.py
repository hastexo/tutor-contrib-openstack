"""Plugin definition for the Tutor openstack plugin."""

from glob import glob
from .command import openstack as openstack_command

import os
import pkg_resources


templates = pkg_resources.resource_filename(
    "tutoropenstack", "templates"
)


config = {
    "defaults": {
        'CLUSTER_NAME': 'tutor',
        'TEMPLATE': 'tutor-kubernetes',
        'KEYPAIR': None,
        'MASTER_COUNT': 1,
        'NODE_COUNT': 1,
        'KUBERNETES_VERSION': None,
        'DOCKER_VOLUME_SIZE': 50,
        'FIXED_NETWORK': None,
        'FIXED_SUBNET': None,
        'NETWORK_DRIVER': None,
        'HYPERKUBE_PREFIX': None,
        'ENABLE_REGISTRY': False,
    },
}


hooks = {}


command = openstack_command


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
