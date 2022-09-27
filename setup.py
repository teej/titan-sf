from setuptools import find_packages, setup

setup(
    name="titan-sf",
    version="0.0.1",
    description="A package manager for Snowflake DB",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/teej/titan-sf",
    author="TJ Murphy",
    license="MIT",
    packages=find_packages(include=["titan", "titan.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: SQL",
        "Topic :: Database",
    ],
)
