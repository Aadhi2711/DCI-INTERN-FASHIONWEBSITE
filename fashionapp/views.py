from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from fashionapp.models import UserProfile, VendorDetails, OrderDetails, ProductDetails, ProductReviews , UserCart
from django.contrib.auth.models import User

def mainpage(req):
    return render(req,'landingpage.html')

def index(req):
    if req.method == 'POST':
        name = req.POST.get('name')
        email = req.POST.get('email')
        password1 = req.POST.get('password')
        password2 = req.POST.get('confirmPassword')
        mobile = req.POST.get('mobilenumber')
        user_type = 'Customer'
        if password1 == password2:
            UserProfile.objects.create(name=name,email=email,password=password1,mobile_number=mobile,type=user_type)
            success_message = "Registration successful!"
            return render(req, 'login_user.html')
        else:
            err_msg = "Passwords do not match"
            return render(req, 'register_user.html', {'er_msg': err_msg})
    return render(req, 'register_user.html')

def vendor(req):
    if req.method == 'POST':
        name = req.POST.get('name')
        email = req.POST.get('email')
        password1 = req.POST.get('password')
        password2 = req.POST.get('confirmPassword')
        mobile = req.POST.get('mobilenumber')
        user_type = 'Vendor'
        if password1 == password2:
            user_profile = UserProfile.objects.create(name=name,email=email,password=password1,mobile_number=mobile,type=user_type)
            return render(req, 'vendor_registration.html', {'user_id': user_profile.id})
        else:
            err_msg = "Passwords do not match"
            return render(req, 'register_vendor.html', {'er_msg': err_msg})
    return render(req, 'register_vendor.html')

def vendor_registration(request):
    er_msg = None
    success_message = None

    if request.method == 'POST':
        business_phone = request.POST.get('business_phone')
        GSTIN_number = request.POST.get('GSTIN_number')
        business_name = request.POST.get('business_name')
        street = request.POST.get('street')
        postal_code = request.POST.get('postal_code')
        city = request.POST.get('city')
        state = request.POST.get('state')
        user_id = UserProfile.objects.latest('id').id

        vendor_details = VendorDetails.objects.create(
            user_profile_id=user_id,
            business_phone=business_phone,
            GSTIN_number=GSTIN_number,
            business_name=business_name,
            street=street,
            postal_code=postal_code,
            city=city,
            state=state
        )

        success_message = "Registration successful!"

    return render(request, 'login_user.html')

def user_login(req):
    if req.method == 'POST':
        mail = req.POST.get('email')
        pw = req.POST.get('password')
        user = get_object_or_404(UserProfile, email=mail)

        if pw == user.password:
            if user.type == 'Customer':
                products = ProductDetails.objects.all().values()
                men_subcategories = ProductDetails.objects.filter(category='Men').values_list('sub_category', flat=True).distinct()
                women_subcategories = ProductDetails.objects.filter(category='Women').values_list('sub_category', flat=True).distinct()
                kids_subcategories = ProductDetails.objects.filter(category='Kids').values_list('sub_category', flat=True).distinct()
                context = {
                    'men_subcategories': men_subcategories,
                    'women_subcategories': women_subcategories,
                    'kids_subcategories': kids_subcategories,
                    'customer': user,
                    'products': products,
                }
                
                return render(req, 'customer_homepage.html', context)
            else:
                vend = VendorDetails.objects.filter(user_profile=user)
                return render(req, 'vendor_page.html', {'vendor': user, 'vend': vend[0]})
        else:
            e_msg = 'Incorrect email id or password'
            return render(req, 'login_user.html', {'e_msg': e_msg})

    return render(req, 'login_user.html')

def product_categories_view(request, subcategory,customer_id):
    selected_products = ProductDetails.objects.filter(sub_category=subcategory)  
    context = {
        'selected_subcategory': subcategory,
        'selected_products': selected_products,
        'customer' : customer_id
    }
    return render(request, 'product_categories.html', context)
    
def add_product(request , vendorid):
    return render(request, 'addproduct.html' , { 'id' : vendorid})


