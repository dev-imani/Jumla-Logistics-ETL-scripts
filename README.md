# ETL Pipeline for Orders and Users

This project is a beginner-friendly **ETL** (Extract, Transform, Load) program
written in Python.

The program:

1. **Extracts** data from an orders CSV file and from a users API.
2. **Transforms** the data by checking required fields, validating emails and
   numbers, and cleaning values such as city names.
3. **Loads** the valid data into clean CSV and JSON files.
4. Saves invalid records separately so that they can be inspected later.

The project also includes two deliberate error demonstrations. Seeing error
messages for those demonstrations is expected and does not mean that the whole
program failed.

## 1. What you need before starting

You need:

- A computer running Windows, macOS, or Linux.
- Python **3.14 or newer**. The required version is defined in
  [`pyproject.toml`](./pyproject.toml).
- An internet connection when running the users API pipeline.

You can check whether Python is installed by opening a terminal and running:

```text
python --version
```

On some Windows computers, use this command instead:

```text
py --version
```

If the command is not recognised, install Python from
<https://www.python.org/downloads/>. During installation on Windows, select
**Add Python to PATH**.

## 2. Open the project folder

The project folder is:

```text
C:\Users\Michael\Documents\day4-oop-etl
```

To open it in Visual Studio Code:

1. Start Visual Studio Code.
2. Select **File > Open Folder**.
3. Select the `day4-oop-etl` folder.
4. Open the integrated terminal with **Terminal > New Terminal**.

Make sure the terminal is inside the project folder. On Windows, run:

```powershell
cd C:\Users\Michael\Documents\day4-oop-etl
```

You can confirm the folder contents with:

```powershell
dir
```

You should see `main.py`, `pyproject.toml`, `data`, `output`, and `src`.

## 3. Recommended setup with `uv`

This project includes `uv.lock`, so `uv` is the recommended way to install the
project and its dependencies.

### 3.1 Install `uv`

If `uv` is not already installed, follow the instructions at
<https://docs.astral.sh/uv/getting-started/installation/>.

On Windows, you can also install it with PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen the terminal after installation, then check it:

```powershell
uv --version
```

### 3.2 Install the project dependencies

From the project folder, run:

```powershell
uv sync
```

This creates or updates a project virtual environment and installs the
dependencies listed in `pyproject.toml`. The lock file makes the installation
repeatable.

## 4. Alternative setup without `uv`

Use this option if you prefer the standard Python tools or cannot install `uv`.

### 4.1 Create a virtual environment

From the project folder, run:

```powershell
py -3.14 -m venv .venv
```

If `py -3.14` does not work but `python` points to Python 3.14 or newer, run:

```powershell
python -m venv .venv
```

### 4.2 Activate the virtual environment

In Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run this once for the current
terminal window and then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

When activation works, `(.venv)` appears at the beginning of the terminal
line.

### 4.3 Install the dependency

Run:

```powershell
python -m pip install --upgrade pip
python -m pip install requests
```

The application uses `requests` to read users from the API.

## 5. Run the ETL program

### With `uv`

```powershell
uv run python main.py
```

### With the activated virtual environment

```powershell
python main.py
```

The program runs four pipelines in order:

1. **Orders CSV** - reads `data/orders.csv`, validates the orders, and writes
   valid orders to `output/orders_clean.csv`.
2. **Users API** - downloads users from
   `https://jsonplaceholder.typicode.com/users` and writes them to
   `output/users_clean.json`.
3. **Missing CSV demonstration** - intentionally tries to read a file that
   does not exist. This produces an expected error.
4. **Invalid URL demonstration** - intentionally uses an invalid URL. This
   produces another expected error.

The API pipeline requires an internet connection. If the API is unavailable,
the program reports the problem in its summary.

## 6. Understand the terminal output

For each pipeline, the program prints a summary similar to:

```text
Pipeline: Orders CSV
Status: SUCCESS
Extracted: 25
Valid: 20
Rejected: 5
Loaded: 20
```

The fields mean:

- **Extracted**: records read from the source.
- **Valid**: records that passed validation.
- **Rejected**: records with missing, invalid, or non-positive values.
- **Loaded**: records successfully written to an output file.
- **Errors**: problems reading a source or writing an output file.

