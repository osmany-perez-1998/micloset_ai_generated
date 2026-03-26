# Contributing to MiCloset

## Branch Strategy

```
main        → production (auto-deploys on merge)
uat         → UAT environment (requires manual approval to deploy)
test        → QA / integration testing
dev         → development integration
feature/*   → individual features  (branch from dev)
bugfix/*    → bug fixes            (branch from dev or test)
hotfix/*    → emergency prod fixes (branch from main)
```

## Workflow

1. Create a GitHub Issue using the appropriate template
2. Branch off `dev`: `git checkout -b feature/MC-123-order-estimate`
   - Prefix: `MC-` + issue number + short description
3. Make your changes, commit often with descriptive messages
4. Open a PR against `dev`
5. CI must pass (lint + tests) before review
6. After code review approval, merge into `dev`
7. `dev` → `test` (QA testing)
8. `test` → `uat` (client acceptance — requires UAT environment approval)
9. `uat` → `main` (production — requires production environment approval)

## Commit Message Format

```
type(scope): short description

Types: feat | fix | chore | docs | refactor | test | style
Scope: backend | frontend | infra | auth | orders | shipping | ai

Examples:
  feat(orders): add price change confirmation flow
  fix(backend): return 404 when order not found
  chore(infra): add Redis healthcheck to docker-compose
```

## Environment Variables

- Never commit `.env` files
- Copy `.env.example` → `.env` and fill in local values
- All secrets go into GitHub Actions Secrets for CI/CD
