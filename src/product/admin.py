from django.contrib import admin

from .models import (
    Variant,
    Product,
    ProductImage,
    ProductVariant,
    ProductVariantPrice,
)


admin.site.register(Variant)


class ProductVariantTabular(admin.TabularInline):
    model = ProductVariant
    extra = 6


class ProductVariantPriceTabular(admin.TabularInline):
    model = ProductVariantPrice
    extra = 4


class ProductImageTabular(admin.TabularInline):
    model = ProductImage
    extra = 4
    

class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductVariantTabular,
        ProductImageTabular,
     ]


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "product"
    ]


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductVariantPrice)

