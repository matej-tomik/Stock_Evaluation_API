from setuptools import setup, find_packages


VERSION = "1.0.0"
DESCRIPTION = "api for stock analyser"


with open('requirements.txt', 'r', encoding='utf-16') as f:
    requirements = f.read()


setup(
    name='stock api',
    version=VERSION,
    author="Matěj Tomík",
    author_email="<mtomik.work@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    long_description=open('README.md').read(),
    url='https://github.com/matej-tomik/appi-for-stock-screen-analyser',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    keywords=["python", "stock analysis"],
    install_requires=requirements,
)
