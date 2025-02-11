from django.http import HttpResponse
from django.shortcuts import render, redirect

from utils.filehandler import handle_file_upload

from .models import *
import pandas as pd
from weasyprint import HTML
from django.template.loader import render_to_string
from django.db.models import Q


# Create your views here.


def getTotalIncome():
    allInvoice = Invoice.objects.all()
    totalIncome = 0
    for curr in allInvoice:
        totalIncome += curr.total
    return totalIncome


def base(request):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()
    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
    }

    return render(request, "invoice/base/base.html", context)


def download_all(request):
    # Download all invoice to excel file
    # Download all product to excel file
    # Download all customer to excel file

    allInvoiceDetails = InvoiceDetail.objects.all()
    invoiceAndProduct = {
        "invoice_id": [],
        "invoice_date": [],
        "invoice_customer": [],
        "invoice_contact": [],
        "invoice_email": [],
        "invoice_comments": [],
        "product_name": [],
        "product_price": [],
        "product_unit": [],
        "product_amount": [],
        "invoice_total": [],

    }
    for curr in allInvoiceDetails:
        invoice = Invoice.objects.filter(id=curr.invoice_id).first()
        product = Product.objects.filter(id=curr.product_id).first()
        if invoice is not None:
            invoiceAndProduct["invoice_id"].append(invoice.id)
            invoiceAndProduct["invoice_date"].append(invoice.date)
            invoiceAndProduct["invoice_customer"].append(invoice.customer)
            invoiceAndProduct["invoice_contact"].append(invoice.contact)
            invoiceAndProduct["invoice_email"].append(invoice.email)
            invoiceAndProduct["invoice_comments"].append(invoice.comments)
            invoiceAndProduct["product_name"].append(product.product_name)
            invoiceAndProduct["product_price"].append(product.product_price)
            invoiceAndProduct["product_unit"].append(product.product_unit)
            invoiceAndProduct["product_amount"].append(curr.amount)
            invoiceAndProduct["invoice_total"].append(invoice.total)

    df = pd.DataFrame(invoiceAndProduct)
    df.to_excel("static/excel/allInvoices.xlsx", index=False)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="allInvoices.xlsx"'
    with open("static/excel/allInvoices.xlsx", "rb") as f:
        response.write(f.read())
    return response


def delete_all_invoice(request):
    # Delete all invoice
    Invoice.objects.all().delete()
    return redirect("view_invoice")


def upload_product_from_excel(request):
    # Upload excel file to static folder "excel"
    # add all product to database
    # save product to database
    # redirect to view_product
    excelForm = excelUploadForm(request.POST or None, request.FILES or None)
    print("Reached HERE!")
    if request.method == "POST":
        print("Reached HERE2222!")

        handle_file_upload(request.FILES["excel_file"])
        excel_file = "static/excel/masterfile.xlsx"
        df = pd.read_excel(excel_file)
        Product.objects.all().delete()
        for index, row in df.iterrows():
            product = Product(
                product_name=row["product_name"],
                product_price=row["product_price"],
                product_unit=row["product_unit"],
            )
            print(product)
            product.save()
        return redirect("view_product")
    return render(request, "invoice/upload_products.html", {"excelForm": excelForm})

    # Product view


def create_product(request):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    product = ProductForm()

    if request.method == "POST":
        product = ProductForm(request.POST)
        if product.is_valid():
            product.save()
            return redirect("create_product")

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "product": product,
    }

    return render(request, "invoice/create_product.html", context)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def view_product(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()
    product = Product.objects.filter(product_is_delete=False)
    page_num = request.GET.get('page', 1)

    paginator = Paginator(product, 6) # 6 employees per page


    try:
        product = paginator.page(page_num)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        product = paginator.page(1)
    except EmptyPage:
        # if the page is out of range, deliver the last page
        product = paginator.page(paginator.num_pages)

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "product": product,
    }
    

    return render(request, "invoice/view_product.html", context)


# Customer view
# def create_customer(request):
#     total_product = Product.objects.count()
#     total_customer = Customer.objects.count()
#     total_invoice = Invoice.objects.count()

#     customer = CustomerForm()

#     if request.method == "POST":
#         customer = CustomerForm(request.POST)
#         if customer.is_valid():
#             customer.save()
#             return redirect("create_customer")

#     context = {
#         "total_product": total_product,
#         "total_customer": total_customer,dwon
#         "total_invoice": total_invoice,
#         "customer": customer,
#     }

#     return render(request, "invoice/create_customer.html", context)


# def view_customer(request):
#     total_product = Product.objects.count()
#     total_customer = Customer.objects.count()
#     total_invoice = Invoice.objects.count()

#     customer = Customer.objects.all()

#     context = {
#         "total_product": total_product,
#         "total_customer": total_customer,
#         "total_invoice": total_invoice,
#         "customer": customer,
#     }

#     return render(request, "invoice/view_customer.html", context)


# Invoice view
from django.shortcuts import render, redirect
from .models import Invoice, InvoiceDetail, Product

from django.shortcuts import render, redirect
from .models import Invoice, InvoiceDetail

