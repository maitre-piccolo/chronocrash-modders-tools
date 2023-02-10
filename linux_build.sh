#!/bin/bash
#build file for linux

#remove old builds
if [ -d "./dist" ];
then
rm -rf "./dist"
fi
if [ -d "./build" ];
then
rm -rf "./build"
fi

#run installer
pyinstaller --clean --name "chronocrash-modders-tools" ./cmt.py

#copy directories
if [ -d "./dist/chronocrash-modders-tools" ];
then
cp -r ./data ./common ./gui ./guilib ./icons ./other ./qutepart ./templates ./themes ./dist/chronocrash-modders-tools
fi
