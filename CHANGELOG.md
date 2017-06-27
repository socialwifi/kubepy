Changelog for kubepy
=================

1.8.0 (2017-06-27)
------------------

- Support ingress resource.


1.7.1 (2017-03-24)
------------------

- Fix Adding command line options.


1.7.0 (2017-03-24)
------------------

- Added tenacity to kubectl get command.
- Added --max-job-retries option to fail after job failed too many times.


1.6.0 (2017-02-27)
------------------

- Added --show-definition option to apply one for easier debugging.
- Added --env option to set environment variables on every container.


1.5.1 (2017-01-26)
------------------

- Added support for StatefulSet, StorageClass, PersistentVolume and PersistentVolumeClaim


1.5.0 (2017-01-13)
------------------

- Allowed --directory <path> to be used multiple times to override definitions.
- Added --host-volume <name>=<path> to add host volume to pod definitions.


1.4.0 (2016-12-07)
------------------

- Add pod as one time job support.
- Don't require app label in jobs.


1.3.0 (2016-11-25)
------------------

- Handle exceeded deadline in job applier.


1.2.0 (2016-10-21)
------------------

- Allow to replace deployments instead of updating them.

1.1 (2016-10-06)
----------------

- Changes tracking started.
