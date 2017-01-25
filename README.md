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
persistent volume claim and stateful set.
Just run `kubepy-apply-all` from a directory where all of you kubernetes definition yml files are.

Options:
* --directory <path> - uses path instead of local directory.
  Can be used multiple times to add new and partialy override existing definitions.
* --build-tag <tag> - sets tag to all images without specified tag in your definition files
* --replace - if present, replaces deployments instead of updating them. Default: false.
* --host-volume <name>=<path> Adds host volume to each pod definition. Can be used multiple times.
