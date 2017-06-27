# kubepy

[![Latest Version](https://img.shields.io/pypi/v/kubepy.svg)](https://github.com/socialwifi/kubepy/blob/master/CHANGELOG.md)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/kubepy.svg)](https://pypi.python.org/pypi/kubepy/)
[![Wheel Status](https://img.shields.io/pypi/wheel/kubepy.svg)](https://pypi.python.org/pypi/kubepy/)
[![License](https://img.shields.io/pypi/l/kubepy.svg)](https://github.com/socialwifi/kubepy/blob/master/LICENSE)

Python wrapper on kubectl that makes deploying easy.

## Installation
Requires python 3.5 and configured kubectl. To install run:
`pip3 install kubepy`

## Usage
You can use this package to install all yml definitions from given directory.
Supported kinds are deployment, service, secret, job, storage class, persistent volume,
persistent volume claim, stateful set and ingress.
Just run `kubepy-apply-all` from a directory where all of you kubernetes definition yml files are.

Options:
* `--directory <path>` - uses path instead of local directory.
  Can be used multiple times to add new and partialy override existing definitions.
* `--build-tag <tag>` - sets tag to all images without specified tag in your definition files
* `--replace` - if present, replaces deployments instead of updating them. Default: false.
* `--host-volume <name>=<path>` Adds host volume to each pod definition. Can be used multiple times.
* `--env <VAR>=value` Sets environment vatiable on every container.
* `--max-job-retries <n>` While waiting for job to finish if it fails n times than delete job and fail.
  Job sometimes can still be executed more than n times.

There is also `kubepy-apply-one` command which is called as `kubepy-apply-one name1 [name2 ...]`
It applies only files selected files. Names should be without ".yml".
It accepts all options from `kubepy-apply-all`. Additionaly you can pass option:
* `--show-definition` - shows definition instead of applying them.

## Applying jobs.
Applying usualy means that underlying `kubectl apply` or `kubectl replace` is called. However applying job is treated differently.
To ensure that job finished and succeeded kubectl waits for job to finish and fails if job failed.

## Applying pods.
Usualy you don't need to aply pods manualy, but if you want to run some kind of check and you need to know if it succeeded without retries then you can use pod with `restartPolicy: Never`. Only pods with this policy are currently supported. They are treated as jobs, so applying waits for them to finish and fails if they fail.
