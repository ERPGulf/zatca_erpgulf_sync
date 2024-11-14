
# import json
# from werkzeug.wrappers import Response
# import frappe


# @frappe.whitelist(allow_guest=True)
# def create_simple_sales_invoice(customer_name, items, posting_date, due_date, taxes=None, discount_amount=0, discount_percentage=0, tax_category="Standard"):
#     if not items:
#         return Response(json.dumps({"data": "items information not provided"}), status=404, mimetype='application/json')

#     # Check if customer exists by customer_name, or create a new one if not found
#     customer_details = frappe.get_all("Customer", fields=["name"], filters={'customer_name': customer_name})
#     if not customer_details:
#         try:
#             new_customer = frappe.get_doc({
#                 "doctype": "Customer",
#                 "customer_name": customer_name,
#                 "customer_type": "Individual",
#                 "customer_group": "All Customer Groups",
#                 "territory": "All Territories"
#             })
#             new_customer.insert(ignore_permissions=True)
#             frappe.db.commit()
#             customer_id = new_customer.name
#         except Exception as e:
#             return Response(json.dumps({"message": f"Failed to create customer: {str(e)}"}), status=404, mimetype='application/json')
#     else:
#         customer_id = customer_details[0]["name"]

#     # Prepare items with income accounts, descriptions, and tax templates
#     invoice_items = []
#     for item in items:
#         item_code = item["item_name"]
#         quantity = item.get("quantity", 0)
#         rate = item.get("rate", 0)
#         income_account = item.get("income_account")
#         description = item.get("description", "No description provided")
#         item_tax_template = item.get("item_tax_template", "")

#         # Validate income account
#         if income_account and not frappe.db.exists("Account", income_account):
#             return Response(json.dumps({"message": f"Income Account '{income_account}' not found"}), status=404, mimetype='application/json')

#         invoice_item = {
#             "item_code": item_code,
#             "qty": quantity,
#             "rate": rate,
#             "income_account": income_account,
#             "description": description,
#             "item_tax_template": item_tax_template
#         }
#         invoice_items.append(invoice_item)

#     # Prepare taxes if provided, with category and additional fields
#     taxes_list = []
#     if taxes:
#         for tax in taxes:
#             charge_type = tax.get("charge_type")
#             account_head = tax.get("account_head")
#             amount = tax.get("amount")
#             description = tax.get("description", "No description provided")

#             if charge_type and account_head and amount is not None:
#                 taxes_list.append({
#                     "charge_type": charge_type,
#                     "account_head": account_head,
#                     "tax_amount": amount,
#                     "description": description,
#                     "tax_category": tax_category  # Add tax category
#                 })

#     # Create Sales Invoice with discounts and tax information
#     try:
#         new_invoice = frappe.get_doc({
#             "doctype": "Sales Invoice",
#             "customer": customer_id,
#             "posting_date": posting_date,
#             "due_date": due_date,
#             "items": invoice_items,
#             "taxes": taxes_list,
#             "additional_discount_percentage": discount_percentage,
#             "discount_amount": discount_amount,
#             "apply_discount_on": "Net Total" 
#         })

#         new_invoice.insert(ignore_permissions=True)
#         new_invoice.submit()
#         new_invoice.reload()  # Check the ZATCA status after submitting the invoice

# # If ZATCA status is 503, return a 503 response
#         if new_invoice.custom_zatca_status == "503 Service Unavailable":
#             return Response(
#                 json.dumps({
#                     "data": {
#                 "invoice_id": new_invoice.name,
#                 "uuid": new_invoice.custom_uuid,
#                 "zatca_full_response": new_invoice.custom_zatca_full_response
#             },
#             "message": "Service Unavailable"
#         }),
#         status=503,
#         mimetype='application/json'
#     )

