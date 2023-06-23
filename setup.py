import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
name = "To-DO-Liste",
version = "0.0.1",
author = "Feldhues Malte",
author_email = "malte.feldhues@gmx.de",
description = "To DO Liste fuers Studium",
long_description = long_description,
long_description_content_type = "text/markdown",
url = "https://github.com/FeldhuesM/To-DO-Liste",
project_urls = ,
license='MIT',
packages=['FLASK'],
python_requires >= "3.11",
)
