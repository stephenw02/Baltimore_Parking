from django.urls import path
from . import views

#URLConf
urlpatterns = [
    path('', views.say_hello),
    path('tickets_heatmap/', views.tickets_heatmap, name='tickets_heatmap'),
    path('tickets_plotmap/', views.tickets_plotmap, name='tickets_plotmap'),
    path('tickets_roadmap/', views.tickets_roadmap, name='tickets_roadmap'),
    path('towings_heatmap/', views.towings_heatmap, name='towings_heatmap'),
    path('towings_plotmap/', views.towings_plotmap, name='towings_plotmap'),
    path('towings_roadmap/', views.towings_roadmap, name='towings_roadmap'),
    path('extras/', views.extras_view, name='extras_view'),
]