
import json
from werkzeug.wrappers import Response
import frappe
import base64


# @frappe.whitelist(allow_guest=True)
# def create_simple_sales_invoice(
#     customer_name,
#     items,
#     posting_date,
#     due_date,
#     custom_user_invoice_number,
#     taxes=None,
#     is_b2c=False,
#     discount_amount=0,
#     discount_percentage=0,
#     tax_category=None,
# ):
#     if not items:
#         return Response(
#             json.dumps({"data": "items information not provided"}),
#             status=404,
#             mimetype="application/json",
#         )

#     # Check for duplicate custom_user_invoice_number
#     # existing_invoice = frappe.get_all("Sales Invoice", filters={"custom_user_invoice_number": custom_user_invoice_number})
#     # if existing_invoice:
#     #     return Response(
#     #         json.dumps({"message": "Duplicate invoice number"}),
#     #         status=409,
#     #         mimetype='application/json'
#     #     )
#     existing_invoice = frappe.get_all(
#         "Sales Invoice",
#         filters={"custom_user_invoice_number": custom_user_invoice_number},
#     )
#     if existing_invoice:
#         existing_doc = frappe.get_doc("Sales Invoice", existing_invoice[0]["name"])
#         xml_content = download_xml(existing_doc.name)
#         xml_str = xml_content.decode("utf-8")
#         qr_image_content = get_invoice_qr_image(existing_doc.name)
#         # qr_image_base64 = base64.b64encode(qr_image_content).decode("utf-8")

#         existing_response = {
#             "invoice_id": existing_doc.name,
#             "uuid": existing_doc.custom_uuid,
#             "zatca_full_response": existing_doc.custom_zatca_full_response,
#             "xml": xml_str,
#             "qr_image": qr_image_content,
#         }

#         return Response(
#             json.dumps(
#                 {"data": existing_response, "message": "Duplicate invoice reused"}
#             ),
#             status=200,
#             mimetype="application/json",
#         )

    
#     customer_details = frappe.get_all(
#         "Customer", fields=["name"], filters={"customer_name": customer_name}
#     )
#     if not customer_details:
#         try:
#             # Create the customer
#             new_customer = frappe.get_doc(
#                 {
#                     "doctype": "Customer",
#                     "customer_name": customer_name,
#                     "customer_type": "Individual",
#                     "customer_group": "Demo Customer Group",
#                     "territory": "All Territories",
#                     "custom_b2c": is_b2c,  # Set custom B2C checkbox
#                 }
#             )
#             new_customer.insert(ignore_permissions=True)
#             frappe.db.commit()
#             customer_id = new_customer.name

#             # Create default address for the new customer
#             default_address = frappe.get_doc(
#                 {
#                     "doctype": "Address",
#                     "address_title": customer_name,
#                     "address_type": "Billing",
#                     "customer": customer_id,
#                     "address_line1": "riyadh",
#                     "address_line2": "8659",
#                     "city": "riyadh",
#                     "state": "Saudi Arabia",
#                     "country": "Saudi Arabia",
#                     "pincode": "87695",
#                     "custom_building_number": "4444",
                    
#                     "links": [
#                         {"link_doctype": "Customer", "link_name": customer_id},
                        
#                     ],
#                 }
#             )
#             default_address.insert(ignore_permissions=True)
#             frappe.db.commit()
#             # Set as customer's primary address
#             frappe.db.set_value(
#                 "Customer",
#                 customer_id,
#                 "customer_primary_address",
#                 default_address.name,
#             )
#             frappe.db.commit()

#         except Exception as e:
#             return Response(
#                 json.dumps(
#                     {"message": f"Failed to create customer or address: {str(e)}"}
#                 ),
#                 status=404,
#                 mimetype="application/json",
#             )
#     else:
#         customer_id = customer_details[0]["name"]

#     # Prepare items with income accounts, descriptions, and tax templates
#     # invoice_items = []

#     # for item in items:
#     #     item_code = item["item_name"]
#     #     quantity = item.get("quantity", 0)
#     #     rate = item.get("rate", 0)
#     #     income_account = item.get("income_account")
#     #     description = item.get("description", "No description provided")
#     #     item_tax_template = item.get("item_tax_template", "")

#     #     # Validate income account
#     #     if income_account and not frappe.db.exists("Account", income_account):
#     #         return Response(json.dumps({"message": f"Income Account '{income_account}' not found"}), status=404, mimetype='application/json')

#     #     invoice_item = {
#     #         "item_name": item_code,
#     #         "qty": quantity,
#     #         "rate": rate,
#     #         "price_list_rate":rate,
#     #         "income_account": income_account,
#     #         "description": description,
#     #         "item_tax_template": item_tax_template
#     #     }
#     #     invoice_items.append(invoice_item)
#     invoice_items = []
#     for item in items:
#         item_code = item["item_name"]
#         quantity = item.get("quantity", 0)
#         rate = item.get("rate", 0)
#         income_account = item.get("income_account")
#         description = item.get("description", "No description provided")
#         item_tax_template = item.get("item_tax_template", "")

