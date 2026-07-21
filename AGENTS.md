**See also**: [REPORULES.md](../REPORULES.md) — multi-machine sync, git identity, PAT handling, and new-repo bootstrap.

# AGENTS.md — Worker Contract for Sword-jin_PWA (SwordJin)

*This file is the verifier contract for any AI agent working in this repo. Read it before starting. Follow it always. Violations are regressions.*

*Repo facts: Mobile-first action RPG built in Godot 4.4.1 (GL Compatibility), deployed as a PWA. Stack: GDScript. The "test" gate is a Godot headless smoke test across all 30 chapters. Default branch: `main`. Git identity: `Henrik Kirk <285947470+KirkForge@users.noreply.github.com>`.*

---

## ⚠️ Mandatory Rules — Read Before Editing (preserved)

- **Never commit**: `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `*.pyc`, `dist/`, `build/`, `.next/`, `coverage/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.tox/`, `.DS_Store`, `*.log`, `.env`, `*.pem`, `*.key`
- **Always pull before work, push after work**
- **Git identity**: `Henrik Kirk <285947470+KirkForge@users.noreply.github.com>`
- **Commit format**: `type(scope): message` — feat, fix, docs, refactor, test, chore, wip
- **Pre-push CI**: `ci-cleandev` hooks block pushes on failure. Fix, don't bypass.
- **Headless smoke test**: `bash scripts/ci/smoke_test.sh`
- **Browser PWA smoke test**: `python3 scripts/ci/browser_smoke.py` (requires `playwright`)

## Testing (preserved)

- **Headless smoke test**: `bash scripts/ci/smoke_test.sh`
- **Browser PWA smoke test**: `python3 scripts/ci/browser_smoke.py` (requires `playwright`)
- **Live PWA URL**: deployed automatically from `main` via GitHub Pages (enable Pages source = GitHub Actions in repo settings).

## Project Rules (preserved)

- Keep files minimal and clean
- Don't add generated or dependency files

## Before Editing (preserved)

1. `git pull`
2. Check `.gitignore` — don't stage ignored files
3. Check this file for project-specific rules

## Before Committing (preserved)

1. `git status --short` — review staged files
2. No secrets, no generated files, no cache directories
3. `git diff --cached` — verify actual content
4. Let pre-push CI pass before pushing

---

## 🔒 Secure-Defaults Checklist (Definition of Done) (preserved)

> **The rule:** The secure state is the DEFAULT. Opening it up is an EXPLICIT, LOGGED, opt-in — never the fallback.

### Network binding
- [ ] Servers bind `127.0.0.1` by default. Non-loopback requires explicit flag/env AND auth enabled.
- [ ] Non-loopback bind logs a startup WARNING naming the exposure.
- [ ] CORS / allowed-hosts default to an explicit allowlist, never `["*"]`.

### Secrets
- [ ] No secret has a usable default value. Missing secret in production → refuse to boot (`exit 1`).
- [ ] Empty-string / placeholder secrets are never a valid signing key, even in dev. Generate random per-process secret if none supplied (+ warning).
- [ ] No secret value is written into generated artifacts (systemd units, configmaps, scripts).
- [ ] Secrets come from env or a secret manager — never a committed file. `*token*.json`, `credentials*.json` etc. are gitignored.

### Comparisons (constant-time)
- [ ] Every secret / token / signature / hash comparison uses constant-time compare (`hmac.compare_digest` / `crypto.timingSafeEqual`), never `==` / `!==`.
- [ ] `grep -rEn '(sig|hmac|token|secret|hash|key)\b.*(==|!=|!==)' src/` returns nothing that compares a secret.

### Allowlists / deny-by-default
- [ ] An empty allowlist means DENY, never ALLOW-ALL.
- [ ] Filesystem paths from tool/API input are confined to a configured root by default; arbitrary paths require explicit opt-in.
- [ ] Command execution uses argv arrays, never `shell=True` / string interpolation. Raw-shell paths gated behind `ALLOW_UNSAFE_*=1`, default off.

### Multi-tenant isolation
- [ ] Every shared store (sessions, cache, files, memory, routing) is keyed by `tenant_id`, not a global namespace.
- [ ] List/enumerate endpoints scope results to the calling tenant.
- [ ] Identity (owner/role/tenant) is derived from the authenticated session/token, never from the request body.
- [ ] At least one test asserts tenant A cannot read/modify tenant B's data.

### Authorization (not just authentication)
- [ ] Every protected endpoint calls BOTH authn (who are you) AND authz (are you allowed).
- [ ] New endpoints are deny-by-default — added to the authz table, not left to fall through.

### Sandbox / untrusted execution
- [ ] Child processes get an explicit env allowlist, not `{...process.env}` inheritance.
- [ ] For untrusted/model-generated code, real isolation (container/microVM/namespaces + rlimits + no-new-privs) is the DEFAULT path; bare-host "constrained" is opt-in with a warning.
- [ ] Isolation claims in README match what the code enforces. No "kernel-enforced"/"enterprise-grade" unless it is.

### Claims vs reality
- [ ] README maturity label matches code reality.
- [ ] Threat model is documented for anything that takes untrusted input.
- [ ] No dead code that implies a capability the product doesn't have.

---

## 1. Plan mode default
- Before writing any code, write a plan to `workplan.md` (gitignored). The plan must list the files you will touch (full paths), state the root cause you're fixing (not the symptom), and state the gate you'll run to verify.
- Check `workplan.md` before implementation. Check `lessons.md` for lessons from prior sessions. Check `state.md` for current repo state.
- If the task is unclear, say so in `workplan.md` and escalate — do not guess.

## 2. Subagent strategy
- For complex multi-step tasks, break them into subtasks and dispatch subagents.
- Each subtask must have a clear scope (files to touch), a gate (command to run), and a done-condition.
- Do not dispatch a subagent for a task you can do in <5 minutes yourself.

## 3. Self-improving loop
- At session end, write `lessons.md` (gitignored) with: what you learned about this codebase (conventions, gotchas, patterns), what you tried that didn't work and why, what you'd do differently next time.
- Update `state.md` (tracked) with: what changed this session, what's pending, what's blocked.
- Lessons from `lessons.md` that are permanent conventions get folded into this `AGENTS.md` file — so the next worker reads them automatically.

## 4. Verification
- Run the gates before every commit. Paste the actual output (not paraphrased). A green claim requires the pasted output + the head SHA. "It passed" is not evidence.
- Gates for this repo:
  - Test (smoke): `GODOT_BIN=./godot bash scripts/ci/smoke_test.sh` (Godot 4.4.1 headless, runs all 30 chapters via `scripts/ci/headless_smoke_driver.gd`; asserts `COMPLETED == 30` + `"All 30 chapters complete"` + zero `SCRIPT ERROR`/`Parse Error`/`FATAL`; timeout 300s)
  - Test (browser PWA): `python3 scripts/ci/browser_smoke.py` (requires `playwright` installed)
  - Lint: `gdformat --check . && gdlint .` (requires `pip install gdtoolkit`; CI runs both with `|| true` — advisory, but fix rather than bypass)
  - Fmt: `gdformat --check .` (`gdformat .` to write)
  - Typecheck: n/a (GDScript has no standalone typechecker; the headless smoke test is the de-facto typecheck)
- Do not rewrite tests to make them pass. Fix the root cause.
- Do not add `|| true`, `|| echo "non-fatal"`, `#[ignore]` to make red go green. (CI lint currently uses `|| true` as advisory — that's a pre-existing repo choice, not a license to silence real failures.)
- Do not commit `.godot/`, `*.gd.uid`, `*.import`, `builds/web/index.*`, `builds/web/*.pck`, `builds/web/*.wasm`, `assets/bgm/`, `assets/video/`, `*.save`, `*.sav`.

