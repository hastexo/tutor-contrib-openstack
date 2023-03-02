## Unreleased

 * Support Tutor 15 and Open edX Olive.

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
