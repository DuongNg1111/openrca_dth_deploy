# Environment setup

## 1. Python
Install **Python 3.10+**. Check: `python3 --version`.

## 2. Virtual environment + deps
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
> You can run the smoke test even before installing anything (it uses only the standard library).

## 3. Run the pipeline
```bash
python -m src.pipeline
python -m pytest -q
```

## 4. Get the dataset (for M3+)
Follow [`../data/DATA.md`](../data/DATA.md). Then set `use_mock: false` in `config/config.yaml`.

## 5. (Optional) LLM key
For LLM reasoning, export a key and reference it by env var (never hard-code):
```bash
export OPENAI_API_KEY=sk-...
```

## 6. (Optional) pre-commit hooks
```bash
pip install pre-commit && pre-commit install
```
