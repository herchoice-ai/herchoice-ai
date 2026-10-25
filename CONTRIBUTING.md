# Contributing to HerChoice AI

Thank you for helping women and girls get trusted health information in their own language.

## Ways to help

- **Hausa language review:** check that answers and messages are natural, respectful and clear when read aloud.
- **Clinical review:** check accuracy and safety of content against current WHO and Federal Ministry of Health guidance.
- **Code:** fix bugs, add channels (voice line, USSD), improve speech accuracy, improve accessibility.
- **Testing:** report anything confusing, unsafe or broken.

## How to contribute code

1. Fork the repository and create a branch: `git checkout -b my-change`.
2. Install: `pip install -e ".[dev]"`.
3. Make your change and add tests.
4. Run `pytest`; all tests must pass.
5. Open a pull request describing what changed and why.

## Content changes

Content changes follow [docs/CONTENT_REVIEW.md](docs/CONTENT_REVIEW.md). A pull request may add or edit **draft** entries; only the clinical reviewer may set `review_status` to `approved`.

## Rules that are never relaxed

- Never log or store message content or phone numbers in plain form.
- Never let the system answer health questions from anything other than the content library.
- Never weaken the safety layer without sign-off from the safeguarding lead.
- Never include real user data in issues, tests or examples.

By contributing, you agree that your code is licensed under Apache 2.0 and your content under CC BY 4.0, and you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