#         # Create item if not exists
#         if not frappe.db.exists("Item", {"item_name": item_code}):
#             try:
#                 new_item_doc = frappe.get_doc(
#                     {
#                         "doctype": "Item",
#                         "item_code": item_code,
#                         "item_name": item_code,
#                         "item_group": "All Item Groups",
#                         "stock_uom": "Nos",
#                         "is_sales_item": 1,
#                         "description": description,
#                     }
#                 )
#                 new_item_doc.insert(ignore_permissions=True)
#                 frappe.db.commit()

#             except Exception as e:
#                 return Response(
#                     json.dumps(
#                         {"message": f"Failed to create item '{item_code}': {str(e)}"}
#                     ),
#                     status=500,
#                     mimetype="application/json",
#                 )

#         if income_account and not frappe.db.exists("Account", income_account):
#             return Response(
#                 json.dumps({"message": f"Income Account '{income_account}' not found"}),
#                 status=404,
#                 mimetype="application/json",
#             )

#         invoice_item = {
#             "item_name": item_code,
#             "qty": quantity,
#             "rate": rate,
#             "price_list_rate": rate,
#             "income_account": income_account,
#             "description": description,
#             "item_tax_template": item_tax_template,
#         }
#         invoice_items.append(invoice_item)
#     # invoice_items = []
#     # for item in items:
#     #     item_code = item["item_name"]
#     #     quantity = item.get("quantity", 0)
#     #     rate = item.get("rate", 0)
#     #     income_account = item.get("income_account")
#     #     description = item.get("description", "No description provided")
#     #     item_tax_template = item.get("item_tax_template", "")

#     #     if income_account and not frappe.db.exists("Account", income_account):
#     #         return Response(json.dumps({"message": f"Income Account '{income_account}' not found"}), status=404, mimetype='application/json')

#     #     invoice_item = {
#     #         "item_name": item_code,
#     #         "qty": quantity,
#     #         "rate": rate,
#     #         "price_list_rate": rate,
#     #         "income_account": income_account,
#     #         "description": description,
#     #         "item_tax_template": item_tax_template
#     #     }
#     #     invoice_items.append(invoice_item)
#     # Prepare taxes if provided, with category and additional fields
#     taxes_list = []
#     if taxes:
#         for tax in taxes:
#             charge_type = tax.get("charge_type")
#             account_head = tax.get("account_head")
#             rate = tax.get("rate")
#             description = tax.get("description", "No description provided")

#             if charge_type and account_head and rate is not None:
#                 taxes_list.append(
#                     {
#                         "charge_type": charge_type,
#                         "account_head": account_head,
#                         "rate": rate,
#                         "description": description,
#                         "tax_category": tax_category,
#                     }
#                 )
#     # Create Sales Invoice with discounts and tax information
#     try:
#         new_invoice = frappe.get_doc(
#             {
#                 "doctype": "Sales Invoice",
#                 "customer": customer_id,
#                 "posting_date": posting_date,
#                 "due_date": due_date,
#                 "custom_user_invoice_number": custom_user_invoice_number,
#                 "custom_zatca_tax_category": tax_category,  # Include custom field
#                 "items": invoice_items,
#                 "taxes": taxes_list,
#                 "additional_discount_percentage": discount_percentage,
#                 "discount_amount": discount_amount,
#                 "apply_discount_on": "Net Total",
#             }
#         )

#         new_invoice.insert(ignore_permissions=True)
#         new_invoice.submit()
#         new_invoice.reload()  # Check the ZATCA status after submitting the invoice
#         # If ZATCA status is 503, return a 503 response
#         if new_invoice.custom_zatca_status == "503 Service Unavailable":
#             return Response(
#                 json.dumps(
#                     {
#                         "data": {
#                             "invoice_id": new_invoice.name,
#                             "uuid": new_invoice.custom_uuid,
#                             "zatca_full_response": new_invoice.custom_zatca_full_response,
#                         },
#                         "message": "Service Unavailable",
#                     }
#                 ),
#                 status=503,
#                 mimetype="application/json",
#             )
#         if not new_invoice.custom_zatca_full_response:
#             return Response(
#                 json.dumps(
#                     {
#                         "data": {
#                             "invoice_id": new_invoice.name,
#                             "uuid": new_invoice.custom_uuid,
#                             "zatca_full_response": None,
#                         },
#                         "message": "Waiting for response",
#                     }
#                 ),
#                 status=202,  # 202 Accepted (still processing)
#                 mimetype="application/json",
#             )
#         xml_content = download_xml(new_invoice.name)
#         xml_str = xml_content.decode("utf-8")
#         # Prepare and return response with invoice detail if no 503 error
#         qr_image_content = get_invoice_qr_image(new_invoice.name)
#         # qr_image_base64 = base64.b64encode(qr_image_content).decode("utf-8")

