#!/bin/sh
# ===================================================================
# Vendor-Agnostic Layout Check :: Read-Only, Needs Only git
# -------------------------------------------------------------------
# Proves that a repository follows the layout /vendor-agnostic builds:
# thin entry points, one routed AGENTS.md, shared skills and agents
# under .agents/, vendor folders that only point at them, and pages
# under docs/ whose links resolve. It runs on Linux, macOS, WSL and
# Git Bash, and writes nothing, not even a temporary file.
#
#   sh check.sh                  check every entry point that exists
#   sh check.sh claude copilot   also require these vendors
#   sh check.sh all              also require every vendor
#
# From PowerShell, let git start the shell it ships with:
#
#   git -c "alias.va=!sh '<folder>/scripts/check.sh'" va all
#
# Each line starts with PASS, WARN or FAIL. A FAIL must be fixed, and a
# WARN must be fixed or explained. Exit status: 0 without a FAIL, 1
# with one, 2 when the check cannot run.
#
# POSIX sh and awk on purpose: no arrays, no `local`, and no interval
# expressions, so dash, busybox, BSD awk and mawk all run it.
# ===================================================================

set -u
LC_ALL=C
export LC_ALL

ENTRY_LINES=14       # an entry point stays under 15 lines
AGENTS_LINES=200     # AGENTS.md is loaded on every request
AGENTS_BYTES=24000   # Antigravity cuts a rule file here; Codex stops at 32 KiB
GUARDRAILS=10
REGISTRY_ROWS=15     # past this, the registry moves to SKILLS.md
POINTER_LINES=25
DUPLICATE_CHARS=140

root=$(git rev-parse --show-toplevel 2> /dev/null) || {
    echo "check.sh: run it inside a git repository" >&2
    exit 2
}
cd "$root" || exit 2

wanted=" "
for argument in "$@"; do
    name=$(printf '%s' "$argument" | tr 'A-Z' 'a-z')
    case "$name" in
        all | claude | codex | copilot | cursor | gemini | opencode) wanted="$wanted$name " ;;
        *)
            echo "check.sh: unknown vendor '$argument' (claude, codex, copilot, cursor, gemini, opencode, all)" >&2
            exit 2
            ;;
    esac
done

# every file git tracks or would track; a file that only differs in
# case, or sits behind .gitignore, is not in this list
FILES=$(git -c core.quotepath=off ls-files -co --exclude-standard | sort -u)

pass() { printf 'PASS  %s\n' "$*"; }
warn() { printf 'WARN  %s\n' "$*"; }
fail() { printf 'FAIL  %s\n' "$*"; }

wants() {
    case "$wanted" in *" all "* | *" $1 "*) return 0 ;; *) return 1 ;; esac
}

lines() { awk 'END { print NR }' "$1"; }
bytes() { wc -c < "$1" | tr -d ' '; }

