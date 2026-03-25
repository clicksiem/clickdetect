# Contributing

### Development environment

This is how I setup the development environment

```sh
git clone https://githun.com/clicksiem/clickdetect
uv sync
source .venv/bin/activate
```

### Commits & Pull requests

Use conventional commits in your commits.

* Read pyproject.toml
* Look for tool.git-cliff.git
* This is how your commits needs to be

### Code quality

Use [Ruff](https://docs.astral.sh/ruff/tutorial/) for identation & Code quality.

* Run uv run check to check the codebase

### IA / LLM

If you are an excited vibecoder, don't try to update the base structure.

Always test your code in a production like environment.