The final `EXECUTION SUMMARY` combines the results from all pipelines.

## 7. Find the generated files

After running the program, inspect the `output` folder:

| File | Description |
| --- | --- |
| `output/orders_clean.csv` | Valid and cleaned orders from the input CSV |
| `output/users_clean.json` | Valid users downloaded from the API |
| `output/orders_csv/rejected_records.json` | Orders rejected during validation |
| `output/missing_csv_demonstration/rejected_records.json` | Rejected records, if any, from that pipeline |
| `output/invalid_url_demonstration/rejected_records.json` | Rejected records, if any, from that pipeline |

The two demonstration pipelines normally have no rejected records because they
fail during extraction before they receive any records. Their error messages
are shown in the terminal instead.

To view the cleaned orders in PowerShell:

```powershell
Get-Content .\output\orders_clean.csv
```

To view the rejected order details:

```powershell
Get-Content .\output\orders_csv\rejected_records.json
```

To make the JSON easier to read in Visual Studio Code, open
`output/users_clean.json` or `output/orders_csv/rejected_records.json` in the
editor.

## 8. What validation does

For the orders CSV, the program checks that:

- `order_id`, `city`, `quantity`, and `unit_price_kes` are present.
- `quantity` is a number greater than zero.
- `unit_price_kes` is a number greater than zero.
- Email fields contain a valid-looking email address.

It also cleans valid values:

- Removes unnecessary spaces.
- Changes city names to title case, for example `kisumu` becomes `Kisumu`.
- Converts numeric text such as `"4"` to a number.
- Calculates `total_amount` when both quantity and unit price are available.

Invalid records are not silently discarded. They are stored with the reasons
for rejection in `rejected_records.json`.

## 9. Try changing the input data

To practise, make a copy of `data/orders.csv` before editing it. Then try one
change at a time:

1. Change a city such as `Nairobi` to ` nairobi `.
2. Change a quantity to `abc`.
3. Remove an email address.
4. Change a price to `-10`.
5. Run the program again.
6. Compare `output/orders_clean.csv` with
   `output/orders_csv/rejected_records.json`.

The program reads the input file each time it runs and overwrites the generated
output files.

## 10. Project structure

```text
day4-oop-etl/
├── data/
│   └── orders.csv                 Input orders
├── output/                        Generated results
├── src/etl/
│   ├── extractors.py              Reads CSV files and API data
│   ├── transformer.py             Validates and cleans records
│   ├── loader.py                  Writes CSV and JSON files
│   ├── pipeline.py                Connects extract, transform, and load
│   ├── summary.py                 Creates run summaries
│   └── errors.py                  Defines ETL errors
├── main.py                        Program entry point
├── pyproject.toml                 Project settings and dependencies
├── requirements.txt               Dependency list for standard pip workflows
└── uv.lock                        Locked dependency versions for uv
```

The normal ETL flow is:

```text
Source data -> Extract -> Transform/validate -> Load -> Output files
```

## 11. Troubleshooting

### `python` or `py` is not recognised

Install Python 3.14 or newer and make sure Python is added to PATH. Restart
Visual Studio Code after installing it.

### `uv` is not recognised

Install `uv`, close the terminal, open a new terminal, and run:

```powershell
uv --version
```

You can use the alternative virtual-environment setup if you do not want to
install `uv`.

### `ModuleNotFoundError: No module named 'requests'`

With `uv`, run:

```powershell
uv sync
```

With the alternative setup, activate `.venv` and run:

```powershell
python -m pip install requests
```

### The users API fails

Check your internet connection and try again. The API is an external service,
so it may be temporarily unavailable. The orders CSV pipeline can still be
used without the API.

### PowerShell says script execution is disabled

Run the activation command from section 4.2, or use `uv run python main.py`
without manually activating a virtual environment.

## 12. Useful commands

Run the program:

```powershell
uv run python main.py
```

Check the installed project environment:

```powershell
uv sync
```

Deactivate the alternative virtual environment:

```powershell
deactivate
```