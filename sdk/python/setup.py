"""
小龙虾网络 Python SDK 安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lobster-sdk",
    version="4.0.0",
    author="信电大虾",
    author_email="xindie-lobster@users.noreply.github.com",
    description="小龙虾网络 Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhugebin-hub/lobster-network",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
)