#         customer_info = {
#             "invoice_id": new_invoice.name,
#             "uuid": new_invoice.custom_uuid,
#             "zatca_full_response": new_invoice.custom_zatca_full_response,
#             "xml": xml_str,
#             "qr_image": qr_image_content,
#         }
#         return Response(
#             json.dumps({"data": customer_info}), status=200, mimetype="application/json"
#         )

#     except Exception as e:
#         return Response(
#             json.dumps({"message": str(e)}), status=404, mimetype="application/json"
#         )

@frappe.whitelist(allow_guest=True)
def create_simple_sales_invoice(
    customer_name,
    items,
    posting_date,
    due_date,
    custom_user_invoice_number,
    taxes=None,
    is_b2c=False,
    discount_amount=0,
    tax_category=None,
    is_return=0,  # 👈 Credit Note flag
    return_against=None,
    custom_exemption_reason_code="Standard 15%",  # 👈 Invoice to link back (mandatory for credit note)
):
    if not items:
        return Response(
            json.dumps({"data": "Items information not provided"}),
            status=404,
            mimetype="application/json",
        )
    intermediate_settings = frappe.get_single("Intermediate Server Setting")
    default_items = intermediate_settings.get("items") or []
    default_taxes = intermediate_settings.get("taxes") or []

    # Check for duplicate invoice by custom_user_invoice_number
    existing_invoice = frappe.get_all(
        "Sales Invoice",
        filters={"custom_user_invoice_number": custom_user_invoice_number},
    )
    if existing_invoice:
        existing_doc = frappe.get_doc("Sales Invoice", existing_invoice[0]["name"])
        xml_content = download_xml(existing_doc.name)
        xml_str = xml_content.decode("utf-8")
        qr_image_content = get_invoice_qr_image(existing_doc.name)

        existing_response = {
            "invoice_id": existing_doc.name,
            "uuid": existing_doc.custom_uuid,
            "zatca_full_response": existing_doc.custom_zatca_full_response,
            "xml": xml_str,
            "qr_image": qr_image_content,
        }

        return Response(
            json.dumps(
                {"data": existing_response, "message": "Duplicate invoice reused"}
            ),
            status=200,
            mimetype="application/json",
        )

    # Check if customer exists, else create
    customer_details = frappe.get_all(
        "Customer", fields=["name"], filters={"customer_name": customer_name}
    )
    tax_id = intermediate_settings.tax_id if is_b2c else ""
    if not customer_details:
        try:
            new_customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_name,
                "customer_type": "Individual",
                "customer_group": "Demo Customer Group",
                "territory": "All Territories",
                "custom_b2c": is_b2c,
                "custom_buyer_id_type":"NAT",
                "custom_buyer_id" :"786531",
                "tax_id": tax_id
            })
            new_customer.insert(ignore_permissions=True)
            frappe.db.commit()

            customer_id = new_customer.name

            # Create default address
            default_address = frappe.get_doc({
                "doctype": "Address",
                "address_title": customer_name,
                "address_type": "Billing",
                "customer": customer_id,
                "address_line1": "riyadh",
                "address_line2": "8659",
                "city": "riyadh",
                "state": "Saudi Arabia",
                "country": "Saudi Arabia",
                "pincode": "87695",
                "custom_building_number": "4444",
                "links": [{"link_doctype": "Customer", "link_name": customer_id}],
            })
            default_address.insert(ignore_permissions=True)
            frappe.db.commit()

            frappe.db.set_value(
                "Customer",
                customer_id,
                "customer_primary_address",
                default_address.name,
            )
            frappe.db.commit()

        except Exception as e:
            return Response(
                json.dumps({"message": f"Failed to create customer: {str(e)}"}),
                status=404,
                mimetype="application/json",
            )
    else:
        customer_id = customer_details[0]["name"]

    # Prepare Invoice Items
    invoice_items = []
    for item in items:
        item_name = item["item_name"]
    
    # Fetch the item_code from the Item Doctype based on item_name
        item_docname = frappe.get_value("Item", {"item_name": item_name}, "name")
        if not item_docname:
            try:
                new_item = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": item_name,
                    "item_name": item_name,
                    "item_group": "All Item Groups",
                    "stock_uom": "Nos",
                    "is_sales_item": 1,
                    "description": item.get("description", "No description provided"),
                }).insert(ignore_permissions=True)
                frappe.db.commit()
                item_docname = new_item.name
            except Exception as e:
                return Response(
                    json.dumps({"message": f"Failed to create item '{item_name}': {str(e)}"}),
                    status=500,
                    mimetype="application/json",
                )


        quantity = item.get("quantity", 0)
        discount_amount_item = item.get("discount_amount", 0)
        rate = item.get("rate", 0)
        # income_account = item.get("income_account")
        income_account = item.get("income_account") or (default_items[0].get("income_account") if default_items else None)
        description = item.get("description", "No description provided")
        item_tax_template = item.get("item_tax_template", "")
        final_rate = rate - discount_amount_item
        if final_rate < 0:
            final_rate = 0

        # Auto-create item if not exists
        # if not frappe.db.exists("Item", {"item_name": item_name}):
        #     try:
        #         frappe.get_doc({
        #             "doctype": "Item",
        #             "item_code": item_name,
        #             "item_name": item_name,
        #             "item_group": "All Item Groups",
        #             "stock_uom": "Nos",
        #             "is_sales_item": 1,
        #             "description": description,
        #         }).insert(ignore_permissions=True)
        #         frappe.db.commit()
        #     except Exception as e:
        #         return Response(
        #             json.dumps({"message": f"Failed to create item '{item_name}': {str(e)}"}),
        #             status=500,
        #             mimetype="application/json",
        #         )

        if income_account and not frappe.db.exists("Account", income_account):
            return Response(
                json.dumps({"message": f"Income Account '{income_account}' not found"}),
                status=404,
                mimetype="application/json",
            )

        if is_return:
            quantity = -abs(quantity)  # Credit note quantities must be negative

        invoice_item = {
            "item_name": item_name,
            "item_code":item_docname,
            "qty": quantity,
            "rate": final_rate,
            "price_list_rate": rate,
            "income_account": income_account,
            "description": description,
            "grant_commission" : 1,
            "item_tax_template": item_tax_template,
            "discount_amount": discount_amount_item,
        }
        invoice_items.append(invoice_item)

    # Prepare Taxes
    taxes_list = []
    if taxes:
        for tax in taxes:
            # charge_type = tax.get("charge_type")
            charge_type = tax.get("charge_type") or (default_taxes[0].get("charge_type") if default_taxes else None)
            account_head = tax.get("account_head") or (default_taxes[0].get("account_head") if default_taxes else None)
            rate = tax.get("rate")
            description = tax.get("description", "No description provided")
            included_in_print_rate=tax.get("included_in_print_rate")


            if charge_type and account_head and rate is not None:
                taxes_list.append({
                    "charge_type": charge_type,
                    "account_head": account_head,
                    "rate": rate,
                    "description": description,
                    "tax_category": tax_category,
                    "included_in_print_rate" :included_in_print_rate,
                })

    # Validate if return_against is needed
    if is_return and not return_against:
        return Response(
            json.dumps({"message": "return_against (original invoice id) is required for credit notes"}),
            status=400,
            mimetype="application/json",
        )

    try:
        # Create Sales Invoice
        invoice_data = {
            "doctype": "Sales Invoice",
            "customer": customer_id,
            "posting_date": posting_date,
            "due_date": due_date,
            "custom_user_invoice_number": custom_user_invoice_number,
            "custom_zatca_tax_category": tax_category,
            "custom_exemption_reason_code": custom_exemption_reason_code,
            "items": invoice_items,
            "taxes": taxes_list,
            "discount_amount": discount_amount,
            "apply_discount_on": "Net Total",
            "is_return": 1 if is_return else 0,
        }
    

        if is_return:
            invoice_data["return_against"] = return_against  # 👈 Link to original Sales Invoice

        new_invoice = frappe.get_doc(invoice_data)

        new_invoice.insert(ignore_permissions=True)
    
        new_invoice.submit()
        new_invoice.reload()

        # Handle ZATCA response
        if new_invoice.custom_zatca_status == "503 Service Unavailable":
            return Response(
                json.dumps({
                    "data": {
                        "invoice_id": new_invoice.name,
                        "uuid": new_invoice.custom_uuid,
                        "zatca_full_response": new_invoice.custom_zatca_full_response,
                    },
                    "message": "Service Unavailable",
                }),
                status=503,
                mimetype="application/json",
            )

        if not new_invoice.custom_zatca_full_response:
            return Response(
                json.dumps({
                    "data": {
                        "invoice_id": new_invoice.name,
                        "uuid": new_invoice.custom_uuid,
                        "zatca_full_response": None,
                    },
                    "message": "Waiting for response",
                }),
                status=202,
                mimetype="application/json",
            )

        # Download XML and QR Code
        xml_content = download_xml(new_invoice.name)
        xml_str = xml_content.decode("utf-8")
        qr_image_content = get_invoice_qr_image(new_invoice.name)

        response_data = {
            "invoice_id": new_invoice.name,
            "uuid": new_invoice.custom_uuid,
            "zatca_full_response": new_invoice.custom_zatca_full_response,
            "xml": xml_str,
            "qr_image": qr_image_content,
        }

        return Response(
            json.dumps({"data": response_data}),
            status=200,
            mimetype="application/json",
        )

    except Exception as e:
        return Response(
            json.dumps({"message": str(e)}),
            status=404,
            mimetype="application/json",
        )




