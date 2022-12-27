from django.urls import path
from django.views.generic import TemplateView

from product.views.product import (
    CreateProductView,
    ListProductView,
    EditProductView
)
from product.views.variant import (
    VariantView,
    VariantCreateView,
    VariantEditView
)
from product.apis.views import (
    CreateProductApi,
    RetrieveProductApi,
    EditProductApi,
)

app_name = "product"

urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),

    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('list/', ListProductView.as_view(extra_context={
        'product': True
    }), name='list.product'),
    path('edit/<int:pk>/', EditProductView.as_view(extra_context={
        'product': True
    }), name='edit.product'),
    
     # Product rest api
    path('create-new-product/', CreateProductApi.as_view(), name='create-new-product'),
    path('retrieve-product/<int:pk>/', RetrieveProductApi.as_view(), name='retrieve-product'),
    path('edit-product/<int:pk>/', EditProductApi.as_view(), name='edit-product'),
]
