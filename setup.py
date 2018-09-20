from setuptools import setup
from setuptools import find_packages
setup(
    name="logagg_utils",
    version="0.5.0",
    description="Commonly re-used logic for loggag kept in one library",
    keywords="logagg-utils",
    author="Deep Compute, LLC",
    author_email="contact@deepcompute.com",
    url="https://github.com/deep-compute/logagg/logagg-utils",
    license='MIT',
    dependency_links=[
        "https://github.com/deep-compute/logagg/logagg-utils",
    ],
    install_requires=[
        "deeputil==0.2.5",
        "six==1.11.0",
        "tornado==5.1.1",
        "basescript==0.2.6",
    ],
    packages=find_packages('.'),
    include_package_data=True,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    test_suite='test.suite_maker',
    entry_points={
        "console_scripts": [
            "nsq-api = logagg_utils:main",
            ]
        }
)
