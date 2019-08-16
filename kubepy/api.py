import subprocess
import sys

import tenacity
import yaml


class ApiError(Exception):
    pass


def kubectl_command_builder(basic_command, resource=None, name=None, container_name=None,
                            namespace=None, flags=None, with_definition=False):
    command = ['kubectl', basic_command]
    if resource:
        command.append(resource)
    if name:
        command.append(name)
    if container_name:
        command += ['-c', container_name]
    if namespace:
        command += ['--namespace', namespace]
    if flags:
        command += flags
    if with_definition:
        command += ['-f', '-']
    return command


@tenacity.retry(reraise=True, retry=tenacity.retry_if_exception_type(ApiError), stop=tenacity.stop_after_attempt(3))
def get(kind, name=None, namespace=None):
    command = kubectl_command_builder('get', resource=kind, name=name, namespace=namespace, flags=['-o', 'yaml'])
    get_process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=sys.stderr)
    objects = yaml.safe_load(get_process.stdout)
    if get_process.wait() != 0:
        raise ApiError
    return objects


def get_failed_pod_for_job(job_name, namespace=None):
    command = kubectl_command_builder('get', resource='pod', namespace=namespace,
                                      flags=['-o', 'yaml', '--field-selector', 'status.phase=Failed', '-l',
                                             'job-name={}'.format(job_name)])
    get_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=sys.stderr)
    objects = yaml.safe_load(get_process.stdout)
    if get_process.wait() != 0:
        raise ApiError
    return objects


def logs(pod_name, container_name=None, namespace=None):
    command = kubectl_command_builder('logs', name=pod_name, container_name=container_name, namespace=namespace)
    log_process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = log_process.communicate()
    if log_process.returncode != 0:
        raise ApiError
    return stdout, stderr


def create(definition, namespace=None):
    command = kubectl_command_builder('create', namespace=namespace, with_definition=True)
    run_command_with_yaml_on_stdin(command, definition)


def apply(definition, namespace=None):
    command = kubectl_command_builder('apply', namespace=namespace, flags=['--record'], with_definition=True)
    run_command_with_yaml_on_stdin(command, definition)


def replace(definition, namespace=None):
    command = kubectl_command_builder('replace', namespace=namespace, flags=['--force', '--cascade'],
                                      with_definition=True)
    run_command_with_yaml_on_stdin(command, definition)


def rolling_update(definition, name, namespace=None):
    command = kubectl_command_builder('rolling-update', name=name, namespace=namespace, with_definition=True)
    run_command_with_yaml_on_stdin(command, definition)


def delete(kind, name, namespace=None):
    command = kubectl_command_builder('delete', resource=kind, name=name, namespace=namespace)
    subprocess.check_call(command)


def run_command_with_yaml_on_stdin(command, definition):
    create_process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = create_process.communicate(yaml.dump(definition).encode())
    create_process.stdin.close()
    if create_process.wait() != 0:
        raise ApiError(stderr)
