import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

classifiers = [
    'Development Status :: 5 - Production/Experimental',
    'Intended Audience :: PAT'
    'License :: OSI Approved :: GNU GPLv3 License',
    'Programming Language :: Python :: 3'
]

setuptools.setup(
    name="soniccontrol",
    version="0.1.70",
    author="Usepat G.m.b.H",
    author_email="info@usepat.com",
    maintainer="Ilja Golovanov",
    maintainer_email="ilja.golovanov@usepat.com",
    description="Lightweight GUI for controlling a sonicamp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/usepat/soniccontrol",
    packages=setuptools.find_packages(),
    classifiers=classifiers,
    package_dir={'': 'src'},
    install_requires=['pyserial', 'Pillow', 'pyglet', 'ttkbootstrap', 'matplotlib', 'sonicpackage']
)
