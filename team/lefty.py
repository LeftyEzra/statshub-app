
# Class Base View For Team Details
class ProductDetailView(APIView):
    def get(self, request, foo):
        #replace hyphen with empty string
        foo = foo.replace('-', '')
        #Fetch the category from the url
        
        product_details = get_object_or_404(Product, name=foo)
        context = {
        'product_details':product_details,
        # Product Image
        'product_images': GalleryImages.objects.filter(product=product_details),
        }
        return render(request, 'product-page.html', context)
