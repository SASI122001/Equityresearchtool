from setuptools import setup, find_packages

setup(
    name="equityresearchtool",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yfinance",
        "pandas",
        "numpy",
        "matplotlib",
        "scipy",
        "openai",
        "python-dotenv",
        "tabulate",
    ],
    entry_points={
        "console_scripts": [
            "equityresearch=main:cli",
        ]
    },
)
