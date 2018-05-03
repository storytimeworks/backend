from setuptools import setup

setup(
    name="Storytime",
    version="0.1",
    url="https://storytime.works",
    packages=["app"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
    )
