import itertools

from django.shortcuts import get_object_or_404

from django.contrib import messages

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from product.models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductVariantPrice,
    Variant
)
from .serializers import (
    ProductSerializer,
    ProductDetailsSerializer,
    ProductVariantPriceSerializer
)


def create_product_variant_and_get_combination(request, product):
    data = request.data
    product_variants = data['product_variant']
    tag_list = []
    new_tags = []

    for variant in product_variants:
        option = variant['option']
        tags = variant['tags']
        attribute = Variant.objects.get(pk=option)
        
        for tag in tags:
            product_variant, created = ProductVariant.objects.get_or_create(
                variant_title=tag,
                variant=attribute,
                product=product
            )
            new_tags.append(product_variant.id)

        tag_list.append(new_tags)
        new_tags = []
    
    return tag_list


class CreateProductApi(APIView):

    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, *args, **kwargs):
        data = self.request.data
        product_images = data['product_image']
        product_variant_prices = data['product_variant_prices']
        tag_list = []

        serializer = ProductSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        for image in product_images:
            ProductImage.objects.create(
                product=product,
                file_path=image
            )
        
        tag_list = create_product_variant_and_get_combination(self.request, product)
        
        for (index, tags) in enumerate(list(itertools.product(*tag_list))):
            number_of_tags = len(tags)

            if number_of_tags == 1:
                ProductVariantPrice.objects.create(
                    product_variant_one=ProductVariant.objects.get(id=tags[0]),
                    price=float(product_variant_prices[index]['price']),
                    stock=float(product_variant_prices[index]['stock']),
                    product=product

                )
            elif number_of_tags == 2:
                ProductVariantPrice.objects.create(
                    product_variant_one=ProductVariant.objects.get(id=tags[0]),
                    product_variant_two=ProductVariant.objects.get(id=tags[1]),
                    price=float(product_variant_prices[index]['price']),
                    stock=float(product_variant_prices[index]['stock']),
                    product=product
                )
            elif number_of_tags == 3:
                ProductVariantPrice.objects.create(
                    product_variant_one=ProductVariant.objects.get(id=tags[0]),
                    product_variant_two=ProductVariant.objects.get(id=tags[1]),
                    product_variant_three=ProductVariant.objects.get(id=tags[2]),
                    price=float(product_variant_prices[index]['price']),
                    stock=float(product_variant_prices[index]['stock']),
                    product=product
                )

        messages.success(self.request, "Product has been added successfully !")
        return Response(
            {"success": True, "success_url": "/product/list/"},
            status=status.HTTP_201_CREATED
        )


class RetrieveProductApi(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, *args, **kwargs):
        queryset = get_object_or_404(Product, pk=kwargs.get('pk'))
        serializer = ProductDetailsSerializer(queryset)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class EditProductApi(APIView):

    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('pk'))
        data = self.request.data
        product_images = data['product_image']
        product_variant_prices = data['product_variant_prices']
        updated_and_newly_created_product_variant_prices = []
        total_availabe_product_variants = []

        serializer = ProductSerializer(product, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        for image in product_images:
            ProductImage.objects.create(
                product=product,
                file_path=image
            )

        for variant_price in product_variant_prices:
            if not variant_price.get('new'):
                product_varint_price = ProductVariantPrice.objects.filter(id=variant_price.get('id'))
                if product_varint_price.exists():
                    new_price = product_varint_price.first()
                    new_price.price = variant_price.get('price')
                    new_price.stock = variant_price.get('stock')  
                    new_price.save()
                    
                    updated_and_newly_created_product_variant_prices.append(new_price.id)
                    variant_one = new_price.product_variant_one
                    variant_two = new_price.product_variant_two
                    variant_three = new_price.product_variant_three

                    if variant_one:
                        total_availabe_product_variants.append(
                            ProductVariant.objects.get(id=variant_one.id).id
                        )
                    if variant_two:
                        total_availabe_product_variants.append(
                            ProductVariant.objects.get(id=variant_two.id).id
                        )
                    if variant_three:
                        total_availabe_product_variants.append(
                            ProductVariant.objects.get(id=variant_three.id).id
                        )
            else:
                list_of_variant_titles = str(variant_price.get('title')).split('/')

                new_variants = list_of_variant_titles[0:len(list_of_variant_titles) - 1]
                list_of_options = str(variant_price.get('options')).split('/')
                options = list_of_options[0:len(list_of_options)]
                number_of_variants = len(new_variants)
                new_product_variants_to_add = []
               
                if number_of_variants == 1:
                    for (index, variant) in enumerate(new_variants):
                        new_product_variant, created = ProductVariant.objects.get_or_create(
                            variant_title=variant,
                            variant=Variant.objects.get(id=int(options[index])),
                            product=product
                        )
                        new_product_variants_to_add.append(new_product_variant.id)
                        total_availabe_product_variants.append(new_product_variant.id)

                    new_product_variant_price = ProductVariantPrice.objects.create(
                        product_variant_one=new_product_variant,
                        price=float(variant_price.get('price')),
                        stock=float(variant_price.get('stock')),
                        product=product
                    )
                    new_product_variants_to_add = []
                    updated_and_newly_created_product_variant_prices.append(new_product_variant_price.id)

                elif number_of_variants == 2:
                    for (index, variant) in enumerate(new_variants):
                        new_product_variant, created = ProductVariant.objects.get_or_create(
                            variant_title=variant,
                            variant=Variant.objects.get(id=int(options[index])),
                            product=product
                        )
                        new_product_variants_to_add.append(new_product_variant.id)
                        total_availabe_product_variants.append(new_product_variant.id)

                    new_product_variant_price = ProductVariantPrice.objects.create(
                        product_variant_one=ProductVariant.objects.get(id=new_product_variants_to_add[0]),
                        product_variant_two=ProductVariant.objects.get(id=new_product_variants_to_add[1]),
                        price=float(variant_price.get('price')),
                        stock=float(variant_price.get('stock')),
                        product=product
                    )
                    new_product_variants_to_add = []
                    updated_and_newly_created_product_variant_prices.append(new_product_variant_price.id)
                
                elif number_of_variants == 3:
                    for (index, variant) in enumerate(new_variants):
                        new_product_variant, created = ProductVariant.objects.get_or_create(
                            variant_title=variant,
                            variant=Variant.objects.get(id=int(options[index])),
                            product=product
                        )
                        new_product_variants_to_add.append(new_product_variant.id)
                        total_availabe_product_variants.append(new_product_variant.id)

                    new_product_variant_price = ProductVariantPrice.objects.create(
                        product_variant_one=ProductVariant.objects.get(id=new_product_variants_to_add[0]),
                        product_variant_two=ProductVariant.objects.get(id=new_product_variants_to_add[1]),
                        product_variant_three=ProductVariant.objects.get(id=new_product_variants_to_add[2]),
                        price=float(variant_price.get('price')),
                        stock=float(variant_price.get('stock')),
                        product=product
                    )
                    new_product_variants_to_add = []
                    updated_and_newly_created_product_variant_prices.append(new_product_variant_price.id)

        removed_product_variant_prices = ProductVariantPrice.objects.filter(
            product=product
        ).exclude(
            id__in=list(set(updated_and_newly_created_product_variant_prices))
        )
        removed_product_variants = ProductVariant.objects.filter(
            product=product
        ).exclude(
            id__in=list(set(total_availabe_product_variants))
        )

        removed_product_variant_prices.delete()
        removed_product_variants.delete()
            

        messages.success(self.request, "Product has been updated successfully !")
        return Response(
            {"success": True, "success_url": "/product/list/"},
            status=status.HTTP_200_OK
        )
