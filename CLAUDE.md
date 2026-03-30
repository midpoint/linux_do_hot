# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository is a launcher script for running Claude Code with MiniMax's Anthropic-compatible API. It is not a software project with source code to develop — it is a single configuration script.

## Project Type

- Shell script that configures environment variables and launches Claude Code
- Uses MiniMax's API endpoint: `https://api.minimaxi.com/anthropic`
- Configured to use MiniMax-M2.7 model

## Usage

```bash
./m25.sh
```

This script:
1. Sets `ANTHROPIC_BASE_URL` to MiniMax's API endpoint
2. Sets `ANTHROPIC_AUTH_TOKEN` for authentication
3. Configures the default model to MiniMax-M2.7
4. Sets `API_TIMEOUT_MS=3000000` (5 minute timeout)
5. Disables non-essential traffic
6. Launches Claude Code in auto-mode

## Notes

- The repository contains no source code to build, test, or lint
- No package.json, Cargo.toml, or other project files exist here