@frappe.whitelist(allow_guest=True)
def download_image(new_invoice):
    # Specify the file path of the XML file
    # file_path = "zatca.erpgulf.com/private/files/QR_image_ACC-SINV-2024-01233.png"
    new_invoice = frappe.get_doc("Sales Invoice", new_invoice)

    file_path = frappe.local.site + new_invoice.ksa_einv_qr

    # Open the file in binary mode and read the content
    with open(file_path, "rb") as file:
        file_content = file.read()
    return file_content
    response = Response(file_content, content_type="image/png")
    # Set the headers to indicate that the file is a downloadable PNG
    response.headers["Content-Disposition"] = f"inline; filename={file_path}"
    return response


@frappe.whitelist(allow_guest=True)
def download_xml(new_invoice):
    # Specify the file path of the XML file
    # file_path = "zatca.erpgulf.com/private/files/Cleared xml file ACC-SINV-2024-01232.xml"
    new_invoice = frappe.get_doc("Sales Invoice", new_invoice)

    file_path = frappe.local.site + new_invoice.custom_ksa_einvoicing_xml
    # Open the file in binary mode and read the content
    with open(file_path, "rb") as file:
        file_content = file.read()
    return file_content
    response = Response(file_content, content_type="application/xml")
    # Set the headers to indicate that the file is a downloadable PNG
    response.headers["Content-Disposition"] = f"inline; filename={file_path}"
    return response


