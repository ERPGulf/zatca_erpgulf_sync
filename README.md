# Zatca Erpgulf Sync

App for syncing invoices from external systems into ERPNext and submitting them to ZATCA.

## License

MIT

---

## API Endpoints

### Create Sample Invoice

**Endpoint:**  
`POST {{server}}/zatca_erpgulf_sync.zatca_erpgulf_sync.invoice_sync.create_sample_invoice`

**Description:**  
This API is used to quickly create a sample Sales Invoice in ERPNext for testing ZATCA integration workflows.

**Request Body Example:**
```json
{
  "customer_name": "Test Customer",
  "items": [
    {
      "item_name": "Test Item 1",
      "qty": 2,
      "rate": 100
    }
  ],
  "custom_user_invoice_number": "INV-TEST-001"
}
