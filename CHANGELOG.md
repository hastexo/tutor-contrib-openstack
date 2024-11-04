## Unreleased

* [Enhancement] Add the ability to override the registry and registry-ui images (with the `OPENSTACK_REGISTRY_IMAGE` and `OPENSTACK_REGISTRY_UI_IMAGE` options).

## Version 2.1.0 (2024-10-15)

* [Enhancement] Add the ability to run the registry in read-only mode: `tutor openstack registry --read-only`.

## Version 2.0.0 (2024-10-07)

* chore: Drop Python 3.8 support.

## Version 1.5.0 (2024-07-31)

* [Enhancement] Support Tutor 18 and Open edX Redwood.

## Version 1.4.0 (2024-04-05)

* [Enhancement] Support Python 3.12.

## Version 1.3.2 (2024-01-22)

* fix: Un-break cluster template creation with `openstacksdk>=1.0.0`.
* fix: Add the ability to set a boot volume size when creating the
  cluster template (via `OPENSTACK_BOOT_VOLUME_SIZE`).

## Version 1.3.1 (2024-01-16)

* fix: Make the `tutor openstack registry` command behave correctly
  when invoked in Docker-in-Docker.

## Version 1.3.0 (2024-01-12)

* feat: Support Tutor 17 and Open edX Quince.

## Version 1.2.0 (2023-08-23)

* feat: Support Tutor 16, Open edX Palm, and Python 3.11.

## Version 1.1.0 (2023-03-15)

* feat: Support Tutor 15 and Open edX Olive.

## Version 1.0.0 (2022-08-04)

* [BREAKING CHANGE] Support Tutor 14 and Open edX Nutmeg. This entails
  a configuration format change from JSON to YAML, meaning that from
  version 1.0.0 this plugin only supports Tutor versions from 14.0.0
  (and with that, only Open edX versions from Nutmeg).

## Version 0.3.1 (2022-07-21)

* fix: When invoking the OpenStack Magnum API for template creation,
  identify the keypair with `keypair_id`, not just `keypair`.

## Version 0.3.0 (2022-07-20)

* feat: Add the ability to set an SSH keypair on the cluster
  *template,* as opposed to just the cluster.

## Version 0.2.0 (2022-06-29)

* refactor: Use Tutor v1 plugin API.

## Version 0.1.2 (2022-04-27)

* fix: Add a check to wait for the registry to start up before continuing.

## Version 0.1.1 (2022-03-22)

* fix: Add missing whitespace in warning message for `tutor openstack
  registry`

## Version 0.1.0 (2022-02-22)

**Experimental. Do not use in production.**

* Initial experimental release.
