from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from catalog.models import Product
from .models import Review
from .forms import ReviewForm

@login_required
def review_create(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('catalog:product_detail', pk=product.pk)
    else:
        form = ReviewForm()
    return render(request, 'reviews/review_form.html', {'form': form, 'product': product})

def review_list(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.all()
    return render(request, 'reviews/review_list.html', {'product': product, 'reviews': reviews})
