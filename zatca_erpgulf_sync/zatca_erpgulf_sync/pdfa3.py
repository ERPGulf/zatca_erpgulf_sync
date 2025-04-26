import os
import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url

@frappe.whitelist(allow_guest=True)
def generate_pdf_a3(invoice, language, letterhead=None, print_format="PDF-A3"):
    """
    Generate and attach a PDF-A3 print of a Sales Invoice.
    
    Args:
        invoice (Document or str): The Sales Invoice doc or its name.
        language (str): Language code for the PDF content.
        letterhead (str, optional): Letterhead to use in the PDF.
        print_format (str, optional): Print format name. Defaults to "PDF-A3".
        
    Returns:
        dict: File doc or file URL of the attached PDF.
    """

    if isinstance(invoice, str):
        invoice = frappe.get_doc("Sales Invoice", invoice)

    original_language = frappe.local.lang
    frappe.local.lang = language

    try:
        # Generate the HTML for the invoice using the given print format
        html = frappe.get_print(
            doctype="Sales Invoice",
            name=invoice.name,
            print_format=print_format,
            no_letterhead=not bool(letterhead),
            letterhead=letterhead,
        )

        # Convert HTML to PDF
        pdf_content = get_pdf(html)

        # Save the file as a new File document (as an attachment)
        file_name = f"{invoice.name}-{print_format}.pdf"
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "attached_to_doctype": "Sales Invoice",
            "attached_to_name": invoice.name,
            "content": pdf_content,
            "is_private": 0,  # Make it public (set to 1 if you want it private)
        })
        file_doc.save(ignore_permissions=True)

        return {
            "file_name": file_doc.file_name,
            "file_url": get_url(file_doc.file_url),
            "file_doc": file_doc.name
        }

    finally:
        frappe.local.lang = original_language
@frappe.whitelist(allow_guest=True)
def simulate_print_pdf_a3(invoice_name, print_format="PDF-A3", letterhead=None, language="en"):
    """
    Simulates clicking the 'Print PDF-A3' button from Python code.
    """
    app_path = frappe.get_app_path("zatca_erpgulf_sync")
    icc_path = app_path + "/sRGB.icc"
    return icc_path
    return frappe.call(
        "zatca_erpgulf.zatca_erpgulf.pdf_a3.embed_file_in_pdf",
        invoice_name=invoice_name,
        print_format=print_format,
        letterhead=letterhead,
        language=language
    )
