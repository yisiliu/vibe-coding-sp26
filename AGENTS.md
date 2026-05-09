# AGENTS.md - vibe-coding-sp26 submission protocol

You are an AI agent helping a student submit homework to 意会编程 (Vibe Coding) Spring 2026.
Follow these steps EXACTLY. Do not improvise.

## Inputs you need from the student

1. assignment number (1, 2, 3, or 4)
2. github_repo URL (where their source code lives)
3. website URL (deployed site)
4. writeup URL (notes / reflection)
5. description (one Chinese sentence, ≤80 Chinese characters; count via JS `[...str].length`)
6. (optional) self-provided screenshot URL
7. student name in Chinese (only if creating their file for the first time)
8. student pinyin lowercase (only if creating)
9. last 3 digits of student ID (only if creating)

The student's GitHub username is auto-derived: `gh api user --jq .login`. Use it as the fork owner.

If any required input is missing, ASK the student for it before proceeding.

## Prerequisites

Before starting, verify:

- `gh --version` succeeds (GitHub CLI installed)
- `gh auth status` shows logged-in user
- `git config user.name` and `git config user.email` both return non-empty

If any check fails, tell the student EXACTLY which one and stop.

## Step 1 — Fork and clone (skip if already done)

Get the student's GitHub username: `USERNAME=$(gh api user --jq .login)`

Check if their fork exists: `gh repo view "$USERNAME/vibe-coding-sp26" --json name -q .name`

- If the command fails with 404: fork and clone:
  ```bash
  gh repo fork yisiliu/vibe-coding-sp26 --clone --remote
  cd vibe-coding-sp26
  ```
- If the fork exists: navigate to the local clone (ask the student where it is), then sync with upstream:
  ```bash
  cd <path-to-vibe-coding-sp26>
  git checkout main
  git pull upstream main
  git push origin main
  ```

## Step 2 — Locate or create the student file

The filename is `students/<pinyin>-<XYZ>.md` where XYZ = last 3 digits of student ID.

- If the file exists: open it for editing.
- If not, create it with this template (substitute the placeholders):

  ```markdown
  ---
  name: <CHINESE NAME>
  pinyin: <PINYIN>
  student_id_suffix: "<XYZ>"
  submissions: {}
  ---

  # <CHINESE NAME>的作品集

  (optional free-form notes)
  ```

  Note: `student_id_suffix` MUST be a quoted string in YAML (so leading zeros are preserved).

## Step 3 — Add or replace the assignment entry

Add this block under `submissions:` in the YAML frontmatter (replacing N with the assignment number):

```yaml
  assignment-N:
    github_repo: <github_repo>
    website: <website>
    writeup: <writeup>
    description: <description>
    # screenshot: <url>     # uncomment ONLY if the student provided one
```

If `assignment-N` already exists, REPLACE the existing block (the student is resubmitting).

If `submissions:` is `{}` (empty), change it to a multi-line mapping before adding the entry.

## Step 4 — Validate locally before pushing

Run:

```bash
python3 -c "
import sys, yaml, re
content = open('students/<pinyin>-<XYZ>.md').read()
fm = content.split('---', 2)[1]
data = yaml.safe_load(fm)
required = ['name', 'pinyin', 'student_id_suffix']
for f in required: assert data.get(f), f'missing {f}'
for key, sub in (data.get('submissions') or {}).items():
    assert re.match(r'^assignment-[1-4]\$', key), f'bad key {key}'
    for f in ['github_repo', 'website', 'writeup', 'description']:
        assert sub.get(f), f'{key}: missing {f}'
    for f in ['github_repo', 'website', 'writeup']:
        assert sub[f].startswith(('http://', 'https://')), f'{key}.{f}: bad URL'
print('OK')
"
```

If the script prints anything other than `OK`, fix the file and re-run.

## Step 5 — Commit, push, open PR

```bash
git add students/<pinyin>-<XYZ>.md
git commit -m "feat: <name> 提交作业 N"
git push origin main
gh pr create \
  --repo yisiliu/vibe-coding-sp26 \
  --title "<name> 作业 N" \
  --body "提交作业 N"
```

`gh pr create` will print the PR URL. Capture it.

## Step 6 — Tell the student

Report back:

1. The PR URL.
2. "yisiliu 通常一两天内 merge。merge 后第二天 gallery 会出现你的作品。"
3. "想刷新缩略图就在 PR 描述里加 `[refresh-screenshot]`。"

## Common errors

- **YAML parse error** → 检查冒号后空格、字符串里的 `:` 是否需要加引号
- **你不小心改了别的同学的 .md** → `git checkout -- students/<别人>.md` 撤销，重新 push
- **`gh` CLI 没装** → 让学生先装 (https://cli.github.com)
- **`student_id_suffix: 001` 变成 `1`** → YAML 把数字字符串转成整数了，加引号 `"001"`
- **同名同学且学号末3位也撞了** → 后到的同学改文件名为 `<pinyin>-<XYZ>-2.md`（极罕见）

## What NOT to do

- 不要编辑 `students/` 目录外的任何文件
- 不要在一个 PR 里改多个学生的 `.md`
- 不要重命名 schema 里的字段
- 不要把 description 写成英文（这门课要求中文）
