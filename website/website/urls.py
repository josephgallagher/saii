from django.conf.urls import include, url, patterns
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
# from oscar.app import application
from app import application


urlpatterns = patterns(

    url(r'^i18n/', include('django.conf.urls.i18n')),

    # The Django admin is not officially supported; expect breakage.
    # Nonetheless, it's often useful for debugging.
    url(r'^admin/', include(admin.site.urls)),

    #For future PayPal integration
    # (r'^checkout/paypal/', include('paypal.express.urls')),


    url(r'', include(application.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.DOCUMENT_URL, document_root=settings.DOCUMENT_ROOT)
