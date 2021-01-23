setup(
    name="earthinversion",
    version="1.0.0",
    description="Go to earthinversion blog",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/earthinversion/",
    author="Utpal Kumar",
    author_email="office@earthinversion.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["pyqt"],
    include_package_data=True,
    install_requires=[
        "matplotlib",
        "PyQt5",
        "sounddevice",
    ],
    entry_points={"console_scripts": ["pyqt=gui.__main__:voicePlotter"]},
)