def get_file_path(path):
    return frappe.get_site_path(
        (("" if "/private/" in path else "/public") + path).strip("/")
    )


@frappe.whitelist(allow_guest=True)
def get_invoice_by_custom_number(custom_user_invoice_number):
    # Check if the Sales Invoice with the given custom_user_invoice_number exists
    existing_invoice = frappe.get_all(
        "Sales Invoice",
        filters={"custom_user_invoice_number": custom_user_invoice_number},
        fields=["name", "docstatus"],
    )

    if not existing_invoice:
        # If the invoice does not exist, return an error response
        return Response(
            json.dumps({"message": "Invoice not found"}),
            status=404,
            mimetype="application/json",
        )

    # Get the first matched invoice
    invoice_name = existing_invoice[0]["name"]
    docstatus = existing_invoice[0]["docstatus"]

    if docstatus != 1:  # docstatus 1 means the invoice is submitted
        # If the invoice exists but is not submitted, return an error response
        return Response(
            json.dumps({"message": "Invoice exists but is not submitted"}),
            status=400,
            mimetype="application/json",
        )

    # If the invoice exists and is submitted, retrieve detailed information
    try:
        new_invoice = frappe.get_doc("Sales Invoice", invoice_name)

        # Check if ZATCA status is 503
        if new_invoice.custom_zatca_status == "503 Service Unavailable":
            return Response(
                json.dumps(
                    {
                        "data": {
                            "invoice_id": new_invoice.name,
                            "uuid": new_invoice.custom_uuid,
                            "zatca_full_response": new_invoice.custom_zatca_full_response,
                        },
                        "message": "Service Unavailable",
                    }
                ),
                status=503,
                mimetype="application/json",
            )

        # Retrieve XML and QR code as base64 for response
        xml_content = download_xml(new_invoice.name)
        xml_str = xml_content.decode("utf-8")

        qr_image_content = download_image(new_invoice.name)
        qr_image_base64 = base64.b64encode(qr_image_content).decode("utf-8")

        # Prepare response data
        customer_info = {
            "invoice_id": new_invoice.name,
            "uuid": new_invoice.custom_uuid,
            "zatca_full_response": new_invoice.custom_zatca_full_response,
            "xml": xml_str,
            "qr_image": qr_image_base64,
        }

        return Response(
            json.dumps({"data": customer_info}), status=200, mimetype="application/json"
        )

    except Exception as e:
        return Response(
            json.dumps({"message": str(e)}), status=500, mimetype="application/json"
        )


from datetime import datetime
import os
import pikepdf
import frappe
import frappe.utils
from frappe.utils.pdf import get_pdf
from frappe.utils import get_site_path, get_url
from frappe.model.document import Document


def generate_invoice_pdf(invoice, language, letterhead=None, print_format=None):
    """Function for generating invoice PDF based on the provided print format, letterhead, and language."""
    # Set the language for the PDF generation
    invoice_name = invoice.name
    original_language = frappe.local.lang
    frappe.local.lang = language

    # Generate HTML content for the invoice
    frappe.set_user("Administrator")
    html = frappe.get_print(
        doctype="Sales Invoice",
        name=invoice_name,  # Use the invoice's name directly
        print_format=print_format,  # Use the selected print format
        no_letterhead=not bool(letterhead),  # Use letterhead only if specified
        letterhead=letterhead,  # Specify the letterhead if provided
    )
    # Revert back to the original language
    frappe.local.lang = original_language

    # Generate PDF content from the HTML
    pdf_content = get_pdf(html)

    # Set the path for saving the generated PDF
    site_path = frappe.local.site  # Get the site path
    file_name = f"{invoice_name}.pdf"
    file_path = os.path.join(site_path, "private", "files", file_name)

    # Write the PDF content to the file
    with open(file_path, "wb") as pdf_file:
        pdf_file.write(pdf_content)

    # Return the path of the generated PDF file
    return file_path


