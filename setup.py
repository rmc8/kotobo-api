from typing import List
from setuptools import setup, find_packages


def get_requires() -> List[str]:
    with open("./requirements.txt") as f:
        txt: str = f.read()
        return txt.splitlines()


setup(
    name="kotobo-api",
    description="Working with the Kotobo app in Python",
    version="0.0.1",
    license="MIT",
    author="K",
    author_email="kmyashi@rmc-8.com",
    url="https://github.com/rmc8/kotobo-api",
    keywords=["Kotobo"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=get_requires(),
    # entry_points={
    #     "console_scripts": [
    #         "cmd = src.__main__:main",
    #     ]
    # },
)
