#!/bin/bash

mkdir -p output
if [ -d "output/$2" ]; then
    echo "Project $1 already exists."
    exit
fi
cd output
react-native init $2

cd output
cp js/$1/index.android.js js/$1/index.ios.js output/$2

cd output/$2

