#!/bin/bash
set -x

pwd ls -lah
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

##############
# BUILD DOCS #
##############

# Python Sphinx, configured with docs/source/conf.py
# See https://www.sphinx-doc.org/
make clean
SPHINXOPTS="-t github" make html

#######################
# Update GitHub Pages #
#######################

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"

docroot=`mktemp -d`
rsync -av "docs/build/html/" "${docroot}/"

pushd "${docroot}"

git init
git remote add deploy "https://token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git checkout -b gh-pages

# instead of adding .nojekyll, we have set the layout to null, so we can use
# github pages' jekyll plugins

# Add add jekyll config
cat > _config.yml <<EOF
title: Odoo Business Relationship Types Documentation
description: Manage business relationship types, e.g. B2B, B2C and Internal on contact level
baseurl: "/odoo_business_relationships" # the subpath of your site, e.g. /blog
url: "https://ayudoo.github.io" # the base hostname & protocol for your site, e.g. http://example.com

permalink: pretty
plugins:
  - jekyll-seo-tag

include:
  - _static
EOF

# Add README
cat > README.md <<EOF
# README for the GitHub Pages Branch
This branch is simply a cache for the website served from https://ayudoo.github.io/odoo_business_relationships/,
and is not intended to be viewed on github.com.

For more information on how this site is built using Sphinx, Read the Docs, and GitHub Actions/Pages, see:
 * https://www.docslikecode.com/articles/github-pages-python-sphinx/
 * https://tech.michaelaltfield.net/2020/07/18/sphinx-rtd-github-pages-1
EOF

# Copy the resulting html pages built from Sphinx to the gh-pages branch
git add .

# Make a commit with changes and any new files
msg="Updating Docs for commit ${GITHUB_SHA} made on `date -d"@${SOURCE_DATE_EPOCH}" --iso-8601=seconds` from ${GITHUB_REF} by ${GITHUB_ACTOR}"
git commit -am "${msg}"

# overwrite the contents of the gh-pages branch on our github.com repo
git push deploy gh-pages --force

popd # return to main repo sandbox root

# exit cleanly
exit 0
