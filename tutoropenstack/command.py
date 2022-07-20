"""tutor openstack: Implements a Click command group for openstack commands.

This defines the "openstack" command group and its subcommands:

* create-cluster
* create-template
* delete-cluster
* registry
"""
import click
import yaml
import requests

from urllib3 import Retry
from urllib3.exceptions import MaxRetryError
from tutor import config as tutor_config
from tutor import fmt
from tutor.utils import docker_run

from openstack import connection
from pprint import pformat
from tempfile import NamedTemporaryFile

# Magnum generally expects the container to be named exactly like
# this. Whoever administers the Magnum service can change this with a
# configuration override, but this is practically never done.
REGISTRY_SWIFT_CONTAINER = 'docker_registry'


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
    keypair = config['OPENSTACK_TEMPLATE_KEYPAIR']

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
    if keypair:
        kwargs['keypair_id'] = keypair
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


@openstack.command(help="Delete Kubernetes cluster running on OpenStack")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation.")
@click.option('--dry-run', is_flag=True, default=False,
              help="Don't actually interact with OpenStack, "
                   "just show what would be done.")
@click.pass_obj
def delete_cluster(context, dry_run, yes):
    """Delete a Magnum cluster based on Tutor settings."""
    config = tutor_config.load(context.root)
    cluster_name = config['OPENSTACK_CLUSTER_NAME']

    if not yes:
        click.confirm(
            f"Are you sure you want to delete cluster \"{cluster_name}\"? "
            "All data will be removed.",
            abort=True,
        )

    fmt.echo_info(f"Sending request to delete cluster \"{cluster_name}\"")
    if dry_run:
        fmt.echo_info("Dry run, not invoking API call")
    else:
        conn = get_openstack_connection()
        if conn.delete_coe_cluster(cluster_name):
            fmt.echo_info("Cluster deletion request sent")
        else:
            fmt.echo_info("Cluster deletion request failed")


def create_registry_config(conn):
    """Create a configuration for a Swift-backed registry container."""
    registry_config = {
        'version': '0.1',
        'http': {
            'addr': ':5000',
            'headers': {
                'Access-Control-Allow-Origin': ['*'],
                'Access-Control-Allow-Methods': [
                    'HEAD',
                    'GET',
                    'OPTIONS',
                    'DELETE'
                ],
                'Access-Control-Expose-Headers': [
                    'Docker-Content-Digest',
                ],
            },
        },
        'storage': {
            'swift': {
                'authurl': conn.auth['auth_url'],
                'authversion': 3,
                'username': conn.auth['username'],
                'domain': conn.auth['user_domain_name'],
                'password': conn.auth['password'],
                'container': REGISTRY_SWIFT_CONTAINER,
                'tenant': conn.auth['project_name'],
                'tenantdomain': conn.auth['project_domain_name'],
                'region': conn.identity.region_name,
            },
            'delete': {
                'enabled': True
            },
        },
        'log': {
            'level': 'debug',
            'fields': {
                'service': 'registry',
            },
        },
    }
    return registry_config


@openstack.command(help="Run a local registry for pushing images "
                   "to an OpenStack Kubernetes cluster")
@click.option("--with-ui", is_flag=True,
              help="Run a local registry web user interface")
@click.pass_obj
def registry(context, with_ui):
    """Run a local registry on port 5000, with an optional web UI."""
    config = tutor_config.load(context.root)
    if not config['OPENSTACK_ENABLE_REGISTRY']:
        fmt.echo_alert("OPENSTACK_ENABLE_REGISTRY is not set to true. "
                       "You must set it so your OpenStack Kubernetes cluster "
                       "can use this registry.")
    # TODO: This should also check the cluster (and template) to see
    # if it exposes a registry.

    conn = get_openstack_connection()
    registry_config = create_registry_config(conn)
    registry_title = "%s in %s" % (conn.auth['project_name'],
                                   conn.identity.region_name)

    # The registry's config.yml contains OpenStack credentials. We
    # don't want those to be acessible from the host, so we use a
    # NamedTemporaryFile here which is unlinked from the filesystem as
    # soon as we leave the context manager (i.e. as soon as "docker
    # run -d" is done firing up the container).
    #
    # Not leaking the OpenStack credentials is also why we're doing
    # things this way in the first place, rather than just adding
    # docker-compose patches for both services.
    with NamedTemporaryFile(mode="r+", suffix=".yml") as config_file:
        yaml.safe_dump(registry_config, config_file)
        fmt.echo_info("Wrote registry configuration to %s" % config_file.name)

        registry_args = [
            "-d",
            "--network", "host",
            "-v", "%s:/etc/docker/registry/config.yml" % config_file.name,
            "--name", "tutor-openstack-registry",
            "registry:2"
        ]

        docker_run(*registry_args)

        # Check if the registry service has started up before continuing.
        # Retry with backoff factor 2 and total of 10 means the amount of
        # sleep will exponentially increase between retires up to 256
        # seconds. So we can wait up to 17 minutes total for the registry
        # service to start working.
        retries = Retry(total=10, backoff_factor=2,
                        status_forcelist=[429, 500, 502, 503, 504])
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        session = requests.sessions.Session()
        session.mount("http://", adapter)
        try:
            session.get("http://localhost:5000/v2/_catalog")
        except MaxRetryError:
            raise

        fmt.echo_info(f"OpenStack-backed registry for {registry_title} "
                      "running at http://localhost:5000")

    if with_ui:
        # This really should also run with "--network host", but the image
        # has no way to override its listening port (it hardcodes 80/tcp),
        # so it can't run in host networking mode except when running as
        # root. Thus, to make it run as non-root, use default (bridged)
        # networking instead, and publish container port 80 as host port
        # 8000.
        registry_ui_args = [
            "--detach",
            "--publish", "8000:80",
            "-e", "SINGLE_REGISTRY=true",
            "-e", "REGISTRY_URL=http://localhost:5000",
            "-e", f"REGISTRY_TITLE={registry_title}",
            "-e", "DELETE_IMAGES=true",
            "--name", "tutor-openstack-registry-ui",
            "joxit/docker-registry-ui:2"
        ]
        docker_run(*registry_ui_args)
        fmt.echo_info(f"Registry web UI for {registry_title} "
                      "running at http://localhost:8000")