@frappe.whitelist(allow_guest=True)
def embed_file_in_pdf_1(input_pdf, xml_file, output_pdf):
    """embed the pdf file"""
    app_path = frappe.get_app_path("zatca_erpgulf_sync")
    icc_path = app_path + "/sRGB.icc"

    # frappe.throw(icc_path)
    with pikepdf.open(input_pdf, allow_overwriting_input=True) as pdf:
        # Open metadata for editing
        with pdf.open_metadata() as metadata:
            metadata["pdf:Trapped"] = "False"
            metadata["dc:creator"] = ["John Doe"]  # Example author name
            metadata["dc:title"] = "PDF/A-3 Example"
            metadata["dc:description"] = (
                "A sample PDF/A-3 compliant document with embedded XML."
            )
            metadata["dc:date"] = datetime.now().isoformat()

        # Create XMP metadata
        xmp_metadata = f"""<?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>
        <x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP toolkit 2.9.1-13, framework 1.6">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                <rdf:Description rdf:about=""
                    xmlns:dc="http://purl.org/dc/elements/1.1/"
                    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
                    xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
                    xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/"
                    xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
                    <pdf:Producer>pikepdf</pdf:Producer>
                    <pdf:Trapped>False</pdf:Trapped>
                    <dc:creator>
                        <rdf:Seq>
                            <rdf:li>John Doe</rdf:li>
                        </rdf:Seq>
                    </dc:creator>
                    <dc:title>
                        <rdf:Alt>
                            <rdf:li xml:lang="x-default">PDF/A-3 Example</rdf:li>
                        </rdf:Alt>
                    </dc:title>
                    <dc:description>
                        <rdf:Alt>
                            <rdf:li xml:lang="x-default">A sample PDF/A-3 compliant document with embedded XML.</rdf:li>
                        </rdf:Alt>
                    </dc:description>
                    <xmp:CreateDate>{datetime.now().isoformat()}</xmp:CreateDate>
                    <pdfaid:part>3</pdfaid:part>
                    <pdfaid:conformance>B</pdfaid:conformance>
                </rdf:Description>
            </rdf:RDF>
        </x:xmpmeta>
        <?xpacket end="w"?>"""

        metadata_bytes = xmp_metadata.encode("utf-8")

        # Ensure the PDF has the necessary PDF/A-3 identifiers
        if "/StructTreeRoot" not in pdf.Root:
            pdf.Root["/StructTreeRoot"] = pikepdf.Dictionary()
        pdf.Root["/Metadata"] = pdf.make_stream(metadata_bytes)
        pdf.Root["/MarkInfo"] = pikepdf.Dictionary({"/Marked": True})
        pdf.Root["/Lang"] = pikepdf.String("en-US")

        # Embed the XML file
        with open(xml_file, "rb") as xml_f:
            xml_data = xml_f.read()

        embedded_file_stream = pdf.make_stream(xml_data)
        embedded_file_stream.Type = "/EmbeddedFile"
        embedded_file_stream.Subtype = "/application/xml"

        embedded_file_dict = pikepdf.Dictionary(
            {
                "/Type": "/Filespec",
                "/F": pikepdf.String(os.path.basename(xml_file)),
                "/EF": pikepdf.Dictionary({"/F": embedded_file_stream}),
                "/Desc": "XML Invoice",
            }
        )

        if "/Names" not in pdf.Root:
            pdf.Root.Names = pikepdf.Dictionary()
        if "/EmbeddedFiles" not in pdf.Root.Names:
            pdf.Root.Names.EmbeddedFiles = pikepdf.Dictionary()
        if "/Names" not in pdf.Root.Names.EmbeddedFiles:
            pdf.Root.Names.EmbeddedFiles.Names = pikepdf.Array()

        pdf.Root.Names.EmbeddedFiles.Names.append(
            pikepdf.String(os.path.basename(xml_file))
        )
        pdf.Root.Names.EmbeddedFiles.Names.append(embedded_file_dict)

        # Set OutputIntent
        with open(icc_path, "rb") as icc_file:
            icc_data = icc_file.read()
            output_intent_dict = pikepdf.Dictionary(
                {
                    "/Type": "/OutputIntent",
                    "/S": "/GTS_PDFA1",
                    "/OutputConditionIdentifier": "sRGB",
                    "/Info": "sRGB IEC61966-2.1",
                    "/DestOutputProfile": pdf.make_stream(icc_data),
                }
            )
            if "/OutputIntents" not in pdf.Root:
                pdf.Root["/OutputIntents"] = pikepdf.Array([output_intent_dict])
            else:
                pdf.Root.OutputIntents.append(output_intent_dict)

        # Add PDF/A-3 compliance information
        pdf.Root["/GTS_PDFA1"] = pikepdf.Name("/PDF/A-3B")
        pdf.docinfo["/GTS_PDFA1"] = "PDF/A-3B"
        pdf.docinfo["/Title"] = "PDF/A-3 Example"
        pdf.docinfo["/Author"] = "John Doe"  # Example author name
        pdf.docinfo["/Subject"] = "PDF/A-3 Example with Embedded XML"
        pdf.docinfo["/Creator"] = "Python pikepdf Library"
        pdf.docinfo["/Producer"] = "pikepdf"
        pdf.docinfo["/CreationDate"] = datetime.now().isoformat()

        # Save the PDF as PDF/A-3
        pdf.save(output_pdf)


