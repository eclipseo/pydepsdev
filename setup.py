import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydepsdev",
    version="0.1.0",
    author="Robert-André Mauchin",
    author_email="zebob.m@gmail.com",
    description="A Python library for interacting with Deps.dev API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="api, deps.dev",
    url="https://github.com/eclipseo/pydepsdev",
    project_urls={
        "Bug Reports": "https://github.com/eclipseo/pydepsdev/issues",
    },
    license="ASL-2.0",
    license_files=["LICENSE"],
    packages=setuptools.find_packages(exclude=('tests', 'tests.*')),
    classifiers=[
        "Topic :: Software Development :: Libraries",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-asyncio",
            "aioresponses",
        ],
    },
)
