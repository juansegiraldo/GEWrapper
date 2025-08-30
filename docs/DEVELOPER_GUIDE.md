# Developer Guide - DataWash by Stratesys

## Setup
```powershell
git clone https://github.com/juansegiraldo/GEWrapper.git
cd GEWrapper
.\scripts\activate_env.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Project structure (key parts)
- `streamlit_app.py`: App entrypoint and step navigation
- `components/`: UI components (upload, profiling, configure, validate, results)
- `utils/`: GE helpers, data processing, reporting
- `config/app_config.py`: Central configuration
- `docs/`: Documentation
- `tests/`: Pytest-based tests
- `scripts/`: Helper scripts (activate env, start_app)

## Core modules
- `utils/ge_helpers.py`: Great Expectations context, suite creation, validation
- `components/expectation_builder.py`: Build expectations (built-ins + custom SQL)
- `components/sql_query_builder.py`: UI for custom SQL expectations
- `components/results_display.py`: Results, charts, exports
- `components/failed_records_generator.py`: Advanced failed-records export

## Development workflow
- Add features in `components/` and supporting logic in `utils/`
- Keep `AppConfig` as source of truth for UI/limits/templates
- Prefer small, composable functions; avoid deep nesting

## Testing
```powershell
python -m pytest tests/ -v
python -m pytest tests/ --cov=components --cov-report=html
```

## Conventions
- Python 3.8+
- Type hints for public APIs
- Follow PEP 8; format with Black; lint with Flake8
- Guard clauses and explicit error messages
- No inline comments for obvious code; add short docstrings for complex logic

## GE compatibility notes
- `ge_helpers.py` uses multiple code paths to work across GE 0.17–0.18+
- When adding new expectations, ensure both config dict and object forms are handled

## Useful scripts
- `.\scripts\activate_env.ps1`: Activate venv
- `.\scripts\start_app.bat`: Quick run app

## Contributing
- Fork, branch, PR; include tests and docs for changes
- Keep docs in sync (User Guide, Tutorials, Configuration)
