#!/usr/bin/env bash

rsync -avhP --no-perms --no-owner --no-group --delete ./datadata-api ~/.claude/skills/
