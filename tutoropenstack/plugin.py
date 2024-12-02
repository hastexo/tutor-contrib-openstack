"""Plugin definition for the Tutor openstack plugin."""

from glob import glob
from .command import openstack as openstack_command

import os
# When Tutor drops support for Python 3.8, we'll need to update this to:
# from importlib import resources as importlib_resources
# See: https://github.com/overhangio/tutor/issues/966#issuecomment-1938681102
import importlib_resources

from tutor import hooks


config = {
    "defaults": {
        'CLUSTER_NAME': 'tutor',
        'TEMPLATE': 'tutor-kubernetes',
        'TEMPLATE_KEYPAIR': None,
        'KEYPAIR': None,
        'MASTER_COUNT': 1,
        'NODE_COUNT': 1,
        'KUBERNETES_VERSION': None,
        'DOCKER_VOLUME_SIZE': 50,
        'BOOT_VOLUME_SIZE': None,
        'FIXED_NETWORK': None,
        'FIXED_SUBNET': None,
        'NETWORK_DRIVER': None,
        'HYPERKUBE_PREFIX': None,
        'ENABLE_REGISTRY': False,
        'REGISTRY_IMAGE': 'registry:2',
        'REGISTRY_UI_IMAGE': 'joxit/docker-registry-ui:2',
    },
}

hooks.Filters.CLI_COMMANDS.add_item(openstack_command)

# Add the "templates" folder as a template root
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    str(importlib_resources.files("tutoropenstack") / "templates")
)
# Render the "build" and "apps" folders
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("openstack/build", "plugins"),
        ("openstack/apps", "plugins"),
    ],
)
# Load patches from files
for path in glob(str(
        importlib_resources.files("tutoropenstack") / "patches" / "*")):

    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item(
            (os.path.basename(path), patch_file.read())
        )
# Add configuration entries
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        (f"OPENSTACK_{key}", value)
        for key, value in config.get("defaults", {}).items()
    ]
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        (f"OPENSTACK_{key}", value)
        for key, value in config.get("unique", {}).items()
    ]
)
hooks.Filters.CONFIG_OVERRIDES.add_items(
    list(config.get("overrides", {}).items())
)
