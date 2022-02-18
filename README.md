# rl-training

# Development

Create a new environment:

```bash
conda create -n rl-training python=3.8
conda activate rl-training
```

Install dependencies:

```bash
pip install -r requirements.txt
```

To run the tests make sure you are at the root of the repository and run:

```bash
export PYTHONPATH=$(pwd)
pytest tests/unit -v
```
