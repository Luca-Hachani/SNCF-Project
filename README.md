## SNCF Project - IADATA701

### Students
**HACHANI Luca**

**LABOUDIGUE Jérémie**

**SEGUIN Augustin**

This project consists of developing an interactive web application powered by a modular Python backend.

---

### 1. Object-Oriented Programming (`Traveler` & `Trip`)
We developed two dedicated `@dataclass` inside `src/sncf_project/models/`:
* **`Traveler` (`traveler.py`):** Encapsulates user trip criteria (`departure_city`, `departure_airport`, `trip_date`) and resolves the **3 closest active TGV departure stations** from French commune coordinates (`compute_departure_station()`).
* **`Trip` (`trip_SNCF.py`):** Found a rail itinerary from a candidate departure station to an airport hub using a directed graph (`networkx.DiGraph`), computing the optimal path (`set_shortest_path()`), destination station (`set_arrival_station()`), and filter by the punctuality leg-by-leg punctuality (`set_trip_reliability()`).

---

### 2. Interactive Streamlit Web Application & Data Storytelling
To run on your computer :

`streamlit run src/sncf_project/app.py`


Built with multi-page navigation (`st.navigation` and `st.Page`), the interface guides users from macro-level network insights to personalized trip planning:
* **Data Storytelling (`homepage.py` & `data_visualization.py`):** Combines key regularity KPIs (`st.metric`), interactive Plotly delay/cancellation timelines, delay root-cause breakdowns (infrastructure, rolling stock, external causes, traffic management), and a 3D/2D geospatial PyDeck station map (`ScatterplotLayer` & `TextLayer`).
* **Interactive Widgets (`search_form.py`):** Integrates form validation (`st.form`), date/airport selectors, and one-click browser GPS auto-detection (`streamlit-geolocation`) to automatically pre-select the user's nearest commune.

---

### 3. Static Type Hinting
All functions, methods, `@property` getters, and dataclass attributes are annotated with modern Python type hints (`str`, `float`, `datetime.date`, `pd.DataFrame`, `list[str] | None`, `Traveler | None`) to improve IDE autocompletion, self-documentation, and static verification.

---

### 4. Structured Logging Management
Observability is centralized via a YAML configuration (`configs/logging.yaml`) initialized by `setup_logging()`:
* **Dedicated Loggers:** Separates backend/data pipeline events (`utils`, `sncf_project.models.*`) from frontend UI interactions (`streamlit_app`, `sncf_project.pages.*`).
* **Rotating Log Files:** Routes logs to `logs/backend.log`, `logs/frontend.log`, and `logs/error.log` using `RotatingFileHandler` (10 MB max size with automatic backups) so disk usage remains bounded.

---

### 5. PEP 8 Compliance & Linting (`ruff`)
Code formatting, import sorting, naming conventions, and Google-style docstrings strictly adhere to **PEP 8** and are enforced automatically using **`ruff`** (`ruff check` and `ruff format`).

---

### 6. Explicit Exception Handling
Rather than relying on broad `except Exception:` blocks, the application catches and logs specific failure modes with graceful UI fallbacks (`st.error` / `st.warning` / `st.stop()`):
* **Data I/O & Parsing:** `FileNotFoundError`, `pd.errors.EmptyDataError`, and `pd.errors.ParserError` in `load_dataset()`.
* **Domain & Graph Lookups:** `ValueError` when a departure city is missing from the communes dataset or datasets are unloaded, and `(nx.NodeNotFound, nx.NetworkXNoPath)` when no rail connection exists between two stations.

---

### 7. Security Best Practices
* **Path Traversal Prevention & Safe Path Resolution:** Dataset and configuration paths are resolved dynamically relative to the package root (`pathlib.Path(__file__).resolve()`) rather than trusting raw user-supplied file paths.
* **Input Sanitization & Validation:** All user inputs (city names, IATA airport codes, dates, GPS coordinates) are validated against controlled option lists (`FRENCH_AIRPORTS`, `df_communes`) before computation, and numeric conversions use safe coercion (`pd.to_numeric(..., errors="coerce")`).
* **Zero Hardcoded Secrets & Privacy-Aware Logging:** No credentials or API keys are stored in source control, and visitor request metadata (`st.context`) is logged strictly for operational diagnostics without exposing sensitive personal data.

---

### 8. Unit & Integration Testing (`pytest` & `AppTest`)
The `tests/` suite validates backend logic. 

Unfortunately, we did not manage to deploy tests for the web pages inside `src/sncf_project/pages/`

---

### 9. Test Coverage (`pytest-cov`)
Test execution is tracked with `pytest-cov` (`uv run pytest --cov=src/sncf_project --cov-report=term-missing`) to verify line and branch coverage across core utilities, domain models, configuration loaders, and Streamlit page modules.

---

### 10. Automated Documentation (`Sphinx`)
All modules, classes, and functions include standardized **Google-style docstrings** (`Args`, `Returns`, `Raises`, `Attributes`, `Example`), allowing **Sphinx** (`sphinx.ext.autodoc` + `sphinx.ext.napoleon`) to automatically generate browsable HTML API documentation directly from the codebase.

---

### 11. CI/CD Pipeline (`GitHub Actions`)
A GitHub Actions workflow (`.github/workflows/ci.yml`) automates quality checks on every push and pull request targeting `develop` and `main`:
1. Sets up the Python environment and installs dependencies reproducibly with **`uv`**.
2. Runs **`ruff`** linting and formatting checks to enforce PEP 8 compliance.
3. Executes the **`pytest` + `pytest-cov`** test suite to prevent regressions before merging.