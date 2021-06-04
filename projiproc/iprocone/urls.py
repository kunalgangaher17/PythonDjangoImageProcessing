from django.urls import path
from . import views
urlpatterns=[path('',views.index,name='index'),
path('getState',views.getState,name='getState'),
path('openFile',views.openFile,name='openFile'),
path('getImage',views.getImage,name='getImage'),
path('closeFile',views.closeFile,name='closeFile'),
path('toGrayscale',views.toGrayscale,name='toGrayscale'),
path('scaleIt',views.scaleIt,name='scaleIt'),
path('rotateIt',views.rotateIt,name='rotateIt'),
path('setBorder',views.setBorder,name='setBorder'),
path('downloadFile',views.downloadFile,name='downloadFile'),
path('enhanceImage',views.enhanceImage, name="enhanceImage"),
path('flipImageHorizontally',views.flipImageHorizontally, name="flipImageHorizontally"),
path('flipImageVertically',views.flipImageVertically, name="flipImageVertically"),
path('filterImage',views.filterImage, name="filterImage"),
]