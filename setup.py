"""
PyWebHooks Setup
"""

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


def read(relative):
    """
    Read file contents and return a list of lines.
    ie, read the VERSION file
    """
    contents = open(relative, 'r').read()
    return [l for l in contents.split('\n') if l != '']

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='pywebhooks',
    url='https://github.com/chadlung/pywenhooks',
    keywords=['WebHooks'],
    long_description=readme,
    version=read('VERSION')[0],
    description='WebHooks Service',
    author='Chad Lung',
    author_email='chad.lung@gmail.com',
    tests_require=read('./test-requirements.txt'),
    install_requires=read('./requirements.txt'),
    test_suite='nose.collector',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux'
    ],
    packages=find_packages(exclude=['ez_setup'])
)
