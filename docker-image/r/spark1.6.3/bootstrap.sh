#!/bin/bash
IFS='.' read -r -a baseVersion << $1
curl -O https://cran.r-project.org/src/base/R-${baseVersion[0]}/R-$1.tar.gz \