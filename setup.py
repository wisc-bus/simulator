import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    install_requires = fh.read()
    install_requires = install_requires.split("\n")
    install_requires = list(filter(lambda x: x[0] != "#", install_requires))

setuptools.setup(
    name="SCanalyzer",
    version="0.0.2",
    author="Chang Xu",
    author_email="cxu249@wisc.edu",
    description="Service Cube Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wisc-bus/simulator",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python :: 3",
    ],
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
