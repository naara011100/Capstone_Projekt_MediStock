#!/usr/bin/env bash
# setup-skills.sh
#
# Creates symlinks so Claude Code (.claude/skills) and Agent-framework
# compatible tools (.agents/skills) both resolve to the single source-of-truth
# skills/ folder in the project root.
#
# Usage:
#   bash scripts/setup-skills.sh
#
# Windows note: Git Bash or WSL required.  Native PowerShell alternative:
#   New-Item -ItemType Junction -Path .claude\skills  -Target (Resolve-Path skills)
#   New-Item -ItemType Junction -Path .agents\skills  -Target (Resolve-Path skills)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${REPO_ROOT}/skills"

if [ ! -d "${SKILLS_DIR}" ]; then
  echo "ERROR: skills/ directory not found at ${SKILLS_DIR}" >&2
  exit 1
fi

# ── .claude/skills ────────────────────────────────────────────────────────────
CLAUDE_DIR="${REPO_ROOT}/.claude"
mkdir -p "${CLAUDE_DIR}"

if [ -L "${CLAUDE_DIR}/skills" ]; then
  echo "Updating symlink: .claude/skills"
  rm "${CLAUDE_DIR}/skills"
elif [ -d "${CLAUDE_DIR}/skills" ]; then
  echo "ERROR: .claude/skills exists as a real directory; remove it first." >&2
  exit 1
fi
ln -s "${SKILLS_DIR}" "${CLAUDE_DIR}/skills"
echo "  Created: .claude/skills -> ${SKILLS_DIR}"

# ── .agents/skills ────────────────────────────────────────────────────────────
AGENTS_DIR="${REPO_ROOT}/.agents"
mkdir -p "${AGENTS_DIR}"

if [ -L "${AGENTS_DIR}/skills" ]; then
  echo "Updating symlink: .agents/skills"
  rm "${AGENTS_DIR}/skills"
elif [ -d "${AGENTS_DIR}/skills" ]; then
  echo "ERROR: .agents/skills exists as a real directory; remove it first." >&2
  exit 1
fi
ln -s "${SKILLS_DIR}" "${AGENTS_DIR}/skills"
echo "  Created: .agents/skills -> ${SKILLS_DIR}"

echo ""
echo "Done.  Both agent frameworks now resolve skills/ from the project root."
