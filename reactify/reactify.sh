#!/bin/bash

mkdir -p output
if [ -d "output/$2" ]; then
    echo "Project $1 already exists."
    exit
fi
cd output
react-native init $2

cd ..
cp js/$1/index.android.js output/$2
# js/$1/index.ios.js 

cd output/$2

