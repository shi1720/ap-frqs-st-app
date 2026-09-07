# AP Free-Response Question Review

Review AP free-response questions in batches using configurable evaluation prompts, parallel requests and downloadable feedback.

**Stack:** Python / Streamlit. **Status:** reference implementation. Provider integrations require your own credentials and service access.

## Run locally

Use Python 3.12 and a virtual environment. Commands below run from the repository root.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements.lock.txt
```

Where the interface asks for a provider key or backend address, supply your own authorized configuration at runtime. The repository does not supply access to an external service.

```bash
python -m streamlit run st-qc-frqs.py --server.address 127.0.0.1
```

Open the localhost URL printed by Streamlit. Start with a small synthetic input, review the result, then export or continue the workflow.

## Repository map

| Path | Role |
| --- | --- |
| [`st-qc-frqs.py`](st-qc-frqs.py) | Application entrypoint and workflow logic |
| [`requirements.txt`](requirements.txt) | Direct Python dependencies |
| [`requirements.lock.txt`](requirements.lock.txt) | Pinned Python 3.12 dependencies with integrity hashes |
| [`.github/workflows/repository-quality.yml`](.github/workflows/repository-quality.yml) | Offline maintenance checks |

## Validation

```bash
python .github/scripts/repository_check.py --self-test
python .github/scripts/repository_check.py
```

CI checks Python syntax, local documentation links, credential patterns and locked dependency compatibility without importing the app or calling a model. Dependency validation contacts the package index; it does not install the application or use provider credentials. It does not establish grading accuracy or current provider availability. For integration validation, use synthetic examples and compare the output with known answers.

## Operating notes

Model names, remote endpoints and prompt assumptions reflect the original implementation. Review them before connecting current services. Keep provider keys, service-account files and private learning data outside the repository. Any credential previously committed must be rotated; removing it from the current tree does not invalidate earlier copies.

## Contributing

Keep changes focused and add regression coverage for behavior changes. Include synthetic reproduction data and the checks actually run. See the account [contribution guide](https://github.com/shi1720/.github/blob/main/CONTRIBUTING.md) and [private security reporting process](https://github.com/shi1720/.github/blob/main/SECURITY.md).

No open-source license is currently granted by this repository. Preserve existing ownership and obtain permission before reuse or redistribution.

## Refresh dependencies

```bash
uv pip compile --python-version 3.12 --universal --generate-hashes requirements.txt -o requirements.lock.txt
```

Validate the relevant provider integrations before deploying dependency updates. A lockfile fixes dependency resolution; it does not establish that a historical model endpoint is still available.
