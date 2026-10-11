import json
import os
import time
from pathlib import Path
from urllib.parse import quote, urlsplit

import requests
from weasyprint import CSS, HTML
from weasyprint.urls import URLFetcherResponse


def read_companies(path: str | Path) -> list[dict]:
    """Load the company list from JSON."""
    return json.loads(Path(path).read_text())


def fetch_10k(company: dict, user_agent: str) -> dict:
    """Grab the latest 10-K HTML for one company."""
    cik = str(company["cik"]).zfill(10)
    with requests.Session() as session:
        session.headers.update({"User-Agent": user_agent})

        def get_response(url):
            time.sleep(0.25)
            response = session.get(url, timeout=30)
            response.raise_for_status()
            return response

        def find_10ks(filings):
            # Same index across SEC's lists = same filing.
            reports = []
            for index, form in enumerate(filings["form"]):
                if form == "10-K":
                    report = {field: values[index] for field, values in filings.items()}
                    reports.append(report)
            return reports

        submissions = get_response(f"https://data.sec.gov/submissions/CIK{cik}.json").json()
        if str(submissions["cik"]).zfill(10) != cik:
            raise ValueError(f"SEC returned a different company for {company['name']}")
        reports = find_10ks(submissions["filings"]["recent"])

        # The 10-K might be in an older file, so check those too.
        older_files = sorted(
            submissions["filings"].get("files", []),
            key=lambda filing_file: filing_file["filingTo"],
            reverse=True,
        )
        for filing_file in older_files:
            newest_date = max((report["filingDate"] for report in reports), default="")
            if filing_file["filingTo"] < newest_date:
                break
            history_url = f"https://data.sec.gov/submissions/{filing_file['name']}"
            older_filings = get_response(history_url).json()
            reports.extend(find_10ks(older_filings))

        if not reports:
            raise ValueError(f"No 10-K found for {company['name']}")
        latest = max(reports, key=lambda report: report["filingDate"])
        accession = latest["accessionNumber"].replace("-", "")
        filename = quote(latest["primaryDocument"], safe="")
        filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{filename}"
        response = get_response(filing_url)
        return {
            "company": company["name"],
            "filing_date": latest["filingDate"],
            "url": filing_url,
            "html": response.content.decode("utf-8"),
        }


def convert_to_pdf(report: dict, output_path: str | Path, user_agent: str) -> Path:
    """Save the filing as a PDF, with its SEC images and styles."""

    def fetch_asset(url):
        parsed_url = urlsplit(url)
        hostname = parsed_url.hostname or ""
        is_sec_host = hostname == "sec.gov" or hostname.endswith(".sec.gov")
        if parsed_url.scheme != "https" or not is_sec_host:
            raise ValueError(f"Expected an HTTPS SEC asset: {url}")
        time.sleep(0.25)
        response = requests.get(
            url,
            headers={"User-Agent": user_agent},
            timeout=30,
            allow_redirects=False,
        )
        response.raise_for_status()
        if response.status_code != 200:
            raise ValueError(f"Unexpected asset response: HTTP {response.status_code}")
        return URLFetcherResponse(
            url,
            body=response.content,
            headers={"Content-Type": response.headers.get("Content-Type", "")},
        )

    # Tell WeasyPrint 70 to fail if an asset won't download.
    fetch_asset._fail_on_errors = True

    stylesheet = CSS(filename=Path(__file__).with_name("reports.css"))
    document = HTML(
        string=report["html"],
        base_url=report["url"],
        url_fetcher=fetch_asset,
    )
    pdf = document.write_pdf(stylesheets=[stylesheet], zoom=0.75)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf)
    return output_path


if __name__ == "__main__":
    user_agent = os.environ["SEC_USER_AGENT"]
    for company in read_companies("companies.json"):
        report = fetch_10k(company, user_agent)
        path = convert_to_pdf(report, f"pdfs/{company['name']}.pdf", user_agent)
        print(f"{company['name']}: filed {report['filing_date']} -> {path}")
