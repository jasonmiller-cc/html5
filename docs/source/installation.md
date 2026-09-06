# Installation

`html5cc` is published to [PyPI](https://pypi.org/project/html5cc/).
The import name is `html5`.

## pip

```bash
pip install html5cc
```

## requirements.txt

```text
html5cc==0.4.0
```

## pyproject.toml

### uv

```toml
[project]
dependencies = ["html5cc>=0.4.0"]
```

Then run:

```bash
uv sync
```

### Poetry

```toml
[tool.poetry.dependencies]
python = "^3.10"
html5cc = "^0.4.0"
```

Then run:

```bash
poetry install
```

## Verifying the install

```python
import html5
print(html5.__version__)  # 0.4.0
```