# "<line>TAB<text>" of a Markdown file, without fenced blocks and code spans
prose() {
    awk '
        { sub(/\r$/, "") }
        /^[ \t]*(```|~~~)/ { fence = !fence; next }
        fence { next }
        { gsub(/``[^`]*``/, ""); gsub(/`[^`]*`/, ""); print FNR "\t" $0 }
    ' "$1"
}

# every code span of a Markdown file, one per line
spans() {
    awk '
        { sub(/\r$/, "") }
        /^[ \t]*(```|~~~)/ { fence = !fence; next }
        fence { next }
        {
            text = $0
            while (match(text, /`[^`]+`/)) {
                print substr(text, RSTART + 1, RLENGTH - 2)
                text = substr(text, RSTART + RLENGTH)
            }
        }
    ' "$1"
}

# "<key>TAB<value>" for every top-level frontmatter key, with folded
# lines joined and quotes removed, so two spellings of one value match
frontmatter() {
    awk '
        function flush_key() {
            if (key == "") return
            gsub(/^[ \t]+|[ \t]+$/, "", value)
            if (value ~ /^".*"$/ || value ~ /^\047.*\047$/) value = substr(value, 2, length(value) - 2)
            gsub(/[ \t]+/, " ", value)
            print key "\t" value
            key = ""
        }
        { sub(/\r$/, "") }
        NR == 1 { if ($0 != "---") exit; next }
        $0 == "---" { exit }
        /^[A-Za-z_][A-Za-z0-9_-]*:/ {
            flush_key()
            key = $0
            sub(/:.*/, "", key)
            value = $0
            sub(/^[^:]*:[ \t]*/, "", value)
            if (value ~ /^[>|][+-]?[ \t]*$/) value = ""
            next
        }
        {
            gsub(/^[ \t]+|[ \t]+$/, "")
            if ($0 != "") value = (value == "" ? $0 : value " " $0)
        }
        END { flush_key() }
    ' "$1"
}

field() { frontmatter "$1" | awk -F '\t' -v key="$2" '$1 == key { print $2; exit }'; }

# lines whose text, outside code, holds an @path that a tool would expand
bare_imports() {
    prose "$1" | awk '
        { line = $1; sub(/^[0-9]+\t/, "") }
        /(^|[ \t(])@[A-Za-z0-9_.~\/-]/ { printf "%s ", line }
    '
}

imports_agents() {
    prose "$1" | awk '
        { sub(/^[0-9]+\t/, ""); gsub(/^[ \t]+|[ \t]+$/, "") }
        $0 == "@AGENTS.md" || $0 == "@./AGENTS.md" { found = 1 }
        END { exit !found }
    '
}

# "<mode> <blob>" of an exact path in the index, empty when untracked
indexed() {
    git -c core.quotepath=off ls-files -s -- "$1" | awk -F '\t' -v path="$1" '
        $2 == path { split($1, part, " "); print part[1], part[2]; exit }
    '
}

shared_skills() { printf '%s\n' "$FILES" | grep -E '(^|/)\.agents/skills/[^/]+/SKILL\.md$'; }
shared_agents() { printf '%s\n' "$FILES" | grep -E '(^|/)\.agents/agents/[^/]+\.md$'; }

registered() { grep -qF "$1" AGENTS.md 2> /dev/null || grep -qF "$1" SKILLS.md 2> /dev/null; }


check_agents_md() {
    if [ ! -s AGENTS.md ]; then
        fail "AGENTS.md is missing or empty, so every tool that reads it gets no instructions"
        return
    fi

    count=$(lines AGENTS.md)
    size=$(bytes AGENTS.md)
    if [ "$size" -gt "$AGENTS_BYTES" ]; then
        fail "AGENTS.md is $size bytes; keep it under $AGENTS_BYTES, where Antigravity cuts it"
    elif [ "$count" -gt "$AGENTS_LINES" ]; then
        warn "AGENTS.md has $count lines; over $AGENTS_LINES, move detail into docs/"
    else
        pass "AGENTS.md: $count lines, $size bytes"
    fi

    [ "$(head -n 1 AGENTS.md | tr -d '\r')" = "---" ] && fail "AGENTS.md opens with frontmatter, which tools read as text"
    grep -qE '^ *</?div' AGENTS.md && warn "AGENTS.md holds HTML wrappers, which cost tokens on every request"

    if tr '\r\n' '  ' < AGENTS.md | tr -s ' >' ' ' |
        grep -qF 'DO NOT read all files in `docs/` or `.agents/` upfront'; then
        pass "AGENTS.md tells the assistant not to read docs/ and .agents/ upfront"
    else
        fail "AGENTS.md lacks the sentence: DO NOT read all files in \`docs/\` or \`.agents/\` upfront"
    fi

    awk -v max="$GUARDRAILS" '
        { sub(/\r$/, "") }
        /^## / { inside = ($0 ~ /^## Universal Guardrails[ \t]*$/); if (inside) seen = 1; next }
        inside && (/^ ? ? ?[*+-] / || /^ ? ? ?[0-9]+\. /) { count++ }
        END {
            if (!seen) print "FAIL  AGENTS.md has no \"## Universal Guardrails\" section"
            else if (count > max) print "FAIL  AGENTS.md lists " count " guardrails; the limit is " max
            else print "PASS  AGENTS.md lists " count + 0 " guardrails"
        }
    ' AGENTS.md

    found=$(bare_imports AGENTS.md)
    [ -n "$found" ] && fail "AGENTS.md has an @path outside code on line(s) ${found% }: Claude Code and Copilot CLI load that file into every session"

    for file in AGENTS.md SKILLS.md; do
        [ -f "$file" ] || continue
        spans "$file" | sort -u | while IFS= read -r token; do
            target=${token%%#*}
            case "$target" in
                docs/*'<'* | .agents/*'<'* | docs/*'{'* | .agents/*'{'* | docs/*'*'* | .agents/*'*'*)
                    parent=${target%%[<\{\*]*}
                    parent=${parent%/*}
                    [ -d "$parent" ] || fail "$file routes to \`$token\`, but $parent/ does not exist"
                    ;;
                docs/* | .agents/*)
                    [ -e "$target" ] || fail "$file routes to \`$token\`, which does not exist"
                    ;;
            esac
        done
    done
}


check_pages() {
    for page in docs/README.md docs/ARCHITECTURE.md docs/PRODUCT.md docs/decisions/README.md; do
        printf '%s\n' "$FILES" | grep -qxF "$page" || warn "$page does not exist (or differs in case, or is ignored by git)"
    done

    # an archived page is kept for people to look up, so no route leads to it
    printf '%s\n' "$FILES" | grep -E '^docs/.*\.md$' | grep -v '^docs/archive/' | while IFS= read -r page; do
        [ -f "$page" ] || continue
        grep -qF "$page" AGENTS.md 2> /dev/null && continue
        folder=${page%/*}
        grep -qF "$folder/<" AGENTS.md 2> /dev/null && continue
        reached=
        while :; do
            index="$folder/README.md"
            if [ "$index" != "$page" ] && [ -f "$index" ] && grep -qF "${page#"$folder/"}" "$index"; then
                reached=1
                break
            fi
            [ "$folder" = docs ] && break
            folder=${folder%/*}
        done
        [ -n "$reached" ] || warn "$page is reachable neither from AGENTS.md nor from a docs index"
    done

    printf '%s\n' "$FILES" | grep -E '^docs/decisions/[^/]+\.md$' | while IFS= read -r page; do
        case "${page##*/}" in
            README.md | [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[a-z0-9]*.md) ;;
            [0-9][0-9][0-9][0-9]-[a-z]*.md) warn "$page keeps a number; a new record is named YYYY-MM-DD-<slug>.md" ;;
            *) fail "$page is not named YYYY-MM-DD-<slug>.md" ;;
        esac
    done
}


check_skills() {
    if ! printf '%s\n' "$FILES" | grep -qE '^\.agents/skills/'; then
        fail ".agents/skills/ holds no file git can track; add .agents/skills/.gitkeep"
    fi

    printf '%s\n' "$FILES" | grep -E '(^|/)\.agents/skills/[^/]+\.md$' | while IFS= read -r file; do
        fail "$file sits at the root of the skills folder, where OpenCode loads it as a skill"
    done

    printf '%s\n' "$FILES" | grep -E '(^|/)\.agents/skills/[^/]+/.+/SKILL\.md$' | while IFS= read -r file; do
        warn "$file is nested too deep; Antigravity reads one level, skills/<name>/SKILL.md"
    done

    shared_skills | while IFS= read -r file; do
        [ -f "$file" ] || continue
        folder=${file%/SKILL.md}
        folder=${folder##*/}
        name=$(field "$file" name)
        text=$(field "$file" description)
        extra=$(frontmatter "$file" | awk -F '\t' '
            $1 !~ /^(name|description|license|compatibility|metadata|allowed-tools)$/ { printf "%s ", $1 }
        ')
        if [ -z "$name" ] || [ -z "$text" ]; then
            fail "$file needs frontmatter with a name and a description"
        elif [ "$name" != "$folder" ]; then
            fail "$file is named '$name', but its folder is '$folder'"
        elif ! printf '%s' "$name" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$' || [ "${#name}" -gt 64 ]; then
            fail "$file: the name takes lower-case letters, digits and single hyphens, at most 64"
        elif [ "${#text}" -gt 1024 ]; then
            fail "$file: the description has ${#text} characters; the standard allows 1024"
        elif [ -n "$extra" ]; then
            warn "$file carries vendor keys (${extra% }); move them to the vendor's pointer file"
        else
            pass "skill $file"
        fi
        registered "$file" || fail "$file has no registry row in AGENTS.md or SKILLS.md"
    done
}


check_agents() {
    if ! printf '%s\n' "$FILES" | grep -qE '^\.agents/agents/'; then
        fail ".agents/agents/ holds no file git can track; add .agents/agents/.gitkeep"
    fi

    shared_agents | while IFS= read -r file; do
        [ -f "$file" ] || continue
        stem=${file##*/}
        stem=${stem%.md}
        name=$(field "$file" name)
        text=$(field "$file" description)
        extra=$(frontmatter "$file" | awk -F '\t' '
            $1 == "model" && $2 == "inherit" { next }
            $1 !~ /^(name|description)$/ { printf "%s ", $1 }
        ')
        if [ -z "$name" ] || [ -z "$text" ]; then
            fail "$file needs frontmatter with a name and a description (Antigravity loads every .md file here)"
        elif [ "$name" != "$stem" ]; then
            fail "$file is named '$name' in its frontmatter"
        elif [ -n "$extra" ]; then
            fail "$file carries vendor keys (${extra% }); Antigravity can hang on a tool name it does not know, so move them to the vendor's pointer file"
        else
            pass "agent $file"
        fi
        registered "$file" || fail "$file has no registry row in AGENTS.md or SKILLS.md"
    done
}


check_registry() {
    rows=$({ shared_skills; shared_agents; } | grep -c .)
    if [ -f SKILLS.md ]; then
        grep -qF 'SKILLS.md' AGENTS.md 2> /dev/null || fail "SKILLS.md exists, but AGENTS.md never points at it"
    elif [ "$rows" -gt "$REGISTRY_ROWS" ]; then
        warn "the registry has $rows rows; past $REGISTRY_ROWS it moves to SKILLS.md"
    fi
    if [ -f SKILL.md ] && [ -z "$(field SKILL.md name)" ]; then
        warn "the root SKILL.md has no frontmatter, so skill installers read it as a broken skill; rename it to SKILLS.md"
    fi
}


# entry <vendor> <file>: the size and the delegation of one entry point
entry() {
    if [ ! -f "$2" ]; then
        wants "$1" && fail "$2 is missing"
        return
    fi
    count=$(lines "$2")
    problem=
    [ "$count" -gt "$ENTRY_LINES" ] && problem="has $count lines (under 15 allowed)"
    if [ "$1" = copilot ]; then
        grep -qF 'AGENTS.md' "$2" || problem="${problem:+$problem, }does not name AGENTS.md"
        [ -n "$(bare_imports "$2")" ] && problem="${problem:+$problem, }holds an @path, which Copilot CLI inlines a second time"
    else
        imports_agents "$2" || problem="${problem:+$problem, }has no line that is exactly @AGENTS.md (or @./AGENTS.md)"
    fi
    if [ -n "$problem" ]; then
        fail "$2 $problem"
    else
        pass "$2: $count lines, delegates to AGENTS.md"
    fi
}


check_entries() {
    entry claude CLAUDE.md
    entry gemini GEMINI.md
    entry copilot .github/copilot-instructions.md

    if [ ! -f CLAUDE.md ] && [ -d .claude ]; then
        warn "there is a .claude/ folder but no CLAUDE.md; Claude Code reads AGENTS.md on its own only in some versions and sessions"
    fi
    [ -e AGENTS.override.md ] && fail "AGENTS.override.md replaces AGENTS.md for Codex"
    for file in .agents/AGENTS.md .agents/GEMINI.md .claude/CLAUDE.md .claude/AGENTS.md; do
        [ -e "$file" ] && warn "$file is loaded beside AGENTS.md; merge it and remove it"
    done
    if [ -f GEMINI.md ] && grep -qsF 'AGENTS.md' .gemini/settings.json; then
        warn ".gemini/settings.json also names AGENTS.md, so Gemini CLI loads it twice"
    fi
    for file in opencode.json opencode.jsonc .opencode/opencode.json .opencode/opencode.jsonc; do
        [ -f "$file" ] && grep -q '"docs/' "$file" &&
            warn "$file loads docs/ through \"instructions\" in every session; route to pages instead"
    done
}


# link_state <path> <target>: what a vendor folder is on disk and in git.
# Prints nothing for a healthy pointer folder, a verdict otherwise.
link_state() {
    set -- "$1" "$2" $(indexed "$1")
    mode=${3:-}
    if [ "$mode" = 120000 ]; then
        stored=$(git cat-file blob "$4" && printf x)
        if [ "$stored" != "$2x" ]; then
            fail "$1 is a tracked link whose stored target is not exactly '$2' (a trailing newline breaks it on Linux and macOS)"
        fi
        if [ -L "$1" ]; then
            if [ "$(readlink "$1")" = "$2" ]; then
                [ -d "$1/" ] && pass "$1 -> $2" || fail "$1 -> $2 does not resolve"
            else
                fail "DANGER: $1 is a junction or another link over a tracked symlink; git reset, stash, checkout and branch switches empty its target. Remove it with cmd: rmdir (never a recursive delete)"
            fi
        elif [ -d "$1" ]; then
            fail "$1 is a real directory where git tracks a symlink; committing now replaces the link by copies"
        elif [ -f "$1" ]; then
            fail "$1 was checked out as a text file, so Claude Code sees nothing here; use links=pointer, or enable Developer Mode and core.symlinks on this machine"
        else
            fail "$1 is tracked as a symlink but missing on disk; committing with -a would delete it"
        fi
    elif [ -L "$1" ]; then
        if [ "$(readlink "$1")" != "$2" ]; then
            git check-ignore -q -- "$1" &&
                warn "$1 is a per-machine link that git ignores; every other clone lacks it" ||
                fail "$1 is an untracked junction or link; git add would commit copies of $2"
        else
            warn "$1 is a symlink git does not track yet"
        fi
    elif [ ! -d "$1" ]; then
        printf 'ABSENT\n'
    fi
}


# pointer <kind> <shared file> <pointer file>
pointer() {
    if [ ! -f "$3" ]; then
        fail "$3 is missing, so Claude Code cannot find the $1 $2"
        return
    fi
    if [ "$(field "$3" name)" != "$(field "$2" name)" ] ||
        [ "$(field "$3" description)" != "$(field "$2" description)" ]; then
        fail "$3 and $2 differ in name or description"
    elif ! grep -qF "$2" "$3"; then
        fail "$3 does not point at $2"
    elif [ "$1" = agent ] && [ -n "$(field "$3" tools)" ] && ! field "$3" tools | grep -q 'Read'; then
        fail "$3 limits tools without Read, so the agent cannot open $2"
    elif [ "$(lines "$3")" -gt "$POINTER_LINES" ]; then
        warn "$3 has $(lines "$3") lines; a pointer holds frontmatter and one directive"
    else
        pass "$3 -> $2"
    fi
}


check_claude_folder() {
    [ -e CLAUDE.md ] || [ -d .claude ] || wants claude || return

    # every directory that holds a .agents/ folder, the repository root first
    { printf '\n'; { shared_skills; shared_agents; } | sed 's|\.agents/.*$||'; } | sort -u | while IFS= read -r prefix; do
        for kind in skills agents; do
            path="${prefix}.claude/$kind"
            state=$(link_state "$path" "../.agents/$kind")
            case "$state" in
                '' | ABSENT) ;;   # a pointer folder, or none at all: check every pointer
                *) printf '%s\n' "$state"; continue ;;
            esac
            if [ "$kind" = skills ]; then
                shared_skills | while IFS= read -r file; do
                    [ "${file%%.agents/*}" = "$prefix" ] || continue
                    name=${file%/SKILL.md}
                    pointer skill "$file" "$path/${name##*/}/SKILL.md"
                done
            else
                shared_agents | while IFS= read -r file; do
                    [ "${file%%.agents/*}" = "$prefix" ] || continue
                    pointer agent "$file" "$path/${file##*/}"
                done
            fi
        done
    done

    printf '%s\n' "$FILES" | grep -E '(^|/)\.claude/(skills/[^/]+/SKILL|agents/[^/]+)\.md$' | while IFS= read -r file; do
        [ -f "$file" ] || continue
        spans "$file" | grep -E '(^|/)\.agents/(skills|agents)/.+\.md$' | while IFS= read -r target; do
            [ -f "$target" ] || fail "$file points at $target, which does not exist"
        done
    done
}


check_links() {
    printf '%s\n' "$FILES" | awk '
        function decode(text,   out, at, hex, code) {
            out = ""
            while ((at = index(text, "%")) > 0) {
                hex = toupper(substr(text, at + 1, 2))
                if (hex ~ /^[0-9A-F][0-9A-F]$/) {
                    code = (index("0123456789ABCDEF", substr(hex, 1, 1)) - 1) * 16
                    code += index("0123456789ABCDEF", substr(hex, 2, 1)) - 1
                    out = out substr(text, 1, at - 1) sprintf("%c", code)
                    text = substr(text, at + 3)
                } else {
                    out = out substr(text, 1, at)
                    text = substr(text, at + 1)
                }
            }
            return out text
        }
        function resolve(path,   total, part, i, depth, out) {
            total = split(path, part, "/")
            depth = 0
            for (i = 1; i <= total; i++) {
                if (part[i] == "" || part[i] == ".") continue
                if (part[i] == "..") {
                    if (depth == 0) return "outside"
                    depth--
                    continue
                }
                stack[++depth] = part[i]
            }
            out = ""
            for (i = 1; i <= depth; i++) out = out (i > 1 ? "/" : "") stack[i]
            return out
        }
        function look(file, line, target,   base, path) {
            if (target ~ /^</) { sub(/^</, "", target); sub(/>.*$/, "", target) }
            else sub(/[ \t].*$/, "", target)
            sub(/[#?].*$/, "", target)
            if (target == "" || target ~ /^[A-Za-z][A-Za-z0-9+.-]*:/ || target ~ /^\/\//) return
            target = decode(target)
            base = file
            if (!sub(/\/[^\/]*$/, "/", base)) base = ""
            path = resolve(target ~ /^\// ? target : base target)
            if (path == "" || path == "outside" || path in known) return
            if (file ~ /^docs\/archive\//) print "ARCHIVED\t" file ":" line "\t" path
            else if (tolower(path) in lower) print "FAIL  " file ":" line " links to " path ", but git has " lower[tolower(path)]
            else print "MISSING\t" file ":" line "\t" path
        }
        {
            known[$0] = 1
            lower[tolower($0)] = $0
            folder = $0
            while (sub(/\/[^\/]*$/, "", folder)) { known[folder] = 1; lower[tolower(folder)] = folder }
            if ($0 ~ /^(AGENTS|SKILLS|CLAUDE|GEMINI|README)\.md$/ || $0 == ".github/copilot-instructions.md" ||
                $0 ~ /^docs\/.*\.md$/ || $0 ~ /(^|\/)\.agents\/.*\.md$/) scope[++files] = $0
        }
        END {
            for (n = 1; n <= files; n++) {
                fence = 0
                line = 0
                while ((getline text < scope[n]) > 0) {
                    line++
                    sub(/\r$/, "", text)
                    if (text ~ /^[ \t]*(```|~~~)/) { fence = !fence; continue }
                    if (fence) continue
                    gsub(/``[^`]*``/, "", text)
                    gsub(/`[^`]*`/, "", text)
                    while (match(text, /\]\([^)]*\)/)) {
                        look(scope[n], line, substr(text, RSTART + 2, RLENGTH - 3))
                        text = substr(text, RSTART + RLENGTH)
                    }
                }
                close(scope[n])
            }
            print "PASS  links: read " files + 0 " Markdown files"
        }
    ' | while IFS='	' read -r verdict where path; do
        case "$verdict" in
            MISSING) [ -e "$path" ] || fail "$where links to $path, which does not exist" ;;
            ARCHIVED) [ -e "$path" ] || warn "$where (archived) links to $path, which does not exist; re-point it if the move broke it" ;;
            *) printf '%s\n' "$verdict" ;;
        esac
    done
}


