#!/bin/bash


if [ $# -eq 0 ]; then
  echo "Usage: $0 <commit-message>"
  exit 1
fi

# Store commit message from command line argument
commit_message="$1"

# Perform git add
git add .

# Perform git commit with the provided commit message
git commit -m "$commit_message"

# Perform git push
git push