## 5. Demand elegance
- Small, pure, well-named functions. No dead code. No debug spam (`push_error`, `print()`, `printerr`) in committed code.
- Match the existing style. GDScript 4.4 conventions; `gdformat` enforces formatting. Autoloads are declared in `project.godot` (`[autoload]`): `GameState`, `ChapterDatabase`, `AudioManager`, `GhostRecorder`, `PlayFab`, `CritEffect`, `ScreenShake`, `HitStop`, `ScreenFader`, `ErrorScreen`.
- Preserve honest-doc annotations (`ponytail:`, `ceiling:`, `upgrade path:`) — they document known limitations. Removing them is a regression.
- A change that adds 100 lines to fix a 3-line bug is probably wrong. Find the smaller change.

## 6. Autonomous bug fixing
- If a test fails, read the error. Find the root cause. Fix it.
- Do NOT: rewrite the test to pass, add `|| true`, lower a threshold, delete the assertion, add `#[ignore]` to make red go green.
- Do NOT: add debug logging to committed code. Use `workplan.md` for scratch notes.
- If you've attempted the same fix 3 times and it's still red, STOP. Write "ESCALATE: <root cause unknown>" in `lessons.md` and return. The brain takes over when the brawn is stuck.

## Task management
1. **Plan**: write `workplan.md` (gitignored) with files to touch + root cause + gate.
2. **Check before implementation**: read `workplan.md`, `lessons.md`, `state.md`, and this `AGENTS.md`.
3. **Check progression**: after each file edit, verify it compiles/lints. Don't batch 10 changes then discover the 3rd was wrong.
4. **Explain changes**: post a summary in `workplan.md` (what changed, why) and a one-liner in `CHANGELOG.md` (it exists).
5. **Session close**: commit → write `lessons.md` (what I learned) → update `state.md` (what changed, what's pending) → `CHANGELOG.md` one-liner → verify clean tree → verify gates green → paste final gate output. Session is NOT done until all 6 are done.
6. **Worktree discipline**: work in an isolated worktree off `origin/main` (this repo's default branch is `main`). `git fetch && git reset --hard origin/main` before starting. Never touch `main` directly. Never force-push. Fix forward.
7. **Scope discipline**: touch only the files the task names. If you need to edit outside scope, note it in `lessons.md` as "scope creep: <file> because <reason>".
8. **Honesty over claim**: paste gate output, never say "green" without the run ID + head SHA. An ADR that overclaims is a regression. A "CI green" citation for the wrong run ID is a regression.

## Escalation
If you are stuck after 3 attempts, say so. Write "ESCALATE: <root cause unknown>" in `lessons.md`. The brain (frontier model) takes over. This is not a failure — it's the design: the Fiat knows when to call the tow truck.