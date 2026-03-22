#!/usr/bin/env bash

echo 'Setup pipefail'

set -euo pipefail

echo 'Initializing release script'

# Get next version from conventional commits
NEXT_VERSION=$(uv run git-cliff --bumped-version)

if [ -z "$NEXT_VERSION" ]; then
    echo "No releasable commits found. Nothing to release."
    exit 0
fi


# Strip 'v' prefix for pyproject.toml
VERSION_NO_V="${NEXT_VERSION#v}"

echo "$NEXT_VERSION" > .version
echo "Next version: $NEXT_VERSION"

# Update version in pyproject.toml
sed -i "s/^version = \"[^\"]*\"/version = \"$VERSION_NO_V\"/" pyproject.toml

# Generate full changelog
uv run git-cliff --unreleased --bump --prepend CHANGELOG.md
uv run git-cliff --unreleased --bump  > NEXT_RELEASE.md

BLOG_POST="docs/docs/blog/posts/changelog-$NEXT_VERSION.md"

cat << EOF > $BLOG_POST
---
authors: 
    - souzo
categories:
    - announcement
    - release
tags:
    - announcement
    - release
date: $(date +%Y-%m-%d)
---

# Version $NEXT_VERSION changelog
EOF

cat NEXT_RELEASE.md >> $BLOG_POST

# Build distribution
uv build

# Stage and commit
git add pyproject.toml CHANGELOG.md $BLOG_POST
git commit -m "chore(release): $VERSION_NO_V"

# Create annotated tag
git tag -a "$NEXT_VERSION" -m "Release $NEXT_VERSION"

echo "Release $NEXT_VERSION prepared."
echo "Push with: git push && git push --tags"
