import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PrInge2021-schedule-parser-spanditime",
    version="0.0.1",
    author="Eugene Frolov",
    author_email="spanditime@gmail.com",
    description="Schedule parser made by Dubna university student",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spanditime/PrInge2021_schedule_parser",
    project_urls={
        "Bug Tracker": "https://github.com/spanditime/PrInge2021_schedule_parser/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GPL3 License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)