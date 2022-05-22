import setuptools


with open("README.md", "r", encoding="utf8") as fp:
    long_description = fp.read()


setuptools.setup(
    name="im-remind",
    version="1.0.2",
    author="leonardodalink",
    author_email="ayajilin@pm.me",
    description="A simple tool for reminding you on IM.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leonardodalinky/im-remind",
    project_urls={
        "Tracker": "https://github.com/leonardodalinky/im-remind/issues",
        "Source": "https://github.com/leonardodalinky/im-remind",
        # "Documentation": "https://packaging.python.org/tutorials/distributing-packages/",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    install_requires=[
        "requests>=2",
        "PyYAML",
    ],
    scripts=["scripts/im-remind"],
    keywords="qq telegram",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
