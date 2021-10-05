from typing import List
from setuptools import setup, find_packages


def get_requires() -> List[str]:
    with open("./requirements.txt") as f:
        txt: str = f.read()
        return txt.splitlines()


setup(
    name="",
    description="",
    version="",
    license="MIT",
    author="",
    author_email="",
    url="",
    keywords=[],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=get_requires(),
    # entry_points={
    #     "console_scripts": [
    #         "cmd = src.__main__:main",
    #     ]
    # },
)
