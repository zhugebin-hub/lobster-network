from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lobster-network",
    version="0.4.1",
    author="诸葛斌, 信电大虾, 诸葛马",
    author_email="zhugebin@zjgsu.edu.cn",
    description="小龙虾网络：对话即创造的多Agent协作网络",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhugebin-hub/lobster-network",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.28.0",
        "paramiko>=3.0.0",
    ],
    extras_require={
        "full": [
            "playwright>=1.40.0",
            "python-pptx>=0.6.21",
            "python-docx>=0.8.11",
            "Pillow>=9.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
