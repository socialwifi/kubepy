from setuptools import find_packages
from setuptools import setup


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


def get_long_description():
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name='kubepy',
    version='1.17.0',
    description='Python wrapper on kubectl that makes deploying easy.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Social WiFi',
    author_email='it@socialwifi.com',
    url='https://github.com/socialwifi/kubepy',
    packages=find_packages(exclude=['tests']),
    install_requires=[str(r) for r in parse_requirements('base_requirements.txt')],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'kubepy-apply-all = kubepy.commands.apply_all:run',
            'kubepy-apply-one = kubepy.commands.apply_one:run',
        ],
    },
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
