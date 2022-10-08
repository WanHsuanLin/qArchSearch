import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qArchSearch",
    version="1.0.2",
    author="Wan-Hsuan Lin",
    author_email="wanhsuanlin@ucla.edu",
    description="qArchSearch: A Domain-Secific Quantum Archticture Optimization Tool",
    url="https://github.com/WanHsuanLin/qArchSearch",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ),
)