check_duplicates() {
    printf '%s\n' "$FILES" | awk -v least="$DUPLICATE_CHARS" '
        function keep(   key) {
            if (length(text) >= least) {
                key = tolower(text)
                gsub(/[`*_]/, "", key)
                if (key in first && first[key] != file) {
                    print "WARN  the same paragraph is in " first[key] ":" place[key] " and " file ":" start
                } else if (!(key in first)) {
                    first[key] = file
                    place[key] = start
                }
            }
            text = ""
        }
        $0 ~ /^docs\/archive\// { next }
        $0 ~ /^(AGENTS|SKILLS|CLAUDE|GEMINI|README|CONTRIBUTING)\.md$/ || $0 == ".github/copilot-instructions.md" ||
        $0 ~ /^docs\/.*\.md$/ || $0 ~ /(^|\/)\.(agents|claude)\/.*\.md$/ || $0 ~ /\/README\.md$/ { scope[++files] = $0 }
        END {
            for (n = 1; n <= files; n++) {
                file = scope[n]
                line = 0
                fence = 0
                head = 0
                text = ""
                while ((getline row < file) > 0) {
                    line++
                    sub(/\r$/, "", row)
                    if (line == 1 && row == "---") { head = 1; continue }
                    if (head) { if (row == "---") head = 0; continue }
                    if (row ~ /^[ \t]*(```|~~~)/) { keep(); fence = !fence; continue }
                    if (fence) continue
                    if (row ~ /^[ \t]*$/ || row ~ /^[ \t]*[|#<>]/) { keep(); continue }
                    if (row ~ /^[ \t]*([*+-]|[0-9]+\.) /) { keep(); sub(/^[ \t]*([*+-]|[0-9]+\.) (\[[ xX]\] )?/, "", row) }
                    gsub(/^[ \t]+|[ \t]+$/, "", row)
                    gsub(/[ \t]+/, " ", row)
                    if (text == "") start = line
                    text = (text == "" ? row : text " " row)
                }
                keep()
                close(file)
            }
        }
    '
}


check_placeholders() {
    printf '%s\n' "$FILES" |
        grep -E '^(AGENTS|SKILLS|CLAUDE|GEMINI)\.md$|^\.github/copilot-instructions\.md$|^docs/.*\.md$|(^|/)\.agents/(skills/[^/]+/SKILL|agents/[^/]+)\.md$' |
        while IFS= read -r file; do
            [ -f "$file" ] || continue
            case "$file" in */*) strict=0 ;; *) strict=1 ;; esac
            found=$(awk -v strict="$strict" '
                { sub(/\r$/, "") }
                /^[ \t]*(```|~~~)/ { fence = !fence; next }
                fence { next }
                /\{\{ OPTIONAL/ || /^\}\}$/ { printf "%s ", FNR; next }
                strict && /\{(command|skill|role|component|group|name|page|path|source|link|code path|code dir)\}/ { printf "%s ", FNR; next }
                { gsub(/`[^`]*`/, "") }
                /\{[A-Z][A-Za-z-]*( [^{}]*)?\}/ { printf "%s ", FNR }
            ' "$file")
            [ -n "$found" ] && fail "$file still holds template text on line(s) ${found% }"
        done
}


check_repository() {
    for path in AGENTS.md SKILLS.md CLAUDE.md GEMINI.md .github/copilot-instructions.md .agents/skills \
        .agents/agents .claude/skills .claude/agents docs docs/README.md docs/decisions; do
        if [ -e "$path" ] && git check-ignore -q -- "$path"; then
            fail "$path is ignored by git: $(git check-ignore -v -- "$path" | awk -F '\t' 'NR == 1 { print $1 }')"
        fi
    done

    for path in .claude/docs .cursorrules .windsurfrules .clinerules AGENT.md docs/adr docs/adrs docs/PRD.md; do
        printf '%s\n' "$FILES" | grep -qE "^$(printf '%s' "$path" | sed 's/\./\\./g')(/|$)" &&
            warn "$path is an old location; its content belongs in the layout"
    done

    printf '%s\n' "$FILES" | awk '
        { key = tolower($0); if (key in seen) print "FAIL  " seen[key] " and " $0 " differ only in case, which breaks Windows and macOS"; seen[key] = $0 }
    '
}


report=$(
    check_agents_md
    check_registry
    check_skills
    check_agents
    check_entries
    check_claude_folder
    check_pages
    check_links
    check_duplicates
    check_placeholders
    check_repository
)
printf '%s\n' "$report"
failures=$(printf '%s\n' "$report" | grep -c '^FAIL')
warnings=$(printf '%s\n' "$report" | grep -c '^WARN')
printf '\n%s failure(s), %s warning(s) in %s\n' "$failures" "$warnings" "$root"
[ "$failures" -eq 0 ]
