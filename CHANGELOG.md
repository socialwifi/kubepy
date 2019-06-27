Changelog for kubepy
=================

1.14.0 (2019-06-27)
-------------------

- Display logs for failed Jobs.


1.13.1 (2019-04-16)
-------------------

- Fix YAMLLoadWarning: https://msg.pyyaml.org/load


1.13.0 (2019-03-01)
-------------------

- Removed deprecated `--record` flag when using `replace` command.
- Improved code style (enabled static analysis).


1.12.1 (2019-02-15)
-------------------

- Minor packaging improvements.


1.12.0 (2019-02-15)
-------------------

- Improve support for CronJob resource.
- Support pip >= 10.


1.11.1 (2018-07-17)
-------------------

- Fix merging definitions.


1.11.0 (2018-03-29)
-------------------

- Support CronJob resource.


1.10.0 (2018-01-27)
-------------------

- Added `--annotate` and `--annotate-pod` options for adding annotations.
- Added `--label` and `--label-pod` options to add labels to each pod.


1.9.0 (2017-11-23)
------------------

- Support PodDisruptionBudget resource.


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