def create_invoice(request):
    invoice = None
    invoice_details = None
    invoice_id = request.GET.get("id")  # Get invoice ID from URL

    if invoice_id:
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            invoice_details = InvoiceDetail.objects.filter(invoice=invoice)
        except Invoice.DoesNotExist:
            return redirect("create_invoice")  # Redirect if invoice not found

    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    context = {
        "total_invoice": total_invoice,
        "total_income": total_income,
        "invoice": invoice,  # Pass invoice object for editing
        "invoice_details": invoice_details,  # Pass details to populate form
    }
    if request.method == "POST":
        customer = request.POST.get("customer")
        contact = request.POST.get("contact")
        comments = request.POST.get("comments")

        # TODO: while update read input hidden field
        invoice_id = request.POST.get("id")  # Works only if included in form submission
        if invoice_id:
            try:
                invoice = Invoice.objects.get(id=invoice_id)
                invoice_details = InvoiceDetail.objects.filter(invoice=invoice)
            except Invoice.DoesNotExist:
                return redirect("create_invoice") 
            
        if invoice:
            # Update existing invoice
            invoice.customer = customer
            invoice.contact = contact
            invoice.comments = comments
            invoice.total = 0  # Reset total before recalculating
            invoice.save()

            # Delete old details before adding new ones
            InvoiceDetail.objects.filter(invoice=invoice).delete()
        else:
            # Create new invoice
            invoice = Invoice.objects.create(
                customer=customer,
                contact=contact,
                comments=comments,
                total=0  # Initialize total
            )

        total = 0
        products = request.POST.getlist("product[]")
        amounts = request.POST.getlist("amount[]")
        quantities = request.POST.getlist("quantity[]")

        for product_name, amount, quantity in zip(products, amounts, quantities):
            try:
                amount = float(amount)
                quantity = int(quantity)
                subtotal = amount * quantity
                total += subtotal

                # Save new invoice details
                InvoiceDetail.objects.create(
                    invoice=invoice,
                    product=product_name,
                    product_price=amount,
                    amount=quantity,
                )
            except ValueError:
                continue  # Skip invalid data

        # Update total amount in invoice
        invoice.total = total
        invoice.save()

        return redirect("view_invoice")

    return render(request, "invoice/create_invoice.html", context)



from django.shortcuts import render
from django.db.models import Q
from datetime import datetime
from .models import Invoice

def view_invoice(request):
    search_query = request.GET.get('search', '').strip()  # Get search input
    start_date = request.GET.get('start_date', '').strip()  # Get start date input
    end_date = request.GET.get('end_date', '').strip()  # Get end date input

    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    invoices = Invoice.objects.all()

    # Apply search filter
    if search_query:
        invoices = invoices.filter(
            Q(customer__icontains=search_query) | 
            Q(total__icontains=search_query)
        ).distinct()

    # Apply date range filter
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        invoices = invoices.filter(date__gte=start_date)

    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        invoices = invoices.filter(date__lte=end_date)

    context = {
        "total_invoice": total_invoice,
        "total_income": total_income,
        "invoice": invoices,
    }

    return render(request, "invoice/view_invoice.html", context)


# Detail view of invoices
def view_invoice_detail(request, pk):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        # 'invoice': invoice,
        "invoice_detail": invoice_detail,
    }

    return render(request, "invoice/view_invoice_detail.html", context)


# Delete invoice
def delete_invoice(request, pk):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)
    if request.method == "POST":
        invoice_detail.delete()
        invoice.delete()
        return redirect("view_invoice")

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "invoice": invoice,
        "invoice_detail": invoice_detail,
    }

    return render(request, "invoice/delete_invoice.html", context)


# # Edit customer
# def edit_customer(request, pk):
#     total_product = Product.objects.count()
#     # total_customer = Customer.objects.count()
#     total_invoice = Invoice.objects.count()

#     customer = Customer.objects.get(id=pk)
#     form = CustomerForm(instance=customer)

#     if request.method == "POST":
#         customer = CustomerForm(request.POST, instance=customer)
#         if customer.is_valid():
#             customer.save()
#             return redirect("view_customer")

#     context = {
#         "total_product": total_product,
#         "total_customer": total_customer,
#         "total_invoice": total_invoice,
#         "customer": form,
#     }

#     return render(request, "invoice/create_customer.html", context)


# Delete customer
# def delete_customer(request, pk):
#     total_product = Product.objects.count()
#     total_customer = Customer.objects.count()
#     total_invoice = Invoice.objects.count()

#     customer = Customer.objects.get(id=pk)

#     if request.method == "POST":
#         customer.delete()
#         return redirect("view_customer")

#     context = {
#         "total_product": total_product,
#         "total_customer": total_customer,
#         "total_invoice": total_invoice,
#         "customer": customer,
#     }

#     return render(request, "invoice/delete_customer.html", context)


# Edit product
def edit_product(request, pk):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)

    if request.method == "POST":
        # customer = CustomerForm(request.POST, instance=product)

        product.save()
        return redirect("view_product")

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "product": form,
    }

    return render(request, "invoice/create_product.html", context)


# Delete product
def delete_product(request, pk):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    product = Product.objects.get(id=pk)

    if request.method == "POST":
        product.product_is_delete = True
        product.save()
        return redirect("view_product")

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "product": product,
    }

    return render(request, "invoice/delete_product.html", context)


def preview_invoice(request, pk):
    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)
    return render(request, "invoice/preview_invoice.html", {"invoice_detail":invoice_detail,})


def download_invoice(request, pk):
    template_path = 'invoice/preview_invoice.html'
    
    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)
    
    context = {'invoice_detail': invoice_detail}
    
    # Render the template to HTML
    html = render_to_string(template_path, context, request=request)

    # Generate the PDF
    pdf = HTML(string=html).write_pdf()

    # Create response with PDF as attachment
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    return response