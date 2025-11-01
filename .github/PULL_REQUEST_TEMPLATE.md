### Notes

- This repository uses an AI bot for reviews. Keep your PR in **Draft** while
  you work. When you’re ready for a review, change the status to **Ready for
  review** to trigger a new review round. If you make additional changes and
  don’t want to trigger the bot, switch the PR back to **Draft**.
- AI-bot comments may not always be accurate. Please review them critically and
  share your feedback; it helps us improve the tool.
- Avoid changing code that is unrelated to your proposal. Keep your PR as short
  as possible to increase the chances of a timely review. Large PRs may not be
  reviewed and may be closed.
- Don’t add unnecessary comments. Your code should be readable and
  self-documenting
  ([guidance](https://google.github.io/styleguide/cppguide.html#Comments)).
- Don’t change core features without prior discussion with the community. Use
  our Discord to discuss ideas, blockers, or issues
  (https://discord.gg/Nu4MdGj9jB).
- Do not include secrets (API keys, tokens, passwords), credentials, or
  sensitive data/PII in code, configs, logs, screenshots, or commit history. If
  something leaks, rotate the credentials immediately, invalidate the old key,
  and note it in the PR so maintainers can assist.
- Do not commit large binaries or generated artifacts. If large datasets are
  needed for tests, prefer small fixtures or programmatic downloads declared in
  makim.yaml (e.g., a task that fetches data at test time). If a large binary is
  unavoidable, discuss first and consider Git LFS.

## Pull Request description

<!-- Describe the purpose of your PR and the changes you have made. -->

<!-- Which issue this PR aims to resolve or fix? E.g.:
Fixes #4
-->

## How to test these changes

<!-- Example:

* run `$ abc -p 1234`
* open the web browser with url localhost:1234
* ...
-->

- `...`

<!-- Modify the options to suit your project. -->

## Pull Request checklists

This PR is a:

- [ ] bug-fix
- [ ] new feature
- [ ] maintenance

About this PR:

- [ ] it includes tests.
- [ ] the tests are executed on CI.
- [ ] the tests generate log file(s) (path).
- [ ] pre-commit hooks were executed locally.
- [ ] this PR requires a project documentation update.

Author's checklist:

- [ ] I have reviewed the changes and it contains no misspelling.
- [ ] The code is well commented, especially in the parts that contain more
      complexity.
- [ ] New and old tests passed locally.

## Additional information

<!-- Add any screenshot that helps to show the changes proposed -->

<!-- Add any other extra information that would help to understand the changes proposed by this PR -->

## Reviewer's checklist

Copy and paste this template for your review's note:

```
## Reviewer's Checklist

- [ ] I managed to reproduce the problem locally from the `main` branch
- [ ] I managed to test the new changes locally
- [ ] I confirm that the issues mentioned were fixed/resolved
```
