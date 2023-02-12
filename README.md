# ChronoCrash-Modders-Tools

Hey guys,

OpenBOR Stats is a very useful piece of software for a lot of us, but it is getting a bit old, and MatMan, its creator, seems to have quit.

So, long story short, I just started to develop a new project for OpenBOR / ChronoCrash modding.

Here's what I have in mind right now regarding features & goals :

- An OpenBOR Stats like "entity editor", but one that strictly preserves plain text format, indentation, comments, scripts and such. For me it is the main issue with OpenBORStats (to the point that I never actually save a file with it), it is a not a plain text editor and can mess up text files due to how it handle them (it converts your files and completely rewrite them).
- A rock solid code-edit style editor for all the other text stuff (levels, scripts, ...)

- Cross-platform, built around Python3 and Qt5
- Will be updated to support future syntax (if and when the ChronoCrash engine happens)
- The source code will be available so that other people can contribute and most importantly so that the project can be reprised where it left by someone else if I were to disappear !

So I certainly don't plan to recreate everything OpenBOR Stats do (at least right now and myself) especially as my time is quite limited these days.

It is still in its early stages (started it last week) but development is going well and I'll probably release an Alpha version with a basic "Entity Editor" in the coming week.

Of course if anyone has interesting suggestions for this tool, I'm all ears.

## Running on Linux

Just download the source code and run "python cmt.py".

You'll need python3, Qt5 for python3 and pillow (or PIL).

## Building on Linux

Make sure to install python3, pyinstaller and Qt5. Run the linux_build.sh file and wait for the application to compile, when finished there will be a folder "dist/chronocrash-modders-tools" this will contain the application.
