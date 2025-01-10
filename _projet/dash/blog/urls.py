from django.urls import path

from blog.models import Category
# from . import views
from .views import AddPostView, HomeView, ArticleDetailView, UpdatePostView, deletePostView, AddCategoryView, CategoryView, CategoryListView, LikeView, AddCommentView

app_name = 'blog'

urlpatterns = [
    #path('', views.home, name="home"),
    path('', HomeView.as_view(), name="home"),
    path('article/<int:pk>', ArticleDetailView.as_view(), name="article-detail"),
    path('addPost/', AddPostView.as_view(), name='add_post'),
    path('addCatgeory/', AddCategoryView.as_view(), name='add_category'),
    path('article/edit/<int:pk>', UpdatePostView.as_view(), name='update_post'),
    path('article/<int:pk>/remove', deletePostView.as_view(), name='delete_post'),
    path('category/<str:cats>/', CategoryView, name='category'),
    path('category-list/', CategoryListView, name='category-list'),
    path('like/<int:pk>', LikeView , name='like_post'),
    path('article/<int:pk>/comment/', AddCommentView.as_view(), name='add_comment'),

    
]