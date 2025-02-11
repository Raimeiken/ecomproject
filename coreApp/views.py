from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg
from taggit.models import Tag

from coreApp.models import Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, wishlist, Address
from coreApp.forms import ProductReviewForm
from django.contrib import messages


# Create your views here.
def index(request):
    # products = Product.objects.all().order_by("-id")
    products = Product.objects.filter(product_status="published", featured=True)
    context = {
        "products" : products
    }
    return render(request,'core/index.html', context)


def product_list_view(request):
    products = Product.objects.filter(product_status="published")
    context = {
        "products" : products
    }
    return render(request,'core/product-list.html', context)


def category_list_view(request):

    
    categories = Category.objects.all()
    # categories = Category.objects.all().annotate(product_count=Count("product"))

    context = {
        "categories":categories
    }
    return render(request,'core/category-list.html',context)


def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)

    context = {
        "category":category,
        "products":products,
    }
    return render(request,"core/category-product-list.html",context)


def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
        "vendors": vendors,
    }
    return render(request,"core/vendor-list.html",context)


def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published")
    
    context = {
        "vendor": vendor,
        "products": products,
    }
    return render(request,"core/vendor-detail.html",context)


def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)

    # product = get_object_or_404(Product, pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    # get reviews
    review = ProductReview.objects.filter(product=product).order_by("-date")

    # get reviews average
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    review_form = ProductReviewForm()

    make_review = True

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False

    p_image = product.p_images.all()

    context = {
        "p":product,
        "make_review": make_review,
        "review_form":review_form,
        "p_image": p_image,
        "average_rating":average_rating,
        "reviews":review,
        "products":products,
    }

    return render(request,"core/product-detail.html", context)


def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        "products":products,
        "tag":tag,
    }
    return render(request,"core/tag.html", context)


def ajax_add_review(request,pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user = user,
        product = product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review':request.POST['review'],
        'rating':request.POST['rating'],
    }
    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    return JsonResponse(
        {
            'bool':True,
            'context':context,
            'average_reviews':average_reviews
        }
    )


def search_view(request):
    query = request.GET['q']

    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products":products,
        "query": query,
    }
    return render(request, "core/search.html", context)







def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title':request.GET['title'],
        'qty':request.GET['qty'],
        'price':request.GET['price'],
        'image':request.GET['image'],
        'pid':request.GET['pid'],
    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product
    return JsonResponse({"data":request.session['cart_data_obj'], 'totalcartitems':len(request.session['cart_data_obj'])})


def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems':len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("coreApp:index")

