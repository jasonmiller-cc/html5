# Installation

`html5` is published to [GitHub Packages](https://github.com/jasonmiller-cc/html5/packages).
You need a GitHub Personal Access Token (PAT) with the **`read:packages`** scope to install it.

## Create a token

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**.
2. Generate a new token with at least the `read:packages` scope.
3. Store the token securely (e.g. in a password manager or environment variable).

## pip

Pass the GitHub Packages index as an extra source so pip falls back to it after PyPI:

```bash
pip install html5 \
  --extra-index-url https://<your-github-username>:<your-token>@pypi.pkg.github.com/jasonmiller-cc/
```

Or export your token as an environment variable and reference it:

```bash
export GH_TOKEN=<your-token>
pip install html5 \
  --extra-index-url "https://<your-github-username>:${GH_TOKEN}@pypi.pkg.github.com/jasonmiller-cc/"
```

## requirements.txt

```text
--extra-index-url https://<your-github-username>:<your-token>@pypi.pkg.github.com/jasonmiller-cc/
html5==0.3.0
```

In CI, avoid committing tokens in plain text. Use a repository secret and substitute it at install time:

```text
--extra-index-url https://x-access-token:${GH_TOKEN}@pypi.pkg.github.com/jasonmiller-cc/
html5==0.3.0
```

```yaml
# GitHub Actions example
- name: Install dependencies
  run: pip install -r requirements.txt
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## pyproject.toml (pip / uv)

### pip (PEP 517)

There is no standard mechanism for declaring a private index inside `pyproject.toml` for pip.
Use a `pip.conf` file, a `.env` file that exports `PIP_EXTRA_INDEX_URL`, or pass the flag on the command line as shown above.

### uv

```toml
[project]
dependencies = ["html5>=0.3.0"]

[[tool.uv.index]]
name = "github-html5"
url = "https://pypi.pkg.github.com/jasonmiller-cc/"
```

Authenticate by storing credentials in a `.netrc` file or by setting `UV_INDEX_<NAME>_USERNAME` and `UV_INDEX_<NAME>_PASSWORD` environment variables (replace `<NAME>` with the uppercased index name, e.g. `GITHUB_HTML5`):

```bash
export UV_INDEX_GITHUB_HTML5_USERNAME=<your-github-username>
export UV_INDEX_GITHUB_HTML5_PASSWORD=<your-token>
uv sync
```

### Poetry

```toml
[tool.poetry.dependencies]
python = "^3.10"
html5 = { version = "^0.3.0", source = "github-html5" }

[[tool.poetry.source]]
name = "github-html5"
url = "https://pypi.pkg.github.com/jasonmiller-cc/"
priority = "supplemental"
```

Configure credentials once per machine:

```bash
poetry config http-basic.github-html5 <your-github-username> <your-token>
```

## Verifying the install

```python
import html5
print(html5.__version__)  # 0.3.0
```