# Internal Function for embedding metadata/XML (PDF/A-3 compliance)
@frappe.whitelist(allow_guest=True)
def embed_file_in_pdf_1(input_pdf, xml_file, output_pdf):
    app_path = frappe.get_app_path("zatca_erpgulf_sync")
    icc_path = os.path.join(app_path, "sRGB.icc")

    with pikepdf.open(input_pdf, allow_overwriting_input=True) as pdf:
        # Add metadata
        with pdf.open_metadata() as metadata:
            metadata["pdf:Trapped"] = "False"
            metadata["dc:creator"] = ["John Doe"]
            metadata["dc:title"] = "PDF/A-3 Invoice"
            metadata["dc:description"] = "PDF/A-3 compliant invoice with embedded XML."
            metadata["dc:date"] = datetime.now().isoformat()

        # Create XMP metadata for PDF/A-3 compliance
        xmp_metadata = f"""<?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>
        <x:xmpmeta xmlns:x="adobe:ns:meta/">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                <rdf:Description rdf:about=""
                    xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
                    <pdfaid:part>3</pdfaid:part>
                    <pdfaid:conformance>B</pdfaid:conformance>
                </rdf:Description>
            </rdf:RDF>
        </x:xmpmeta>
        <?xpacket end="w"?>"""
        pdf.Root["/Metadata"] = pdf.make_stream(xmp_metadata.encode("utf-8"))

        # Embed XML file
        with open(xml_file, "rb") as xml_f:
            xml_data = xml_f.read()

        embedded_file_stream = pdf.make_stream(xml_data)
        embedded_file_stream.Type = "/EmbeddedFile"
        embedded_file_stream.Subtype = "/application/xml"

        embedded_file_dict = pikepdf.Dictionary(
            {
                "/Type": "/Filespec",
                "/F": pikepdf.String(os.path.basename(xml_file)),
                "/EF": pikepdf.Dictionary({"/F": embedded_file_stream}),
                "/Desc": "ZATCA XML Invoice",
            }
        )

        # Add embedded file to PDF structure
        if "/Names" not in pdf.Root:
            pdf.Root.Names = pikepdf.Dictionary()
        if "/EmbeddedFiles" not in pdf.Root.Names:
            pdf.Root.Names.EmbeddedFiles = pikepdf.Dictionary()
        if "/Names" not in pdf.Root.Names.EmbeddedFiles:
            pdf.Root.Names.EmbeddedFiles.Names = pikepdf.Array()

        pdf.Root.Names.EmbeddedFiles.Names.append(
            pikepdf.String(os.path.basename(xml_file))
        )
        pdf.Root.Names.EmbeddedFiles.Names.append(embedded_file_dict)

        # Add Output Intent for PDF/A-3 compliance
        with open(icc_path, "rb") as icc_file:
            icc_data = icc_file.read()
        output_intent_dict = pikepdf.Dictionary(
            {
                "/Type": "/OutputIntent",
                "/S": "/GTS_PDFA1",
                "/OutputConditionIdentifier": "sRGB",
                "/Info": "sRGB IEC61966-2.1",
                "/DestOutputProfile": pdf.make_stream(icc_data),
            }
        )
        pdf.Root.OutputIntents = pikepdf.Array([output_intent_dict])
        pdf.save(output_pdf)


