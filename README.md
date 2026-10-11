# SEC 10-K reports

Fetch the latest original 10-K for Apple, Meta, Alphabet, Amazon, Netflix, and
Goldman Sachs directly from SEC, then convert the HTML to PDF with WeasyPrint.

The script uses official SEC endpoints. No SEC account, API key, or browser
automation is needed.

## How it works

All application logic is in `reports.py`:

| Function | Purpose |
| --- | --- |
| `read_companies(path)` | Read company names and CIKs from `companies.json`. |
| `fetch_10k(company, user_agent)` | Find the latest 10-K and download its HTML. |
| `convert_to_pdf(report, output_path, user_agent)` | Fetch SEC assets and save a PDF using `reports.css`. |

Running `python reports.py` processes the companies one at a time and saves
`pdfs/<company name>.pdf`. Add or edit entries in `companies.json` to change
the company list. CIKs identify companies without relying on names or tickers.

## Set up your SEC User-Agent

Run all commands from the project folder containing `reports.py`.

Create a local `.env` if one does not already exist:

```sh
[ -f .env ] || cp .env.example .env
```

Edit `.env` and replace the example with your real name and contact email:

```dotenv
SEC_USER_AGENT="Your Name your.email@example.com"
```

The script reads environment variables; it does not load `.env` automatically.
The run commands below load and export this setting. The local `.env` and
generated PDFs are excluded from Git and the Docker image.

Choose one of the following ways to run the script.

## Run in a dev container

1. Start Docker Desktop or Docker Engine.
2. Open this project folder in VS Code with the Dev Containers extension, or
   another editor with Dev Containers support.
3. Open the command palette and select **Dev Containers: Reopen in Container**.
4. Wait for the image to build, then open a terminal inside the container.

The dev container uses the project's Dockerfile. It installs Python 3.12,
the packages in `requirements.txt`, native PDF libraries, and fonts.
The project folder is mounted at `/app`, so edits and generated PDFs are also
available on your host machine.

In the container terminal, run:

```sh
set -a
. ./.env
set +a
python reports.py
```

Opening the dev container does not start the download automatically.
No separate Python package installation is needed inside it. After changing
`requirements.txt` or the Dockerfile, select **Dev Containers: Rebuild Container**.
Changes to Python, CSS, and company files are available through the mounted folder.

## Run with Docker

From a terminal on your host machine, with Docker running:

```sh
docker build -t sec-reports .
set -a
. ./.env
set +a
mkdir -p pdfs
docker run --rm -e SEC_USER_AGENT \
  --mount "type=bind,source=$(pwd)/pdfs,target=/app/pdfs" \
  sec-reports
```

The container runs the script and exits. The mounted `pdfs/` folder keeps the
output on your machine. Rebuild the image after changing the Python code,
stylesheet, company list, or dependencies.

## Run directly on macOS

With Python 3.12 and Homebrew installed:

```sh
brew install pango
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
set -a
. ./.env
set +a
python reports.py
```

If WeasyPrint cannot find Homebrew libraries on Apple Silicon, run
`export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` in the same terminal before
starting the script. Use `/usr/local/lib` for Intel Homebrew.
For other systems, see the
[WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

## Behavior

- Python lists and dictionaries handle filing metadata. The latest report is
  selected by `filingDate`; same-day ties keep the first matching report.
- Only exact `10-K` filings are selected, excluding amendments such as `10-K/A`.
  Older metadata files are searched when needed.
- Requests run sequentially with a 0.25-second pause before each request and
  30-second connection/read timeouts.
- Errors stop the run. There is no automatic retry or resume.
- WeasyPrint downloads referenced assets from HTTPS SEC hosts using the same
  identifying User-Agent. Asset redirects are rejected, and asset failures stop
  conversion.
- `reports.css` controls page layout and spacing. The enlarged layout is scaled
  to Letter paper during PDF rendering. New filings can still need layout review.
- A PDF is written after rendering succeeds. Rerunning replaces existing PDFs.
  Importing `reports` does not download anything.

See [PROMPT_LOG.md](PROMPT_LOG.md) for the AI prompt log and assistance disclosure.

References: [SEC API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces),
[SEC access guidance](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data),
[Dev Containers](https://containers.dev/guide/dockerfile).
