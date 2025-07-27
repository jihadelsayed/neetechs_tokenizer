# Placeholder
from setuptools import setup, find_packages

setup(
    name='neetechs_tokenizer',
    version='0.1.0',
    description='Arabic root-pattern tokenizer with grammar correction and translation',
    author='Sayed Jihad Al Sayed',
    author_email='jelsayed@uab.edu',
    packages=find_packages(),
    install_requires=[
        'transformers>=4.30.0',
        'torch',
        'arabic_reshaper',
        'python-bidi',
        'nltk',
        'tqdm',
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Natural Language :: Arabic',
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.8'
)
