from django.urls import path
from .views import *
    
app_name = "plag"
urlpatterns = [ 
    path('', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('registration/<str:role>/', registration, name='registration'),

    path('logout/', logout_view, name='logout'),
    path('checkplagiarism/', checkPlag, name='checkplagiarism'),
    path('dictionary/', dictionary, name='dictionary'),
    path('work/', work, name='work'),
    path('results/<str:text>/', results, name='results'),
   

    path('profile/', profile, name='profile'),

    path('?/<str:role>/', users, name='users'),

    path('upload/', upload, name='upload'),
    path('pdfview/<str:pdf_file>/', view_pdf, name='viewpdf'),


    
   ]