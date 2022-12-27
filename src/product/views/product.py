from django.views import generic
from django.db.models import Count, Q

from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
    InvalidPage
)

from product.models import (
    Product,
    ProductVariant,
    ProductVariantPrice,
    Variant
)

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context

class ListProductView(generic.ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = 2

    def get_queryset(self):
        queryset = Product.objects.order_by('-created_at')
        title = self.request.GET.get('title', None)
        variant = self.request.GET.get('variant', None)
        price_from = self.request.GET.get('price_from', None)
        price_to = self.request.GET.get('price_to', None)
        date = self.request.GET.get('date', None)

        if variant:
            selected_variant = ProductVariant.objects.filter(variant_title__icontains=variant)
            qs = ProductVariantPrice.objects.filter(
                Q(product_variant_one__in=selected_variant) |
                Q(product_variant_two__in=selected_variant) |
                Q(product_variant_three__in=selected_variant)

            ).values_list("product__id", flat=True).distinct()
            queryset = queryset.filter(id__in=qs)

        if price_from and price_to:
            qs = ProductVariantPrice.objects.filter(
                price__gte=price_from,
                price__lte=price_to
            ).values_list("product__id", flat=True).distinct()
            queryset = queryset.filter(id__in=qs)
            
        if title:
            queryset = queryset.filter(title__icontains=title)
            
        if date:
            queryset = queryset.filter(created_at__date=date)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        products = self.get_queryset()
        paginator = Paginator(products, self.paginate_by)
        product_variants = Variant.objects.filter(active=True)

        variants = []

        for variant in product_variants:
            data = {}
            data['variant'] = variant
            attributes = []

            for a in ProductVariant.objects.filter(variant=variant):
                if str(a.variant_title).title() not in attributes:
                    attributes.append(str(a.variant_title).title())
            
            data['attributes'] = attributes
            variants.append(data)

        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(1)
        except InvalidPage:
            queryset = paginator.page(1)

        context['variants'] = variants
        context['queryset'] = queryset
        context['paginator'] = paginator

        return context


class EditProductView(generic.DetailView):
    model = Product
    template_name = 'products/edit.html'

    def get_context_data(self, **kwargs):
        context = super(EditProductView, self).get_context_data(**kwargs)
        product_variants = ProductVariant.objects.filter(product__id=self.get_object().id)
        variants = product_variants.values("variant").annotate(Count("variant")).values_list("variant", flat=True)
        context['product'] = True
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['variants'] = list(variants.all())
        context['has_variant'] = len(context['variants']) > 0
        return context