def store_product(request, vendorid):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        availability = request.POST.get('availability')
        size = request.POST.get('size')
        colours = request.POST.get('colours')
        description = request.POST.get('description')
        cost = request.POST.get('cost')
        images = request.FILES.get('images')
        category = request.POST.get('category')
        sub_category = request.POST.get('sub_category')   

        product_details = ProductDetails(
            product_vendor=vendorid,
            product_name=product_name,
            availability=availability,
            size=size,
            colours=colours,
            description=description,
            cost=cost,
            images = images,
            category=category,
            sub_category=sub_category
        )

        product_details.save()
        return HttpResponse("stored")

def view_orders(request,vendorid):
    orderitems = OrderDetails.objects.filter(vend_id_id=vendorid).values()
    return render(request, 'vieworders.html',{'orders':orderitems})

def order_update(req,ordid):
    orderitems = OrderDetails.objects.get(product_ordered_id=ordid)
    if req.method=='POST':
        status = req.POST.get('status')
        orderitems.status = status
        orderitems.save()
        return render(req,'vieworders.html',{'orders':[orderitems]})
    return render(req,'status_update.html',{'orders':[orderitems]})

def display_product(request , vendorid):
    products = ProductDetails.objects.filter(product_vendor=vendorid).values()
    return render(request, 'displayproduct.html', {'products':products})

def vendor_profile(request, vendorid):
    try:
        vendor_details = VendorDetails.objects.get(user_profile_id=vendorid)
    except VendorDetails.DoesNotExist:
        return render(request, 'vendor_page.html')  
    return render(request, 'vendorprofile.html', {'vendor_details': vendor_details})

def edit_and_save_vendor_profile(request, vendorid):
    vendor_details = get_object_or_404(VendorDetails, user_profile_id=vendorid)

    if request.method == 'POST':
        vendor_details.user_profile.name = request.POST.get('name')
        vendor_details.user_profile.email = request.POST.get('email')
        vendor_details.user_profile.mobile_number = request.POST.get('mobile_number')
        vendor_details.business_name = request.POST.get('business_name')
        vendor_details.business_phone = request.POST.get('business_phone')
        vendor_details.GSTIN_number = request.POST.get('GSTIN_number')
        vendor_details.street = request.POST.get('street')
        vendor_details.postal_code = request.POST.get('postal_code')
        vendor_details.city = request.POST.get('city')
        vendor_details.state = request.POST.get('state')

        vendor_details.user_profile.save()
        vendor_details.save()

        return redirect('vendor_profile', vendorid=vendorid)

    return render(request, 'edit_vendor_profile.html', {'vendor_details': vendor_details})

def add_to_cart(request , customer_id , product_id):
    cart_details = UserCart(
        cart_userid = customer_id,
        cart_product = product_id
    )

    product = get_object_or_404(ProductDetails, product_id=product_id)
    existing_cart_item = UserCart.objects.filter(cart_userid=customer_id, cart_product=product_id).first()

    if existing_cart_item:
        existing_cart_item.quantity += 1
        existing_cart_item.save()
    else:
        cart_details = UserCart(
            cart_userid=customer_id,
            cart_product=product_id,
            quantity=1
        )
        cart_details.save()

    return HttpResponse("stored")

def cart(request , customer_id):
    cart = UserCart.objects.filter(cart_userid=customer_id)
    cart_products = ProductDetails.objects.filter(product_id__in=cart.values_list('cart_product', flat=True))
    user = UserProfile.objects.get(id=customer_id)

    return render(request , 'cart.html' , {'cart':cart_products , 'user':user})

def edit_product(request, product_id):
    product_details = get_object_or_404(ProductDetails, product_id=product_id)

    if request.method == 'POST':
        product_details.product_vendor = request.POST.get('product_vendor')
        product_details.product_name = request.POST.get('product_name')
        product_details.availability = request.POST.get('availability')
        product_details.size = request.POST.get('size')
        product_details.colours = request.POST.get('colours')
        product_details.description = request.POST.get('description')
        product_details.cost = request.POST.get('cost')
        product_details.category = request.POST.get('category')
        product_details.sub_category = request.POST.get('sub_category')

        new_images = request.FILES.get('images')
        if new_images:
            product_details.images = new_images

        product_details.save()

        return redirect('display_product', vendorid=product_details.product_vendor)

    return render(request, 'editproduct.html', {'product_details': product_details})

