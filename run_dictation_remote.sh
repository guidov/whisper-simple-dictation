#!/bin/bash
script_dir="$(dirname "$(realpath "$0")")"
cd "$script_dir"

python dictation.py remote "$@" --use-groq
#python dictation.py remote "$@" --use-oai


