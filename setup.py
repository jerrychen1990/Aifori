#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/03/11 14:22:25
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''

import sys

from setuptools import find_packages, setup

from snippets.utils import get_latest_version, get_next_version, read2list


def get_install_req():
    req = read2list("requirements.txt")
    return req


if __name__ == "__main__":
    name = "aifori"
    if len(sys.argv) >= 4 and sys.argv[-1].startswith("v"):
        version = sys.argv.pop(-1)
    else:
        latest_version = get_latest_version(name)
        version = get_next_version(latest_version)

    print(f"building {name} with version: {version}")
    install_req = get_install_req()
    print(f"install_req: {install_req}")
    setup(
        name=name,
        version=version,
        install_requires=install_req,
        packages=find_packages(exclude=['tests*']),
        package_dir={"": "."},
        package_data={},
        url='https://github.com/jerrychen1990/Aifori',
        license='MIT',
        author='Chen Hao',
        author_email='jerrychen1990@gmail.com',
        zip_safe=True,
        description='aifori',
        long_description="aifori"
    )
