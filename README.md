# RankRx PDF Parser

A specialized PDF parser for extracting structured data from medical residency application documents, including ERAS applications, USMLE transcripts, and ECFMG status reports.

## Features

- **ERAS Application Parsing**: Extracts visa and work authorization information
- **USMLE Transcript Analysis**: Parses Step 1 and Step 2 CK scores, attempts, and pass/fail status
- **ECFMG Status Report**: Identifies ECFMG certification status
- **Robust PDF Text Extraction**: Uses PyPDF2 with pdfminer.six fallback for maximum compatibility
- **JSON Output**: Clean, structured data output for easy integration

## Installation

### Prerequisites

- Python 3.6+
- Required packages: `PyPDF2`, `pdfminer.six`

### Install Dependencies

```bash
pip install PyPDF2 pdfminer.six
```

## Usage

### Command Line

```bash
python rankrx_pdf_parser.py /path/to/your/document.pdf
```

### Python API

```python
from rankrx_pdf_parser import parse_pdf

# Parse a PDF file
data = parse_pdf("path/to/document.pdf")
print(data)
```

## Output Format

The parser returns a JSON object with three main sections:

### ERAS Application Section
```json
{
  "eras_visa": {
    "section": "ERAS Application",
    "header_found": true,
    "authorized_to_work_us": "Yes",
    "current_work_authorization": "H-1B",
    "visa_sponsorship_needed": "No",
    "visa_sponsorship_sought": "H-1B",
    "raw_extract": "Authorized to Work in the U.S.: Yes..."
  }
}
```

### USMLE Transcript Section
```json
{
  "usmle_transcript": {
    "section": "USMLE Transcript",
    "header_found": true,
    "step_1": {
      "passed": true,
      "score": "245",
      "failures": 0,
      "attempts": [
        {"date": "01/15/2022", "outcome": "Pass", "score": "245"}
      ]
    },
    "step_2_ck": {
      "passed": true,
      "pass_date": "06/20/2022",
      "score": "258",
      "failures": 0,
      "attempts": [
        {"date": "06/20/2022", "outcome": "Pass", "score": "258"}
      ]
    }
  }
}
```

### ECFMG Status Section
```json
{
  "ecfmg_status": {
    "section": "ECFMG Status Report",
    "header_found": true,
    "ecfmg_certified": "Yes"
  }
}
```

## Supported Document Types

- **ERAS Applications**: Extracts work authorization and visa information
- **USMLE Transcripts**: Parses Step 1 and Step 2 CK examination results
- **ECFMG Status Reports**: Identifies ECFMG certification status

## Technical Details

### PDF Text Extraction
The parser uses a two-tier approach for maximum reliability:
1. **Primary**: PyPDF2 for standard PDF processing
2. **Fallback**: pdfminer.six for complex or problematic PDFs

### Pattern Matching
- Uses regular expressions to identify and extract specific fields
- Handles various date formats and score representations
- Deduplicates multiple attempts and scores
- Identifies pass/fail outcomes and failure counts

### Error Handling
- Graceful fallback between PDF extraction methods
- Handles missing or malformed data gracefully
- Returns structured data even with partial information

## Example

```bash
# Parse a medical residency application PDF
python rankrx_pdf_parser.py "Haruya Hirota header cuts.pdf"
```

This will output structured JSON data containing all extracted information from the PDF.

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests to improve the parser's accuracy and functionality.

## Notes

- The parser is specifically designed for medical residency application documents
- Results may vary depending on PDF quality and formatting
- Some fields may return "Not Available" if the information cannot be reliably extracted
