# Writing docs

Docs are located in the docs folder. We are using `sphinx` to generate the docs and then hosting them on `readthedocs`.

## Start docs autobuild to test locally
```bash
sphinx-autobuild docs docs/_build/html --watch aztk
```
Open `docs/_build/index.html`

## Publish the docs

Docs should be published automatically to read the docs as soon as you push to master under the `latest` tag.
You when creating a git tag readthedocs can also build that one.
