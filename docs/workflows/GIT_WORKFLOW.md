# Git Workflow & Development Strategy

**Project**: ETL UI - HR Data Transformation Tool
**Version**: 1.0
**Last Updated**: November 2, 2025

## Overview

This document defines the Git workflow and branching strategy for the ETL UI project. We use a **modular development approach** where each developer works independently on their module with regular integration checkpoints.

---

## Branching Strategy

### Branch Structure

```
main (production-ready code)
  ├── dev1-frontend-core (Module 1)
  ├── dev2-mapping-engine (Module 2)
  ├── dev3-transformation (Module 3)
  └── dev4-schema-automapping (Module 4)
```

### Branch Naming Convention

- **Module branches**: `dev{N}-{module-name}`
  - `dev1-frontend-core`
  - `dev2-mapping-engine`
  - `dev3-transformation`
  - `dev4-schema-automapping`

- **Feature branches** (if needed): `feature/{module}-{feature-name}`
  - `feature/mapping-visual-lines`
  - `feature/transform-date-conversion`

- **Bugfix branches**: `bugfix/{issue-description}`
  - `bugfix/upload-cors-error`
  - `bugfix/mapping-duplicate-fields`

---

## Initial Setup

### Day 0: Repository Setup

1. **Create GitHub Repository**
```bash
# On GitHub, create new repository: etl-ui-tool
# Initialize with README.md (optional)
```

2. **Clone Repository**
```bash
git clone https://github.com/your-org/etl-ui-tool.git
cd etl-ui-tool
```

3. **Setup Main Branch**
```bash
# Ensure you're on main branch
git checkout main

# Add initial project structure
git add .
git commit -m "Initial project structure"
git push origin main
```

4. **Create Module Branches**
```bash
# Developer 1
git checkout -b dev1-frontend-core
git push -u origin dev1-frontend-core

# Developer 2
git checkout -b dev2-mapping-engine
git push -u origin dev2-mapping-engine

# Developer 3
git checkout -b dev3-transformation
git push -u origin dev3-transformation

# Developer 4
git checkout -b dev4-schema-automapping
git push -u origin dev4-schema-automapping
```

---

## Daily Workflow

### Phase 1: Independent Development (Days 1-2)

Each developer works **independently** on their module branch.

#### Morning Routine (9:00 AM)

1. **Sync with main** (in case of overnight changes)
```bash
git checkout dev1-frontend-core
git fetch origin
git merge origin/main
```

2. **Start working** on daily tasks
```bash
# Make changes...
git status  # Check what changed
```

#### Throughout the Day

**Commit frequently** (every 1-2 hours):

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "Day 1: Implemented FileUpload component

- Added drag-and-drop functionality
- File validation for CSV/Excel
- Upload progress indicator
- Error handling for invalid files"

# Push to remote
git push origin dev1-frontend-core
```

#### Commit Message Format

Follow this format for clear commit history:

```
Day X: Brief description (< 50 chars)

- Detailed bullet point 1
- Detailed bullet point 2
- Detailed bullet point 3