# Main function to embed XML and create PDF-A3
@frappe.whitelist(allow_guest=True)
def embed_file_in_pdf(invoice_name, print_format=None, letterhead=None, language=None):
    try:
        if not language:
            language = "en"

        # Fetch Sales Invoice
        invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)

        # Identify XML attachment
        cleared_xml_file_name = f"Cleared xml file {invoice_name}.xml"
        reported_xml_file_name = f"Reported xml file {invoice_name}.xml"

        xml_file = None
        attachments = frappe.get_all(
            "File", filters={"attached_to_name": invoice_name}, fields=["file_name"]
        )

        for attachment in attachments:
            file_name = attachment.get("file_name")
            if file_name in [cleared_xml_file_name, reported_xml_file_name]:
                xml_file = os.path.join(get_site_path("private", "files"), file_name)
                break

        if not xml_file or not os.path.exists(xml_file):
            frappe.throw(f"No XML file found for invoice {invoice_name}!")

        # Generate Invoice PDF
        input_pdf = generate_invoice_pdf(
            invoice_doc, language, letterhead, print_format
        )

        # Define output PDF-A3 name/path
        output_file_name = f"PDF-A3 {invoice_name} output.pdf"
        output_pdf_path = os.path.join(
            get_site_path("private", "files"), output_file_name
        )

        # Embed XML into PDF and generate PDF/A-3
        with pikepdf.Pdf.open(input_pdf, allow_overwriting_input=True) as pdf:
            with open(xml_file, "rb") as xml_attachment:
                pdf.attachments["invoice.xml"] = xml_attachment.read()
            pdf.save(input_pdf)
            embed_file_in_pdf_1(input_pdf, xml_file, output_pdf_path)

        # Attach PDF-A3 to Sales Invoice
        with open(output_pdf_path, "rb") as f:
            file_data = f.read()
        # Remove previous PDF-A3 attachments for this invoice
        existing_pdf_files = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Sales Invoice",
                "attached_to_name": invoice_name,
                "file_name": ["like", f"PDF-A3 {invoice_name}%"],
            },
            fields=["name"],
        )

        for file in existing_pdf_files:
            frappe.delete_doc("File", file.name, ignore_permissions=True)
            

        frappe.get_doc(
            {
                "doctype": "File",
                "file_name": output_file_name,
                "attached_to_doctype": "Sales Invoice",
                "attached_to_name": invoice_name,
                "content": file_data,
                "is_private": 1,
            }
        ).insert(ignore_permissions=True)

        frappe.db.commit()
        h=get_existing_pdf_a3(invoice_name)
        return h

        # return get_url(f"/private/files/{output_file_name}")

    except pikepdf.PdfError as e:
        frappe.throw(f"PDF processing error: {e}")
    except FileNotFoundError as e:
        frappe.throw(f"File not found: {e}")
    except Exception as e:
        frappe.throw(f"An error occurred: {e}")


@frappe.whitelist(allow_guest=True)
def get_existing_pdf_a3(invoice_name):
    """
    Returns the existing PDF-A3 file attached to the given Sales Invoice.

    Args:
        invoice_name (str): Name of the Sales Invoice.

    Returns:
        dict: Contains file name and URL of the PDF-A3 attachment, if found.
    """
    # Get all files attached to this Sales Invoice
    files = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Sales Invoice",
            "attached_to_name": invoice_name,
        },
        fields=["name", "file_url", "file_name"],
    )

    # Look for a file with "PDF-A3" in the name
    for f in files:
        if "PDF-A3" in f.file_name:
            return {
                "file_name": f.file_name,
                "file_url": get_url(f.file_url),
                "file_doc": f.name,
            }

    # If not found, return error
    frappe.throw(f"No PDF-A3 file found for invoice {invoice_name}")


@frappe.whitelist(allow_guest=True)
def check_print_permission(invoice_name):
    """
    Return 'Yes' if the current user has print permission for the Sales Invoice, else 'No'.

    Args:
        invoice_name (str): Name of the Sales Invoice.

    Returns:
        str: "Yes" or "No"
    """
    frappe.set_user("Administrator")
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    return "Yes" if doc.has_permission("print") else "No"
import os
import frappe
from werkzeug.wrappers import Response

# @frappe.whitelist(allow_guest=True)
# def get_invoice_qr_image(invoice_name):
#     """
#     Returns the QR code image stored in the `ksa_einv_qr` field of the given Sales Invoice.
#     """
#     # Fetch the invoice
#     invoice = frappe.get_doc("Sales Invoice", invoice_name)

#     # Path stored in `ksa_einv_qr` (e.g., "files/example.png")
#     if not invoice.ksa_einv_qr:
#         frappe.throw("No QR image found in 'ksa_einv_qr' field")

#     # Absolute path to the image file
#     image_path = os.path.join(frappe.get_site_path(), invoice.ksa_einv_qr.lstrip("/"))

#     # Check existence
#     if not os.path.exists(image_path):
#         frappe.throw(f"Image not found at path: {invoice.ksa_einv_qr}")

#     # Read and return image
#     with open(image_path, "rb") as img:
#         img_bytes = img.read()

#     return Response(
#         img_bytes,
#         content_type="image/png",  # You can detect type dynamically if needed
#         status=200
#     )
import frappe
from frappe.utils import get_url

@frappe.whitelist(allow_guest=True)
def get_invoice_qr_image(invoice_name):
    """
    Returns the public file URL of the QR code image stored in the `ksa_einv_qr` field
    of the given Sales Invoice.
    """
    # Fetch the invoice
    invoice = frappe.get_doc("Sales Invoice", invoice_name)

    # Get path from custom field
    qr_path = invoice.ksa_einv_qr
    if not qr_path:
        frappe.throw("No QR image found in 'ksa_einv_qr' field")

    # Return full URL
    l =get_url(qr_path)
    return l
