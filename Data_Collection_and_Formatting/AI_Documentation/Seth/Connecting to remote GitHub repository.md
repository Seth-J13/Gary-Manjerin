# Connecting to remote GitHub repository

## User

I am new to Git CLI how do I connect to my remote GitHub repo?

PS C:\Users\xrock\OC_Classes\AI_Project_T1\Gary-Manjerin> git pull dev
fatal: 'dev' does not appear to be a git repository
fatal: Could not read from remote repository.
Please make sure you have the correct access rights
and the repository exists.
PS C:\Users\xrock\OC_Classes\AI_Project_T1\Gary-Manjerin>

## Claude

## Connecting to a Remote GitHub Repository

The error means Git doesn't know what `dev` is — you need to first **add a remote** that points to your GitHub repo.

### Step 1 — Add the Remote

```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
```

Replace the URL with your actual GitHub repo URL. `origin` is the standard name for your main remote.

---

### Step 2 — Verify it was added

```bash
git remote -v
```

You should see something like:
```
origin  https://github.com/YOUR-USERNAME/YOUR-REPO.git (fetch)
origin  https://github.com/YOUR-USERNAME/YOUR-REPO.git (push)
```

---

### Step 3 — Pull from the correct remote/branch

```bash
git pull origin main
```

> Replace `main` with `master` or whatever your default branch is called on GitHub.

---

### What went wrong with your command

```bash
git pull dev   # ❌ Git looked for a remote named "dev" — it doesn't exist
git pull origin dev  # ✅ This would pull the "dev" branch from "origin"
```

`git pull` expects the format: `git pull <remote-name> <branch-name>`

---

### Useful commands to get oriented

| Command | What it does |
|---|---|
| `git remote -v` | List all remotes |
| `git branch -a` | List all branches (local + remote) |
| `git status` | See current state of your working directory |
| `git pull origin main` | Pull latest changes from GitHub |

---

### Getting your GitHub repo URL

Go to your repo on GitHub → click the green **"Code"** button → copy the HTTPS URL.

## User

how do I add a branch to the online repo>

## Claude

## Pushing a Branch to GitHub

### Step 1 — Create the branch locally (if you haven't yet)

```bash
git checkout -b dev
```
This creates **and** switches you to the new branch.

---

### Step 2 — Make sure you have at least one commit on it

```bash
git add .
git commit -m "your message here"
```
> GitHub won't show an empty branch with no commits.

---

### Step 3 — Push the branch to GitHub

```bash
git push -u origin dev
```

The `-u` flag sets **upstream tracking**, meaning from now on you can just type `git push` or `git pull` while on that branch — no need to specify `origin dev` every time.

---

### After that, simple push/pull on that branch

```bash
git push       # send your commits up to GitHub
git pull       # get latest changes from GitHub
```

---

### Useful branch commands

| Command | What it does |
|---|---|
| `git checkout -b dev` | Create and switch to a new branch |
| `git checkout main` | Switch back to main |
| `git branch` | List local branches |
| `git branch -a` | List all branches including remote |
| `git push -u origin dev` | Push branch to GitHub for the first time |
| `git push` | Push updates after the first time |

---

### What it looks like on GitHub
Once pushed, you'll see the branch in your repo under the **branch dropdown** (defaults to `main`), and you can open a **Pull Request** from there to merge it into `main` when ready.

## User

can you display common commands for remote GitHub CLI

## Claude

Here's a full reference covering the most common Git remote commands. A few things worth highlighting for a beginner:

- The **first time** you push a branch, always use `git push -u origin <branch>` — the `-u` sets up tracking so future pushes/pulls are just `git push` or `git pull`.
- Use `git fetch` when you want to see what's changed on GitHub without actually merging it yet.
- Be careful with `git reset --hard` and `git push --force` — they rewrite history and can cause issues if others are on the same branch.

