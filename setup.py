from setuptools import find_packages, setup

setup(
    name="neetechs_tokenizer",
    version="0.9.28",
    description="Conservative Arabic tokenizer and starter morphological analyzer",
    author="Jihad ElSayed",
    license="MIT",
    packages=find_packages(),
    package_data={"neetechs_tokenizer": ["data/*.json"]},
    include_package_data=True,
    install_requires=[],
    extras_require={"solver": ["numpy>=1.24"]},
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Natural Language :: Arabic",
        "Operating System :: OS Independent",
    ],
)
