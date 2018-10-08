#!/usr/bin/env bash

PATH=$PATH:/opt/conda/bin
cd /home/jovyan/project
jupyter-nbconvert --to slides --reveal-prefix reveal.js Presentation.ipynb