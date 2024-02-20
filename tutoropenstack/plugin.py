"""Plugin definition for the Tutor openstack plugin."""

from .command import openstack as openstack_command

import os

# importlib.resources is the standard library module, available since
# Python 3.7. importlib_resources is the backport for older Python
# versions. Normally, we would attempt to import importlib.resources,
# and fall back to importlib_resources on ImportError.
#
# However, in this case we need the files attribute, which was only
# added in 3.9. Thus, we install importlib_resources as a library on
# 3.8 and try to import it here. If importlib_resources is *not*
# installed as a library, we assume we're on 3.9 or later, where we
# can use importlib.resources.files rather than
# importlib_resources.files.
#
# Confused yet?
try:
    import importlib_resources as resources
except ImportError:
    from importlib import resources

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
    },
}

hooks.Filters.CLI_COMMANDS.add_item(openstack_command)

# Add the "templates" folder as a template root
templates = resources.files('tutoropenstack') / 'templates'
with resources.as_file(templates) as path:
    hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(path)

# Render the "build" and "apps" folders
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("openstack/build", "plugins"),
        ("openstack/apps", "plugins"),
    ],
)
# Load patches from files
for path in resources.files('tutoropenstack.patches').iterdir():
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
