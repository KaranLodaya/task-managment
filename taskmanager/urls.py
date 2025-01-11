from django.urls import path,include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from .views import TaskListCreateView,DeadlineExtensionRequestListCreateView,DeadlineExtensionApprovalListView,DeadlineExtensionApprovalRetriveUpdateView, LoginAPIView




urlpatterns = [

    #auth urls
    path('login/', LoginAPIView.as_view(), name='login'),

    # path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Task views
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),

    #task Detail view
    path('tasks/<int:pk>/', TaskListCreateView.as_view(), name='task-detail'),
    
    # Deadline Extension Request views
    path('deadline-extension-requests/', DeadlineExtensionRequestListCreateView.as_view(), name='deadline-extension-request-list-create'),
    
    # Deadline Extension Approval views
    path('deadline-extension-approvals/', DeadlineExtensionApprovalListView.as_view(), name='deadline-extension-approval-list'),
    path('deadline-extension-approvals/<int:pk>/', DeadlineExtensionApprovalRetriveUpdateView.as_view(), name='deadline-extension-approval-update'),
    
    path('auth/', obtain_auth_token, name='auth'),

    # If you are using DefaultRouter for ModelViewSets (uncomment above if needed)
    # path('api/', include(router.urls)),
]
