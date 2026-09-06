# Installation

`html5` is published to [PyPI](https://pypi.org/project/html5/).

## pip

```bash
pip install html5
```

## requirements.txt

```text
html5==0.3.0
```

## pyproject.toml

### uv

```toml
[project]
dependencies = ["html5>=0.3.0"]
```

Then run:

```bash
uv sync
```

### Poetry

```toml
[tool.poetry.dependencies]
python = "^3.10"
html5 = "^0.3.0"
```

Then run:

```bash
poetry install
```

## Verifying the install

```python
import html5
print(html5.__version__)  # 0.3.0
```
