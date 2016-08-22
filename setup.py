from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(
    name='BitstampClient',
    version='2.1.0',
    description='Bitstamp API python implementation',
    packages=['bitstamp'],
    url='',
    license='MIT',
    author='Kamil Madac',
    author_email='kamil.madac@gmail.com',
    install_requires=['requests'],
    tests_require=['tox'],
    cmdclass={'test': Tox},
)
