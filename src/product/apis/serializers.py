from django.db.models import Count

from rest_framework import serializers

from product.models import (
    Product,
    ProductVariantPrice,
    ProductVariant,
    Variant
)


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"


class ProductVariantPriceSerializer(serializers.ModelSerializer):

    title = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariantPrice
        fields = (
            "id",
            "product_variant_one",
            "product_variant_two",
            "product_variant_three",
            "price",
            "stock",
            "title",
        )

    def get_title(self, obj):
        variant_list = []
        
        if obj.product_variant_one:
            variant_list.append(obj.product_variant_one.variant_title)
        if obj.product_variant_two:
            variant_list.append(obj.product_variant_two.variant_title)
        if obj.product_variant_three:
            variant_list.append(obj.product_variant_three.variant_title)

        return "/".join(variant_list) + '/'
            

class ProductDetailsSerializer(serializers.ModelSerializer):

    product_variant_prices = serializers.SerializerMethodField()
    product_variant = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "title",
            "sku",
            "description",
            "product_variant_prices",
            "product_variant",
        )

    def to_representation(self, insatnce):
        context = super(ProductDetailsSerializer, self).to_representation(insatnce)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['variants'] = list(variants.all())
        return context

    def get_product_variant_prices(self, obj):
        return ProductVariantPriceSerializer(obj.variations, many=True).data
    
    def get_product_variant(self, obj):
        context = ProductVariant.objects.filter(product__id=obj.id)
        variants = []
        product_variant_ids = list(context.values("variant").annotate(Count("variant")))
        for data in product_variant_ids:
            product_variant = Variant.objects.get(id=data.get('variant'))
            variant_tags = list(ProductVariant.objects.filter(variant=product_variant, product=obj).values("id", "variant_title"))
            tags = []
            tag_ids = []
            for tag in variant_tags:
                tags.append(tag.get('variant_title'))
                tag_ids.append(tag.get('id'))
            variants.append(
                {"option": product_variant.id, "title": product_variant.title, "tags": tags, "tag_ids": tag_ids}
            )
        return variants