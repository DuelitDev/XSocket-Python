from setuptools import find_packages, setup


with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="XSocket",
    version="0.0.1a",
    description="Cross-Language Socket",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DuelitDev",
    author_email="jyoon07dev@gmail.com",
    maintainer="DuelitDev",
    maintainer_email="jyoon07dev@gmail.com",
    url="https://github.com/DuelitDev/XSocket-Python",
    packages=find_packages(),
    python_requires=">=3.8",
    keywords=["socket"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    zip_safe=False
)


# python setup.py sdist
# python setup.py bdist_wheel
# twine upload ./dist/XSocket-x.x.x-py3-none-any.whl