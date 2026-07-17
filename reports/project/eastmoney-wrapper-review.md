# Eastmoney wrapper review

## Decision

`EASTMONEY-001` — **adapt**.

The archive is a mixed repository of four credentialed tools. The source commit is
`61cfae47451f797d95ae4553ffcc7569b9957e7d`; its repository code declares an MIT
license (copyright `meission`, 2026). That license applies to the wrapper code,
not automatically to the vendor API, returned financial data, or downstream
redistribution rights. API authorization and data-use terms are therefore
`unknown`, and the catalog remains `review_required` / `not_requested`.

## Static evidence

- The data endpoint is `https://mkapi2.dfcfs.com/finskillshub/api/claw/query`.
- The wrapper reads `MX_APIKEY` and sends it as an `apikey` header.
- The repository also contains search, stock-screen, and self-select endpoints;
  self-select can mutate an account watchlist and is not adopted.
- The original implementation uses third-party `requests`, `pandas`, and
  `openpyxl`, writes under `/root/.openclaw`, and accepts arbitrary natural-language
  query text. None of those implementation behaviors are installed or executed.
- The candidate documentation and parser show two inconsistent response paths
  (`data.dataTableDTOList` versus a nested `searchDataResultDTO` path). The
  adapted parser accepts only those two bounded shapes and fails closed on
  ambiguous identity, duplicate keys, non-finite JSON, oversized bodies, and
  non-scalar table values.

## InvestKit adaptation

`src/investkit/providers/eastmoney.py` exposes only fixed, symbol-scoped
company-profile, financial-statement, and valuation queries. It requires both an
`MX_APIKEY` environment variable and explicit network permission, enforces the
exact HTTPS host/path, refuses redirects, bounds request/response sizes, and
never logs or includes credential values in errors. Offline tests use a recording
transport; no live Eastmoney request has been made because the credential is not
configured and catalog approval has not been requested.

## Remaining approval gate

An operator must verify the MX API subscription, permitted use of returned data,
retention/redistribution terms, and whether the credential is authorized for this
project. Only after that review should the catalog asset be promoted to
`approved`; a real `603868.SH` financial/valuation run then requires setting
`MX_APIKEY` outside the repository and passing `--allow-network`.
