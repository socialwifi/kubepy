import subprocess

import sys
import yaml


class ApiError(Exception):
    pass


def get(kind, selector=()):
    selector_query = sum(
        (['-l', '{}={}'.format(key, value)] for key, value in selector),
        [])
    get_process = subprocess.Popen(
        ['kubectl', 'get', kind, *selector_query, '-o', 'yaml'],
        stdout=subprocess.PIPE, stderr=sys.stderr)
    objects = yaml.load(get_process.stdout)
    if get_process.wait() != 0:
        raise ApiError
    return objects


def create(definition):
    run_command_with_yaml_on_stdin(
        ['kubectl', 'create', '-f', '-'], definition)


def apply(definition):
    run_command_with_yaml_on_stdin(
        ['kubectl', 'apply', '--record', '-f', '-'], definition)


def replace(definition):
    run_command_with_yaml_on_stdin(
        ['kubectl', 'replace', '--force', '--cascade', '--record', '-f', '-'], definition)


def rolling_update(definition, name):
    run_command_with_yaml_on_stdin(
        ['kubectl', 'rolling-update', name, '-f', '-'],
        definition)


def delete(kind, name):
    subprocess.check_call(['kubectl', 'delete', kind, name])


def run_command_with_yaml_on_stdin(command, definition):
    create_process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=sys.stderr)
    create_process.communicate(yaml.dump(definition).encode())
    create_process.stdin.close()
    if create_process.wait() != 0:
        raise ApiError()
