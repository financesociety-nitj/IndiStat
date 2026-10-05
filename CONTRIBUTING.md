# Contributing to Indicator-Library

Welcome to **Indicator-Library**, maintained by the **Technical Department, Finance Society, NITJ**! We welcome contributions from students, developers, and quantitative finance enthusiasts.

> 🌐 **Interactive Student Guide & Web Docs**: Check out our visual, interactive student guide for contributing: [docs/index.html](docs/index.html) (or on GitHub Pages at [financesociety-nitj.github.io/Indicator-Library](https://financesociety-nitj.github.io/Indicator-Library/)).

Whether you are fixing a bug, improving documentation, or implementing a new technical indicator (e.g. RSI, MACD, Bollinger Bands), this guide will help you get started.

---

## 📋 Table of Contents

- [Interactive Web Guide](#-interactive-web-guide)
- [Code of Conduct](#-code-of-conduct)
- [How to Contribute](#-how-to-contribute)
  - [Reporting Issues](#reporting-issues)
  - [Suggesting Features / Indicators](#suggesting-features--indicators)
  - [Pull Requests](#pull-requests)

- [Local Development Setup](#-local-development-setup)
- [Guidelines for Adding New Indicators](#-guidelines-for-adding-new-indicators)
- [Coding & Quality Standards](#-coding--quality-standards)
- [Testing](#-testing)
- [Continuous Integration (CI) Checks](#-continuous-integration-ci-checks)
- [Git Workflow & Commit Guidelines](#-git-workflow--commit-guidelines)

---

## 🤝 Code of Conduct

We are committed to providing a friendly, safe, and welcoming environment for all contributors regardless of experience level. Please remain respectful, constructive, and open to feedback.

---

## 💡 How to Contribute

### Reporting Issues

Before opening a new issue, please check the [existing issues](https://github.com/financesociety-nitj/Indicator-Library/issues) to avoid duplicates. When opening an issue, provide:
- A clear description of the problem or bug.
- Steps to reproduce, including code snippet and ticker symbol.
- Expected vs actual behavior.
- Operating system and Python version.

### Suggesting Features / Indicators

If you would like to request or propose a new indicator (e.g., RSI, MACD, Bollinger Bands, ATR):
- Open a feature request issue.
- Include the mathematical definition and formula for the indicator.
- Provide references (e.g. Investopedia, academic papers, or books) where applicable.

---

## 💻 Local Development Setup

### 1. Fork and Clone the Repository

Fork the repository on GitHub, then clone your fork locally:

```bash
git clone https://github.com/<your-username>/Indicator-Library.git
cd Indicator-Library
```

Add the upstream remote:

```bash
git remote add upstream https://github.com/financesociety-nitj/Indicator-Library.git
```

### 2. Set Up a Virtual Environment

We recommend using Python 3.9+:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it:
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

Install the library in editable mode with development dependencies:

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

---

## 📊 Guidelines for Adding New Indicators

All indicators in this library should adhere to the following standards:

1. **Input Format**:
   - Every indicator function must accept a standard `pandas.DataFrame` containing raw OHLCV columns (`Open`, `High`, `Low`, `Close`, `Volume`), which can be obtained using `get_stock_data` / `get_raw_ohlcv`.
   - Never modify input DataFrames in-place; return a copy or a new `Series`/`DataFrame`.

2. **Function Signature & Docstrings**:
   - Provide clear type annotations for all parameters and return types.
   - Use Google or NumPy docstring style detailing parameter meanings, defaults, formulas, and return shapes.

3. **Handling Edge Cases**:
   - Handle lookback periods properly (e.g., `min_periods` for moving averages).
   - Gracefully handle `NaN` values at the beginning of series without raising unhandled exceptions.
   - Validate input parameters (e.g. period > 0, standard deviation multipliers > 0).

4. **Example Template for New Indicators**:

```python
import pandas as pd

def simple_moving_average(
    data: pd.DataFrame,
    period: int = 20,
    price_col: str = "Close"
) -> pd.Series:
    """
    Calculate the Simple Moving Average (SMA).

    Parameters
    ----------
    data : pd.DataFrame
        OHLCV DataFrame containing at least the `price_col`.
    period : int, default 20
        Number of periods to smooth over. Must be > 0.
    price_col : str, default 'Close'
        Column name to apply SMA on.

    Returns
    -------
    pd.Series
        Series representing the computed SMA.
    """
    if period <= 0:
        raise ValueError("period must be greater than 0")
    if price_col not in data.columns:
        raise ValueError(f"Column '{price_col}' not found in provided data")

    return data[price_col].rolling(window=period).mean()
```

---

## 🧹 Coding & Quality Standards

- **PEP 8**: Follow standard PEP 8 Python formatting and style guidelines.
- **Type Annotations**: Use Python typing hints wherever practical (`typing` / modern Python typing).
- **Docstrings**: Add docstrings to all public functions, classes, and modules.
- **Pure Functions**: Indicators should be deterministic and idempotent without side-effects.

---

## 🧪 Testing

Every new feature or indicator must be accompanied by unit tests located in `tests/`:

1. Add tests in `tests/test_<feature>.py`.
2. Verify:
   - Known calculations against reference values or hand-computed values.
   - Behavior when invalid parameters are passed.
   - Edge cases (short series, missing data, empty data).

Run tests before submitting your PR:

```bash
pytest
```

Ensure all tests pass with zero failures.

---

## 🤖 Continuous Integration (CI) Checks

Every Pull Request submitted to `main` automatically triggers our GitHub Actions CI pipeline:

- **Multi-Version Testing Matrix**: Your code is built and tested against **Python 3.9, 3.10, 3.11, and 3.12** on Linux (`ubuntu-latest`).
- **Automated `pytest`**: The full test suite in `tests/` runs on every commit pushed to your PR branch.
- **Passing Requirement**: All matrix checks must pass (✅ green checkmark) before your PR can be approved and merged.
- **Debugging CI Failures**:
  1. If any check fails (❌), click **Details** next to the failing check in your PR.
  2. Inspect the pytest failure trace and error messages.
  3. Reproduce and fix the issue locally using `pytest`.
  4. Commit and push the fix to your branch. GitHub Actions will automatically re-run.

---

## 🌿 Git Workflow & Commit Guidelines


### Branch Naming

Create a descriptive feature branch from `main`:

```bash
git checkout -b feat/your-feature-name
# or for bug fixes:
git checkout -b fix/issue-description
```

### Commit Messages

We encourage Conventional Commits:
- `feat: add Relative Strength Index (RSI) indicator`
- `fix: correct handling of division by zero in stochastic oscillator`
- `docs: update quickstart guide in README`
- `test: add edge-case tests for MACD`

### Submitting a Pull Request

1. Push your branch to your GitHub fork:
   ```bash
   git push origin feat/your-feature-name
   ```
2. Open a Pull Request on GitHub against `main`.
3. Provide a clear PR description explaining what was added or changed, why, and how it was tested.
4. Respond to feedback during review.

---

Thank you for contributing to the **Finance Society, NITJ Indicator-Library**! 🚀
