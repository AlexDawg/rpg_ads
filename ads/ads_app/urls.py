from django.urls import path
from . import views
from .views import AdsList, AdsCreate, AdsDetail, CommentView, AdUpdate, AdDelete, MyResponsesView, delete_comment, \
    accept_comment

urlpatterns = [
    path('', AdsList.as_view(), name='ads_list'),
    path('create/', AdsCreate.as_view(), name='ads_create'),
    path('<int:pk>', AdsDetail.as_view(), name='ads_detail'),
    path('comment/', CommentView.as_view(), name='comment_list'),
    path('edit/<int:pk>/', AdUpdate.as_view(), name='ad_edit'),
    path('delete/<int:pk>/', AdDelete.as_view(), name='ad_delete'),
    path('my-responses/', MyResponsesView.as_view(), name='my_responses'),
    path('delete-comment/<int:pk>/', delete_comment, name='delete_comment'),
    path('accept-comment/<int:pk>/', accept_comment, name='accept_comment'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('profile_list/', views.profile_list, name='profile_list'),

]