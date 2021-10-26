from setuptools import setup

setup(
    name='DataObj',
    version='1.0',
    author='Aaron Gerston (X-trodes LTD)',
    author_email='aarong@xtrodes.com',
    packages=['DataObj'],
    include_package_data=True,
    license='GNU GPLv3',
    long_description=open('README.md').read(),
    url="https://github.com/aarongerston/DataObj/",
    install_requires=open('requirements.txt').read()
)
