try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements
from setuptools import find_packages
from setuptools import setup


def get_long_description():
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name='kubepy',
    version='1.12.2.dev0',
    description='Python wrapper on kubectl that makes deploying easy.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Social WiFi',
    author_email='it@socialwifi.com',
    url='https://github.com/socialwifi/kubepy',
    packages=find_packages(exclude=['tests']),
    install_requires=[str(ir.req) for ir in parse_requirements('base_requirements.txt', session=False)],
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
    ]
)
