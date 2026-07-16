from setuptools import setup, find_packages

setup(
    name="nova-sdk",
    version="0.1.0",
    description="NOVA — Digital Organism SDK. Greffe numérique, système immunitaire, mémoire SPINA.",
    author="0DATA Lab",
    author_email="lab@0data.fr",
    url="https://0data.fr",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0",
        "scapy>=2.5",
        "requests>=2.31",
        "cryptography>=41.0",
    ],
    entry_points={
        "console_scripts": [
            "nova=nova_cli:main",
        ],
    },
    python_requires=">=3.10",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Networking :: Monitoring",
    ],
)
