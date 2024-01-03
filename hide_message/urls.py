from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('encodage/', page_encodage, name='page_encodage'),
    path('decodage/', page_decodage, name='page_decodage'),

    path('encodage/text-image/', encode_text_in_image, name='encodage_text_image'),
    path('encodage/image-image/', encode_image_in_image, name='encodage_image_image'),
    path('encodage/doc-image/', encode_doc_in_image, name='encodage_doc_image'),

    path('decodage/text/result/', decode_text_from_image, name='decode_text_from_image'),
    path('decodage/image/result/', decode_image_from_image, name='decode_image_from_image'),
    path('decodage/document/result/', decode_doc_from_image, name='decode_doc_from_image'),
]