# # Prepare and return response with invoice detail if no 503 error
#         customer_info = {
#     "invoice_id": new_invoice.name,
#     "uuid": new_invoice.custom_uuid,
#     "zatca_full_response": new_invoice.custom_zatca_full_response
# }
#         return Response(
#     json.dumps({"data": customer_info}),
#     status=200,
#     mimetype='application/json'
# )

#     except Exception as e:
#         return Response(
#         json.dumps({"message": str(e)}),
#         status=404,
#         mimetype='application/json'
#     )


        # Call the ZATCA background function for further processing
        # zatca_Background_on_submit(new_invoice)

        # Prepare and return response with invoice detail
    #     updated_invoice = frappe.get_doc("Sales Invoice", new_invoice.name)
    #     customer_info = {
    #         "invoice_id": updated_invoice.name,
    #         "uuid": updated_invoice.custom_uuid,
    #         "zatca_full_response": updated_invoice.custom_zatca_full_response
    #     }

    #     return Response(json.dumps({"data": customer_info}), status=200, mimetype='application/json')

    # except Exception as e:
    #     return Response(json.dumps({"message": str(e)}), status=404, mimetype='application/json')
import json
from werkzeug.wrappers import Response
import frappe
import base64

@frappe.whitelist(allow_guest=True)
def create_simple_sales_invoice(customer_name, items, posting_date, due_date, custom_user_invoice_number, taxes=None, discount_amount=0, discount_percentage=0, tax_category="Standard"):
    if not items:
        return Response(json.dumps({"data": "items information not provided"}), status=404, mimetype='application/json')

    # Check for duplicate custom_user_invoice_number
    existing_invoice = frappe.get_all("Sales Invoice", filters={"custom_user_invoice_number": custom_user_invoice_number})
    if existing_invoice:
        return Response(
            json.dumps({"message": "Duplicate invoice number"}), 
            status=409, 
            mimetype='application/json'
        )

    # Check if customer exists by customer_name, or create a new one if not found
    customer_details = frappe.get_all("Customer", fields=["name"], filters={'customer_name': customer_name})
    if not customer_details:
        try:
            new_customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_name,
                "customer_type": "Individual",
                "customer_group": "All Customer Groups",
                "territory": "All Territories"
            })
            new_customer.insert(ignore_permissions=True)
            frappe.db.commit()
            customer_id = new_customer.name
        except Exception as e:
            return Response(json.dumps({"message": f"Failed to create customer: {str(e)}"}), status=404, mimetype='application/json')
    else:
        customer_id = customer_details[0]["name"]

    # Prepare items with income accounts, descriptions, and tax templates
    invoice_items = []
    for item in items:
        item_code = item["item_name"]
        quantity = item.get("quantity", 0)
        rate = item.get("rate", 0)
        income_account = item.get("income_account")
        description = item.get("description", "No description provided")
        item_tax_template = item.get("item_tax_template", "")

        # Validate income account
        if income_account and not frappe.db.exists("Account", income_account):
            return Response(json.dumps({"message": f"Income Account '{income_account}' not found"}), status=404, mimetype='application/json')

        invoice_item = {
            "item_code": item_code,
            "qty": quantity,
            "rate": rate,
            "income_account": income_account,
            "description": description,
            "item_tax_template": item_tax_template
        }
        invoice_items.append(invoice_item)

    # Prepare taxes if provided, with category and additional fields
    taxes_list = []
    if taxes:
        for tax in taxes:
            charge_type = tax.get("charge_type")
            account_head = tax.get("account_head")
            amount = tax.get("amount")
            description = tax.get("description", "No description provided")

            if charge_type and account_head and amount is not None:
                taxes_list.append({
                    "charge_type": charge_type,
                    "account_head": account_head,
                    "tax_amount": amount,
                    "description": description,
                    "tax_category": tax_category
                })

    # Create Sales Invoice with discounts and tax information
    try:
        new_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": customer_id,
            "posting_date": posting_date,
            "due_date": due_date,
            "custom_user_invoice_number": custom_user_invoice_number,  # Include custom field
            "items": invoice_items,
            "taxes": taxes_list,
            "additional_discount_percentage": discount_percentage,
            "discount_amount": discount_amount,
            "apply_discount_on": "Net Total" 
        })

        new_invoice.insert(ignore_permissions=True)
        new_invoice.submit()
        new_invoice.reload()  # Check the ZATCA status after submitting the invoice

        # If ZATCA status is 503, return a 503 response
        if new_invoice.custom_zatca_status == "503 Service Unavailable":
            return Response(
                json.dumps({
                    "data": {
                        "invoice_id": new_invoice.name,
                        "uuid": new_invoice.custom_uuid,
                        "zatca_full_response": new_invoice.custom_zatca_full_response
                    },
                    "message": "Service Unavailable"
                }),
                status=503,
                mimetype='application/json'
            )
        xml_content = download_xml(new_invoice.name)
        xml_str = xml_content.decode("utf-8")
        # Prepare and return response with invoice detail if no 503 error
        qr_image_content = download_image(new_invoice.name)
        qr_image_base64 = base64.b64encode(qr_image_content).decode("utf-8")
        customer_info = {
            "invoice_id": new_invoice.name,
            "uuid": new_invoice.custom_uuid,
            "zatca_full_response": new_invoice.custom_zatca_full_response,
            "xml":xml_str,
            "qr_image" : qr_image_base64

        }
        return Response(
            json.dumps({"data": customer_info}),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            json.dumps({"message": str(e)}),
            status=404,
            mimetype='application/json'
        )



