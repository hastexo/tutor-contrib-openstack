# openstack plugin for [Tutor](https://docs.tutor.overhang.io)

This **experimental** plugin adds a `tutor openstack` command group to
Tutor, which you can use to create a Kubernetes cluster with
[OpenStack Magnum](https://docs.openstack.org/magnum/latest/user/),
running on a private or public OpenStack cloud.

You can do so by spinning up a cluster based on a *template* that your
cloud service provider has created for you, or — provided you have the
credentials that allow you to do that — you can create a template
yourself, and then spin up your cluster from that template.

That cluster can then serve as an environment for you to deploy Tutor
with the `tutor k8s` command group.


## Installation

```
pip install git+https://github.com/hastexo/tutor-contrib-openstack@v0.1.0
```


## Usage

Once installed, you enable this plugin with:

```
tutor plugins enable openstack
```

### Creating a cluster

Once properly configured (see below), you can spin up a Kubernetes
cluster with

```
tutor openstack create-cluster
```

... or you can first create a template and *then* spin up a cluster:

```
tutor openstack create-template
tutor openstack create-cluster
```

Either command also supports a `--dry-run` option, where instead of
actually invoking OpenStack cloud API calls, you only see what *would*
be done.


### Deleting a cluster

If you want to delete your cluster, you may do so with this command:

```
tutor openstack delete-cluster
```

This command will prompt you before proceeding with cluster deletion.

**Caution:** deleting your Kubernetes cluster is irreversible and will
delete *all* Tutor deployments in all Kubernetes namespaces. Proceed
at your own risk.


### Running your own registry

OpenStack Magnum has a feature in which it exposes a private registry,
backed by OpenStack Swift, on all worker nodes. You can use this
feature with Tutor, to expose your custom-built images to your
Kubernetes cluster.

To do so, you will have to

1. set `OPENSTACK_ENABLE_REGISTRY` to `true` *before* you run `tutor
   openstack create-template` and `tutor openstack create-cluster`.

2. run `tutor openstack registry` to run a local copy of the registry,
   which is backed by the same Swift object store as that in your
   Kubernetes cluster. To be clear, that means that your locally
   available registry and that in your production cluster *are
   functionally identical,* since they are backed by the same storage.

3. set your Tutor image references to include the `localhost:5000`
   registry.

4. run `tutor images build` and `tutor images push` to create and
   register your images, as you [you normally
   would](https://docs.tutor.overhang.io/configuration.html#custom-open-edx-docker-image)
   with any other custom Tutor images or specific registry.

Please note: when used in this manner, the images in your registry
become available to your entire Kubernetes cluster, not just to a
single namespace. If you are planning to run multiple Tutor
configurations on one cluster, each using its own namespace, and they
should all use different flavors of your custom images, then you must
apply a naming or tagging convention to tell your images apart.


## Configuration

This plugin uses configuration information from two sources:

* the `OS_*` environment variables you use to connect to your
  OpenStack API,
* Tutor’s own `config.yml` configuration.


### OpenStack environment variables

This plugin will read your OpenStack credentials and
project/domain/region configuration from the environment, like any
other OpenStack application would. That means that you can either set
`OS_CLOUD` to select a configuration [from a `clouds.yaml`
file](https://docs.openstack.org/python-openstackclient/latest/cli/man/openstack.html#config-files),
or define a set of individual [`OS_*` environment
variables](https://docs.openstack.org/python-openstackclient/latest/cli/man/openstack.html#environment-variables).


### Required `config.yml` settings

*If you plan to invoke `tutor openstack create-template`,* you must
add the following configuration values to your Tutor `config.yml`. The
plugin cannot provide reasonable defaults for them, as they are bound
to differ between OpenStack installations:

* `OPENSTACK_IMAGE`: The base image UUID to use for your Kubernetes
  cluster nodes. This should be a Fedora CoreOS image, and it **must**
  have its `os_distro` property set to `fedora-coreos`, otherwise
  OpenStack Magnum will refuse to use it. You can also use an image
  name, if it uniquely identifies a single image.
* `OPENSTACK_EXTERNAL_NETWORK`: A network marked `external` that your
  OpenStack environment uses to connect to the outside world, and from
  where your cluster can get floating IPv4 addresses.
* `OPENSTACK_MASTER_FLAVOR`: The flavor to use for your control plane
  (“master”) nodes.
* `OPENSTACK_NODE_FLAVOR`: The flavor to use for your worker
  (“minion”) nodes.

*If you only want to run `tutor openstack create-cluster`,* and rely on
a pre-existing template, then you should also set:

* `OPENSTACK_TEMPLATE`: The name of the OpenStack Magnum cluster
  template to use. You can reference it by UUID or name. The default
  assumes that the template is uniquely named `tutor-kubernetes`.


### Optional `config.yml` settings

All other supported configuration variables are optional to set. These
are the variables that can be set for each *cluster,* and will apply
to any invocation of the `tutor openstack create-cluster` command.

* `OPENSTACK_CLUSTER_NAME`: The name of your Kubernetes cluster
  (default `tutor`).
* `OPENSTACK_KEYPAIR`: The name of an OpenStack SSH keypair you want
  to deploy to your Kubernetes nodes, if you want to be able to SSH
  into them. This is optional; by default no SSH key will be deployed
  and you will only be able to interact with the Kubernetes containers
  with `kubectl exec -it`, if needed.
* `OPENSTACK_MASTER_COUNT`: The number of load-balanced control plane
  (“master”) nodes in your cluster. The default is `1`; for a highly
  available control plane set this to `3`.
* `OPENSTACK_NODE_COUNT`: The number or worker (“minion”) nodes in
  your cluster. The default is `1`; for a production Tutor environment
  you may want to set this to at least `2` for some protection against
  node failure. If you want to run multiple Tutor environments on a
  single cluster in separate Kubernetes namespaces, you might want to
  add more nodes.

Other variables can only be set for a *cluster template,* and will
thus apply only if you run `tutor openstack create-template`:

* `OPENSTACK_KUBERNETES_VERSION`: The Kubernetes version to deploy. If
  unset, this will configure the template to deploy whatever
  Kubernetes release is the default for your version of OpenStack
  Magnum.
* `OPENSTACK_DOCKER_VOLUME_SIZE`: The size of the Docker volume
  configured for your control plane and worker nodes, in GiB. The
  default is `50`.
* `OPENSTACK_FIXED_NETWORK`: A pre-existing OpenStack Neutron network
  to patch your nodes into. The default is to create a new network for
  the cluster.
* `OPENSTACK_FIXED_SUBNET`: A pre-existing OpenStack Neutron subnet to
  patch your nodes into. The default is to create a new subnet for the
  cluster.
* `OPENSTACK_NETWORK_DRIVER`: The network driver to use for your
  Kubernetes cluster. If unset, this will use whatever the default
  network driver is for your OpenStack Magnum installation (usually
  `flannel`). You can alternatively set this to `calico`.
* `OPENSTACK_HYPERKUBE_PREFIX`: The prefix to use for the `hyperkube`
  image. This is required to set for deploying any Kubernetes release
  from 1.19.0 forward. There is no default, but you might want to set
  `docker.io/catalystcloud/`.
* `OPENSTACK_ENABLE_REGISTRY`: Configure your Kubernetes cluster to
  use a private, stateless registry that is backed by OpenStack Swift
  (or any other service exposing the Swift API). Default `false`; if
  you set this to `true` be sure to check with your OpenStack service
  provider if they have configured their Magnum service to support
  this. 


## License

This software is licensed under the terms of the AGPLv3.
