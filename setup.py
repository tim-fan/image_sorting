import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='image_sorting',  
    version='0.1',
    scripts=['pic_pick.py'] ,
    author="Tim Fanselow",
    author_email="",
    description="Tool for sorting images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tim-fan/image_sorting",
    packages=setuptools.find_packages(),
    classifiers=[],
    install_requires=[
        'dash',
        'dash_bootstrap_components',
        'sqlitedict',
        'pandas',
        'docopt',
    ],
 )