@frappe.whitelist(allow_guest=True)

def download_image(new_invoice):
    # Specify the file path of the XML file
    # file_path = "zatca.erpgulf.com/private/files/QR_image_ACC-SINV-2024-01233.png"
    new_invoice = frappe.get_doc("Sales Invoice", new_invoice)
    
    file_path = frappe.local.site +new_invoice.ksa_einv_qr

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
    
    file_path = frappe.local.site +new_invoice.custom_ksa_einvoicing_xml
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
      (("" if "/private/" in path else "/public")
       + path).strip("/"))





@frappe.whitelist(allow_guest=True)
def get_invoice_by_custom_number(custom_user_invoice_number):
    # Check if the Sales Invoice with the given custom_user_invoice_number exists
    existing_invoice = frappe.get_all(
        "Sales Invoice", 
        filters={"custom_user_invoice_number": custom_user_invoice_number}, 
        fields=["name", "docstatus"]
    )

    if not existing_invoice:
        # If the invoice does not exist, return an error response
        return Response(
            json.dumps({"message": "Invoice not found"}), 
            status=404, 
            mimetype='application/json'
        )

    # Get the first matched invoice
    invoice_name = existing_invoice[0]["name"]
    docstatus = existing_invoice[0]["docstatus"]

    if docstatus != 1:  # docstatus 1 means the invoice is submitted
        # If the invoice exists but is not submitted, return an error response
        return Response(
            json.dumps({"message": "Invoice exists but is not submitted"}), 
            status=400, 
            mimetype='application/json'
        )

    # If the invoice exists and is submitted, retrieve detailed information
    try:
        new_invoice = frappe.get_doc("Sales Invoice", invoice_name)

        # Check if ZATCA status is 503
        if new_invoice.custom_zatca_status == "503 Service Unavailable":
            return Response(
                json.dumps({
                    "data": {
                        "invoice_id": new_invoice.name,
                        "uuid": new_invoice.custom_uuid,
                        "zatca_full_response": new_invoice.custom_zatca_full_response
                    },
                    "message": "Service Unavailable"
                }),
                status=503,
                mimetype='application/json'
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
            "qr_image": qr_image_base64
        }

        return Response(
            json.dumps({"data": customer_info}),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            json.dumps({"message": str(e)}),
            status=500,
            mimetype='application/json'
        )
