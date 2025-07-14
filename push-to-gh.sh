#!/bin/bash
cd ~/neuralnexus
git add .
git commit -m "${1:-Auto update from AI}"
git push origin main

