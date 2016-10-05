# kubepy
Python wrapper on kubectl that makes deploying easy.

## Installation
Requires python 3.5 and configured kubectl. To install run:
`pip3 install kubepy`

## Usage
You can use this package to install all yml definitions from given directory.
Supported kinds are deployment, service, secret and job.
Just run `kubepy-apply-all` from a directory where all of you kubernetes definition yml files are.

Options:
* --directory <path> - uses path instead of local directory
* --build-tag <tag> - sets tag to all images without specified tag in your definition files
