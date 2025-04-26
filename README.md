# ZATCA Invoice API Integration

This document provides instructions for integrating with the ZATCA Invoice APIs for submitting sales invoices and generating PDF/A-3 invoices with embedded XML.



---

## Submit Sales Invoice

This API allows third-party systems to submit invoices to ZATCA through an intermediary server. It handles both initial submissions and subsequent status checks.

### Request

```bash
curl --location 'https://zatca.erpgulf.com:3717/api/method/zatca_erpgulf_sync.zatca_erpgulf_sync.invoice_sync.create_simple_sales_invoice' \
--header 'Content-Type: application/json' \
--header 'Cookie: full_name=Guest; sid=Guest; system_user=yes; user_id=Guest; user_image=' \
--data '{
  "customer_name": "Grant Plastkicus Lfdtd.",
  "custom_user_invoice_number": "2pp8235m5k5k2h4525888l238853",
  "posting_date": "2025-11-06",
  "due_date": "2025-11-20",
  "discount_amount": 5,
  "discount_percentage": 10,
  "tax_category": "Standard",
  "is_b2c": false,
  "items": [
    {
      "item_name": "Laptop",
      "quantity": 1,
      "rate": 100,
      "income_account": "4110 - Sales - ZA",
      "description": "High-quality T-shirt",
      "item_tax_template": "15 - ZA"
    }
  ],
  "taxes": [
    {
      "charge_type": "On Net Total",
      "account_head": "5118 - Expenses Included In Valuation - ZA",
      "description": "VAT"
    }
  ]
}'
# ZATCA Invoice PDF/A-3 Generation API

This document provides instructions for integrating with the ZATCA Invoice PDF/A-3 Generation API. The API generates a PDF/A-3 version of a Sales Invoice by accepting the invoice number, print format, and language as input parameters. The generated PDF includes the associated XML embedded in the PDF.

## Table of Contents

1. [Generate PDF/A-3 Invoice](#generate-pdfa-3-invoice)

---

## Generate PDF/A-3 Invoice

This API allows users to generate a PDF/A-3 file of a Sales Invoice. The generated PDF will contain the associated XML, making it compliant with ZATCA standards for electronic invoicing.

### Request

```bash
curl --location --request GET 'https://zatca.erpgulf.com:3717/api/method/zatca_erpgulf_sync.zatca_erpgulf_sync.invoice_sync.embed_file_in_pdf' \
--header 'Content-Type: application/json' \
--header 'Cookie: full_name=Guest; sid=Guest; system_user=yes; user_id=Guest; user_image=' \
--data '{
  "invoice_name": "ACC-SINV-2025-00603",
  "print_format": "Claudion Invoice Format",
  "language": "en"
}'