[Optional: closes #issue-number]
```

**Examples**:

```bash
# Good commit messages
git commit -m "Day 1: Setup FastAPI project structure

- Created main.py with CORS config
- Added requirements.txt with dependencies
- Configured development environment"

git commit -m "Day 2: Implemented auto-mapping algorithm

- Fuzzy matching using Levenshtein distance
- Alias dictionary with 50+ common variations
- Confidence scoring (0.0 to 1.0)
- Unit tests with 85% coverage"
```

```bash
# Bad commit messages (avoid these)
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "wip"
```

#### End of Day (6:00 PM)

1. **Commit all work**
```bash
git add .
git commit -m "Day 1 EOD: FileUpload component complete"
git push origin dev1-frontend-core
```

2. **Update progress tracker** (shared Google Sheet/Notion)

3. **Attend daily standup** (15 minutes)

---

### Phase 2: First Integration (Day 3)

#### Integration Checkpoint (2 hours)

**Goal**: Merge all module branches and test integration

1. **Backend Integration First** (Dev 3 + Dev 4)

```bash
# Dev 3 drives, Dev 4 watches
git checkout main
git pull origin main

# Merge transformation module
git merge dev3-transformation
# Resolve conflicts if any

# Merge schema module
git merge dev4-schema-automapping
# Resolve conflicts if any

# Test: Ensure backend starts
cd backend
uvicorn app.main:app --reload

# If tests pass, push to main
git push origin main
```

2. **Frontend Integration** (Dev 1 + Dev 2)

```bash
# Dev 1 drives, Dev 2 watches
git checkout main
git pull origin main

# Merge frontend core
git merge dev1-frontend-core
# Resolve conflicts if any

# Merge mapping engine
git merge dev2-mapping-engine
# Resolve conflicts if any

# Test: Ensure frontend builds
cd frontend
npm install
npm run dev

# If tests pass, push to main
git push origin main
```

3. **End-to-End Integration Test** (All developers)

```bash
# Start backend
cd backend && uvicorn app.main:app --reload

# Start frontend (in separate terminal)
cd frontend && npm run dev

# Test full flow:
# - Upload file
# - Auto-map fields
# - Preview transformation
```

4. **Each developer syncs their branch**

```bash
git checkout dev1-frontend-core
git merge main
git push origin dev1-frontend-core
```

---

### Phase 3: Continuous Integration (Days 4-6)

#### Daily Merge Ritual (6:00 PM)

**One person drives, all watch:**

1. **Prepare for merge** (each dev)
```bash
# Commit all changes
git add .
git commit -m "Day 4: Validation component complete"
git push origin dev1-frontend-core
```

2. **Merge to main** (designated merger)
```bash
git checkout main
git pull origin main

# Merge each module in order
git merge dev1-frontend-core
git merge dev2-mapping-engine
git merge dev3-transformation
git merge dev4-schema-automapping

# Resolve conflicts together
# Test quickly (smoke test)

# Push to main
git push origin main
```

3. **Everyone pulls latest**
```bash
git checkout dev1-frontend-core
git merge main
git push origin dev1-frontend-core
```

#### Handling Merge Conflicts

**Scenario**: Two developers modified the same file

```bash
# When merge conflict occurs
git merge dev2-mapping-engine
# Auto-merging frontend/src/App.tsx
# CONFLICT (content): Merge conflict in frontend/src/App.tsx

# 1. Open file with conflict
code frontend/src/App.tsx

# 2. Look for conflict markers
<<<<<<< HEAD
// Dev 1's code
=======
// Dev 2's code
>>>>>>> dev2-mapping-engine

# 3. Discuss with both devs and resolve
# Keep both changes, or choose one

# 4. Stage resolved file
git add frontend/src/App.tsx

# 5. Complete merge
git commit -m "Merge dev2-mapping-engine: resolved App.tsx conflict"
```

**Tips for avoiding conflicts**:
- Work on different files when possible
- Communicate about shared files
- Merge frequently (daily)

---

### Phase 4: Final Integration (Day 7)

#### Morning: Full Integration

```bash
# Merge all branches one final time
git checkout main
git merge dev1-frontend-core
git merge dev2-mapping-engine
git merge dev3-transformation
git merge dev4-schema-automapping

# Resolve any conflicts
# Run full test suite
# Fix critical bugs

git push origin main
```

#### Afternoon: Demo Preparation

```bash
# Create demo branch (optional)
git checkout -b demo-preparation
git push -u origin demo-preparation

# Make demo-specific tweaks
# Test demo flow 3-4 times
```

---

## Common Git Commands Cheat Sheet

### Basics
```bash
# Check current branch
git branch

# Check status
git status

# See commit history
git log --oneline --graph --all

# See what changed
git diff

# See staged changes
git diff --staged
```

### Branching
```bash
# Create and switch to new branch
git checkout -b feature/new-feature

# Switch to existing branch
git checkout dev1-frontend-core

# Delete local branch
git branch -d feature/old-feature

# Delete remote branch
git push origin --delete feature/old-feature
```

### Undoing Changes
```bash
# Discard changes in file
git checkout -- filename.ts

# Unstage file
git reset HEAD filename.ts

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - DANGEROUS!
git reset --hard HEAD~1

# Revert a commit (creates new commit)
git revert <commit-hash>
```

### Syncing
```bash
# Fetch remote changes
git fetch origin

# Pull latest from remote
git pull origin main

# Push to remote
git push origin dev1-frontend-core

# Force push (use carefully!)
git push origin dev1-frontend-core --force
```

### Stashing
```bash
# Stash current changes
git stash

# List stashes
git stash list

# Apply latest stash
git stash pop

# Apply specific stash
git stash apply stash@{1}
```

---

## Pull Request (PR) Workflow

### When to Use PRs

PRs are **optional** for this hackathon but recommended for:
- Major feature completion
- Code review before merging
- End of each development phase

### Creating a PR

1. **Push your branch**
```bash
git push origin dev1-frontend-core
```

2. **Open PR on GitHub**
   - Go to repository on GitHub
   - Click "Pull Requests" → "New Pull Request"
   - Base: `main` ← Compare: `dev1-frontend-core`
   - Add title: "Module 1: Frontend Core - Complete"
   - Add description with:
     - What was implemented
     - Testing done
     - Screenshots (if UI changes)

3. **Request review** from team members

4. **Merge after approval**

### PR Template (optional)

```markdown
## Module: Frontend Core (Dev 1)

### Implemented Features
- [x] FileUpload component with drag-and-drop
- [x] DataPreview component with table display
- [x] ExportDownload component
- [x] Common UI components (Button, Card, Modal)

### Testing Done
- [x] Manual testing with CSV files
- [x] Manual testing with Excel files
- [x] Integration testing with backend APIs
- [x] Error handling tested

### Screenshots
[Add screenshots of UI]

### Notes
- Used @dnd-kit/core for drag-and-drop
- All components are TypeScript with strict mode
- Follows Tailwind CSS design system
```

---

## Best Practices

### Commit Frequency
- ✅ **Do**: Commit every 1-2 hours
- ✅ **Do**: Commit before switching tasks
- ✅ **Do**: Commit before major refactoring
- ❌ **Don't**: Commit broken code (unless WIP branch)
- ❌ **Don't**: Wait until end of day for first commit

### Commit Size
- ✅ **Do**: Small, focused commits
- ✅ **Do**: One feature/fix per commit
- ❌ **Don't**: Commit 50 files at once
- ❌ **Don't**: Mix unrelated changes

### Commit Messages
- ✅ **Do**: Clear, descriptive messages
- ✅ **Do**: Use bullet points for details
- ❌ **Don't**: "Fixed bug" or "Updates"
- ❌ **Don't**: No message or "wip"

### Branching
- ✅ **Do**: Keep module branches focused
- ✅ **Do**: Merge main into your branch daily
- ❌ **Don't**: Work directly on main
- ❌ **Don't**: Create too many branches

### Merging
- ✅ **Do**: Test before merging
- ✅ **Do**: Resolve conflicts with team
- ✅ **Do**: Communicate before force push
- ❌ **Don't**: Merge without testing
- ❌ **Don't**: Force push without warning

---

## Troubleshooting

### "I'm on the wrong branch!"

```bash
# Don't panic! Your changes are safe

# 1. Stash your changes
git stash

# 2. Switch to correct branch
git checkout dev1-frontend-core

# 3. Apply stashed changes
git stash pop
```

### "I committed to main by mistake!"

```bash
# 1. Create branch from current state
git checkout -b dev1-frontend-core

# 2. Reset main to previous state
git checkout main
git reset --hard origin/main

# 3. Your changes are now on dev1-frontend-core
git checkout dev1-frontend-core
```

### "I need to undo my last commit"

```bash
# Undo commit but keep changes
git reset --soft HEAD~1

# Make corrections
git add .
git commit -m "Corrected commit message"
```

### "Merge conflict is too complex"

```bash
# Abort the merge
git merge --abort

# Ask for help from team
# Pair program to resolve conflict
```

---

## Git Etiquette

### Before You Push
- [ ] Code compiles/builds successfully
- [ ] No console errors
- [ ] Tested your changes
- [ ] Clear commit message written

### During Integration
- [ ] Communicate what you're merging
- [ ] Watch for conflicts
- [ ] Help resolve conflicts in your code
- [ ] Test after merge completes

### Daily
- [ ] Commit at least 3-4 times
- [ ] Push to remote by end of day
- [ ] Sync with main before starting
- [ ] Update progress tracker

---

## Emergency Procedures

### "I broke main branch!"

1. **Don't panic**
2. **Communicate immediately** in team chat
3. **Identify last working commit**
```bash
git log --oneline
```
4. **Revert to working state**
```bash
git revert <bad-commit-hash>
# OR
git reset --hard <good-commit-hash>
git push --force origin main
```
5. **Inform team** to pull latest

### "My branch is way behind main"

```bash
# Option 1: Merge (preserves your commits)
git checkout dev1-frontend-core
git merge main
git push origin dev1-frontend-core

# Option 2: Rebase (cleaner history, more complex)
git checkout dev1-frontend-core
git rebase main
git push --force origin dev1-frontend-core
```

---

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials)
- [Oh Shit, Git!?!](https://ohshitgit.com/) - Common git mistakes

---

## Questions?

If you're unsure about any Git operation:
1. **Ask in team chat** before proceeding
2. **Don't guess** with commands like `git reset --hard`
3. **Pair program** for complex merges
4. **Daily standup** for workflow questions

---

**Remember**: Git is a tool to help us collaborate. When in doubt, communicate!

*Last Updated: November 2, 2025*
