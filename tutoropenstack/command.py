"""tutor openstack: Implements a Click command group for openstack commands.

This defines the "openstack" command group and its subcommands:

* create-cluster
* create-template
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


def check_required_options(config, options):
    """Raise a Click error if a required config.yml option is unset."""
    for option in options:
        if not config.get(option):
            raise click.UsageError(
                f"You must set {option} to a non-empty value."
            )


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


def create_coe_cluster_template_kwargs(config):
    """Construct arguments for the create_coe_cluster_template command."""
    kubernetes_version = config['OPENSTACK_KUBERNETES_VERSION']
    name = config['OPENSTACK_TEMPLATE']
    docker_volume_size = config['OPENSTACK_DOCKER_VOLUME_SIZE']
    external_network = config['OPENSTACK_EXTERNAL_NETWORK']
    master_flavor = config['OPENSTACK_MASTER_FLAVOR']
    node_flavor = config['OPENSTACK_NODE_FLAVOR']
    network_driver = config['OPENSTACK_NETWORK_DRIVER']
    fixed_network = config['OPENSTACK_FIXED_NETWORK']
    fixed_subnet = config['OPENSTACK_FIXED_SUBNET']
    image = config['OPENSTACK_IMAGE']
    hyperkube_prefix = config['OPENSTACK_HYPERKUBE_PREFIX']
    enable_registry = config['OPENSTACK_ENABLE_REGISTRY']

    labels = {
        'container_runtime': 'containerd',
        'cinder_csi_enabled': True,
        'cloud_provider_enabled': True,
        'metrics_server_enabled': False,
    }
    if kubernetes_version:
        labels['kube_tag'] = f'v{kubernetes_version}'
    if hyperkube_prefix:
        labels['hyperkube_prefix'] = hyperkube_prefix

    kwargs = {
        'name': name,
        'coe': 'kubernetes',
        'docker_storage_driver': 'overlay2',
        'docker_volume_size': docker_volume_size,
        'external_network_id': external_network,
        'flavor_id': node_flavor,
        'floating_ip_enabled': True,
        'image_id': image,
        'labels': labels,
        'master_flavor_id': master_flavor,
        'master_lb_enabled': True,
        'volume_driver': 'cinder'
    }
    if network_driver:
        kwargs['network_driver'] = network_driver
    if fixed_network:
        kwargs['fixed_network'] = fixed_network
    if fixed_subnet:
        kwargs['fixed_subnet'] = fixed_subnet
    if enable_registry:
        kwargs['registry_enabled'] = True
        kwargs['insecure_registry'] = 'localhost:5000'
    return kwargs


@openstack.command(help="Create a Kubernetes cluster template on OpenStack")
@click.option('--dry-run', is_flag=True, default=False,
              help="Don't actually interact with OpenStack, "
                   "just show what would be done.")
@click.pass_obj
def create_template(context, dry_run):
    """Create a Magnum cluster template based on Tutor settings."""
    config = tutor_config.load(context.root)

    # We can't provide sensible defaults for these, as they will be
    # differently named in every OpenStack cloud. So, just require
    # that they are set in the configuration.
    check_required_options(
        config,
        ['OPENSTACK_EXTERNAL_NETWORK',
         'OPENSTACK_MASTER_FLAVOR',
         'OPENSTACK_NODE_FLAVOR',
         'OPENSTACK_IMAGE',
        ]
    )

    kwargs = create_coe_cluster_template_kwargs(config)
    fmt.echo_info(
        "Creating cluster template with options:\n%s" % pformat(kwargs)
    )
    if dry_run:
        fmt.echo_info("Dry run, not invoking API call")
    else:
        conn = get_openstack_connection()
        cluster = conn.create_coe_cluster_template(**kwargs)
        fmt.echo_info("Cluster template creation returned:\n%s" %
                      pformat(cluster))
