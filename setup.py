# import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

# classifiers = [
#     'Development Status :: 5 - Production/Experimental',
#     'Intended Audience :: PAT'
#     'Operating System :: Microsoft :: Windows :: Windows 10',
#     'License :: OSI Approved :: GNU GPLv3 License',
#     'Programming Language :: Python :: 3'
# ]

# setuptools.setup(
#     name="soniccontrol",
#     version="0.0.1",
#     author="Usepat G.m.b.H",
#     author_email="info@usepat.com",
#     maintainer="Ilja Golovanov",
#     maintainer_email="ilja.golovanov@usepat.com",
#     description="Lightweight GUI for controlling a sonicamp",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://bitbucket.org/stefangroup/soniccontrol_new.git",
#     packages=setuptools.find_packages(),
#     classifiers=classifiers,
#     install_requires=['pyserial', 'Pillow', 'pyglet', 'ttkbootstrap', 'matplotlib', 'sonicpackage']
# )


from cx_Freeze import setup,Executable
setup(
    name="soniccontrol",
    version=0.1,
    description="Lightweight GUI for controlling a sonicamp",
    executables=[Executable("main.py",base="Win32GUI")],
)
