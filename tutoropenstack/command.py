"""tutor openstack: Implements a Click command group for openstack commands.

This defines the "openstack" command group and its subcommands:

* create-cluster
"""
import click

from tutor import config as tutor_config
from tutor import fmt

from openstack import connection
from pprint import pformat


@click.group(name="openstack",
             help="Manage a Kubernetes cluster on OpenStack")
@click.pass_obj
def openstack(context):
    """Define the "openstack" command group."""
    pass


def get_openstack_connection():
    """Fetch an OpenStack connection using standard configuration sources."""
    # from_config just happens to be the name of the method in the
    # OpenStack SDK that initializes the connection based on OS_*
    # environment variables, or a configuration file in combination
    # with OS_CLOUD. It has nothing to do with the tutor.config
    # dictionary.
    return connection.from_config()


def create_coe_cluster_kwargs(config):
    """Construct arguments for the create_coe_cluster command."""
    name = config['OPENSTACK_CLUSTER_NAME']
    cluster_template = config['OPENSTACK_TEMPLATE']
    keypair = config['OPENSTACK_KEYPAIR']
    master_count = config['OPENSTACK_MASTER_COUNT']
    node_count = config['OPENSTACK_NODE_COUNT']
    timeout = 60

    kwargs = {
        'name': name,
        'cluster_template_id': cluster_template,
        'master_count': master_count,
        'node_count': node_count,
        'create_timeout': timeout,
    }
    if keypair:
        kwargs['keypair'] = keypair
    return kwargs


@openstack.command(help="Create a Kubernetes cluster on OpenStack")
@click.option('--dry-run', is_flag=True, default=False,
              help="Don't actually interact with OpenStack, "
                   "just show what would be done.")
@click.pass_obj
def create_cluster(context, dry_run):
    """Create a Magnum cluster based on Tutor settings."""
    config = tutor_config.load(context.root)
    kwargs = create_coe_cluster_kwargs(config)
    fmt.echo_info(
        "Launching cluster with options:\n%s" % pformat(kwargs)
    )
    if dry_run:
        fmt.echo_info("Dry run, not invoking API call")
    else:
        conn = get_openstack_connection()
        cluster = conn.create_coe_cluster(**kwargs)
        fmt.echo_info("Cluster launch returned:\n%s" %
                      pformat(cluster))
