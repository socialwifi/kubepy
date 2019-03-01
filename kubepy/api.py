import subprocess
import sys

import tenacity
import yaml


class ApiError(Exception):
    pass


@tenacity.retry(reraise=True, retry=tenacity.retry_if_exception_type(ApiError), stop=tenacity.stop_after_attempt(3))
def get(kind, name=None):
    command = ['kubectl', 'get', '-o', 'yaml', kind]
    if name:
        command.append(name)
    get_process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=sys.stderr)
    objects = yaml.load(get_process.stdout)
    if get_process.wait() != 0:
        raise ApiError
    return objects


def logs(pod_name, container_name=None):
    command = ['kubectl', 'logs', pod_name]
    if container_name:
        command += ['-c', container_name]
    log_process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = log_process.communicate()
    if log_process.returncode != 0:
        raise ApiError
    return stdout, stderr


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
    create_process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = create_process.communicate(yaml.dump(definition).encode())
    create_process.stdin.close()
    if create_process.wait() != 0:
        raise ApiError(stderr)
