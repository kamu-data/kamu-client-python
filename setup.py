#!/usr/bin/env python3
from setuptools import setup


def parse_version(path: str) -> str:
    with open(path, "r") as f:
        loc = locals()
        exec(f.read(), None, loc)
        return loc["VERSION"]


def parse_requirements(filename: str) -> str:
    with open(filename, "r") as f:
        requirements = f.read().splitlines()

    requirements = [
        req.strip() for req in requirements if req.strip() and not req.startswith("#")
    ]
    return requirements


def parse_markdown(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def setup_package():
    setup(
        name="kamu",
        version=parse_version("kamu/_version.py"),
        author="Kamu Data Inc.",
        author_email="dev@kamu.dev",
        maintainer="Kamu Data Inc.",
        maintainer_email="dev@kamu.dev",
        url="https://github.com/kamu-data/kamu-client-python",
        description="Kamu client library - decentralized data supply chain.",
        license="Apache 2.0",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Software Development :: Libraries",
        ],
        keywords="kamu, opendatafabric, data, decentralized, web3, AI, ML",
        long_description=parse_markdown("README.md"),
        long_description_content_type="text/markdown",
        packages=["kamu"],
        install_requires=parse_requirements("requirements.in"),
        extras_require={"test": parse_requirements("requirements.test.in")},
        python_requires=">=3.8",
        platforms=["Any"],
    )


if __name__ == "__main__":
    setup_package()