def place_orderdetails(request,customer_id , product_id ):
    product_details = get_object_or_404(ProductDetails, product_id=product_id)
    customer = get_object_or_404(UserProfile, id=customer_id)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        payment_type = request.POST.get('payment_type')
        address = request.POST.get('address')
        create_order(product_details, customer, quantity, payment_type, address)

        return HttpResponse("Ordered placed") 
    return render(request,"place_orderdetails.html",{'place_order':product_details,'customer_detail':customer})


def create_order(product, customer, quantity, payment_type, address):
    vendor = VendorDetails.objects.get(user_profile__id=product.product_vendor)

    try:
        quantity = int(quantity)

        if product.availability >= quantity > 0:
            order = OrderDetails(
                product_ordered=product,
                cust_id=customer,
                vend_id=vendor,
                quantity=quantity,
                payment_details=payment_type,
                address=address,
                status='Ordered',
                cost=product.cost * quantity  
            )
            order.save()

            product.availability -= quantity
            product.save()

            return True 
        else:
            return False  
    except ValueError:
       
        return False

def confirm_order(request,customer_id):
    confirm = OrderDetails.objects.filter(cust_id_id=customer_id)
    return render(request,"confirm_order.html",{"confirm_product":confirm})
    

def delete_product(request, product_id):
    product = UserCart.objects.filter(cart_product=product_id)
    product.delete()
    return HttpResponse("Item deleted")
    
def customer_profile(request, customer_id):
    try:
        customer_details = UserProfile.objects.get(id=customer_id)
    except UserProfile.DoesNotExist:
        return render(request, 'customerprofile.html', {'error_message': 'Customer not found.'})

    return render(request, 'customerprofile.html', {'customer_details': customer_details})

def landing_page_view(request):
    return render(request, 'landingpage.html')

from django.shortcuts import render
import pandas as pd
import plotly.express as px
import plotly.io as pio



def visualize(request, vendor_id):
    # Load the dataset
    df = pd.read_csv("./fashionapp/product_dataset_with_order_details.csv")

    # Function to filter data for a specific vendor
    def filter_data_by_vendor(vendor_id):
        return df[df['product_vendor'] == vendor_id]

    # Convert vendor_id to integer (if needed)
    vendor_id = int(vendor_id)

    # Filter data for the input vendor
    vendor_data = filter_data_by_vendor(vendor_id)

    # Create Plotly figures
    fig1 = px.bar(vendor_data, x='product_name', y='cost', title=f'Sales Performance for Vendor {vendor_id}', labels={'cost': 'Sales (in $)'}, text='cost', height=400)
    fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig1.update_layout(xaxis_tickangle=-45, xaxis_title='Product Name', yaxis_title='Sales (in $)')
    plot_div1 = plot(fig1, output_type='div', include_plotlyjs=False)

    fig2 = px.line(vendor_data.groupby('month')['cost'].sum().reset_index(), x='month', y='cost', title=f'Monthly Sales Trend for Vendor {vendor_id}', labels={'cost': 'Total Sales (in $)'}, markers=True, line_shape='linear')
    fig2_div = plot(fig2, output_type='div', include_plotlyjs=False)

    fig3 = px.pie(vendor_data['order_status'].value_counts(), names=vendor_data['order_status'].value_counts().index, title=f'Order Status Distribution for Vendor {vendor_id}', labels={'label': 'Order Status'}, hole=0.3)
    fig3_div = plot(fig3, output_type='div', include_plotlyjs=False)

    fig4 = px.bar(vendor_data, x='category', y='cost', title=f'Category-wise Sales for Vendor {vendor_id}', labels={'cost': 'Sales (in $)', 'category': 'Category'}, text='cost', height=400)
    fig4.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig4_div = plot(fig4, output_type='div', include_plotlyjs=False)

    fig5_modified = px.bar(vendor_data.groupby(['month', 'delivery_address'])['cost'].sum().reset_index(), x='month', y='cost', color='delivery_address', title=f'Monthly State-wise Revenue for Vendor {vendor_id}', text='cost', height=400)
    fig5_modified.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig5_modified_div = plot(fig5_modified, output_type='div', include_plotlyjs=False)

    # Pass the HTML strings to the template along with vendor_id
    return render(request, 'visualize.html', {'vendor_id': vendor_id, 'plot_div1': plot_div1, 'fig2_div': fig2_div, 'fig3_div': fig3_div, 'fig4_div': fig4_div, 'fig5_modified_div': fig5_modified_div})
