"""Installation facility for the tutor-contrib-openstack package."""
import io
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def load_readme():
    """Load the README.md file and return its contents as a string."""
    with io.open(os.path.join(HERE, "README.md"), "rt", encoding="utf8") as f:
        return f.read()


setup(
    name="tutor-contrib-openstack",
    use_scm_version=True,
    url="https://github.com/hastexo/tutor-contrib-openstack",
    project_urls={
        "Code": "https://github.com/hastexo/tutor-contrib-openstack",
        "Issue tracker": "https://github.com/hastexo/tutor-contrib-openstack/issues",  # noqa: E501
    },
    license="AGPLv3",
    author="Florian Haas",
    description="openstack plugin for Tutor",
    long_description=load_readme(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "tutor <17, >=14.0.0",
        "openstacksdk",
    ],
    setup_requires=['setuptools-scm<7'],
    entry_points={
        "tutor.plugin.v1": [
            "openstack = tutoropenstack.plugin"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
