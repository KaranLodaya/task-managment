from rest_framework.generics import ListCreateAPIView, ListAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, IsAdminUser, BasePermission, AllowAny
from rest_framework.response import Response
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from .models import Task, DeadlineExtensionLog
from django.contrib.auth import authenticate
from .serializers import TaskSerializer, DeadlineExtensionRequestSerializer, DeadlineExtensionApprovalSerializer , LoginSerializer
from .filters import TaskFilter, DeadlineExtensionLogFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# from permissions import DjangoModelPermissions

class CustomPermissions(BasePermission):
    """
    Custom permissions for Task and Deadline Extension Request views.
    """
    def has_permission(self, request, view):
        user = request.user

        # Ensure the user is authenticated
        if not user.is_authenticated:
            return False

        # Permissions for Task views
        if isinstance(view, TaskListCreateView):# or isinstance(view, TaskDetailView):
            # Developers can only view tasks
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return user.has_perm('taskmanager.view_task')

            # Task Providers can create tasks
            if request.method == 'POST':
                return user.has_perm('taskmanager.add_task')

            # Task Providers can update/delete tasks
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return user.has_perm('taskmanager.change_task') or user.has_perm('taskmanager.delete_task')




        # Permissions for Deadline Extension Request views
        if isinstance(view, DeadlineExtensionRequestListCreateView) :
            # Both roles can view requests
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return user.has_perm('taskmanager.view_deadlineextensionlog')

            # Developers can create requestsc
            if request.method == 'POST' and not request.user.groups.filter(name='Task Providers').exists():
                return user.has_perm('taskmanager.add_deadlineextensionlog')

            # Task Providers can update or delete requests
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return user.has_perm('taskmanager.change_deadlineextensionlog') or user.has_perm('taskmanager.delete_deadlineextensionlog')


        if isinstance(view, DeadlineExtensionApprovalListView) or isinstance(view, DeadlineExtensionApprovalRetriveUpdateView):
            # Developers can not approve requests
            if request.method in ['PUT', 'PATCH', 'DELETE','GET', 'HEAD', 'OPTIONS']:
                return user.has_perm('taskmanager.change_deadlineextensionlog') or user.has_perm('taskmanager.delete_deadlineextensionlog')

        
        # Default to deny all other methods
        return False


#View for create and read tasks 
class TaskListCreateView(ListCreateAPIView):
    """
    List all tasks and allow task creation.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = TaskFilter
    permission_classes = [IsAuthenticated, CustomPermissions]


    def perform_create(self, serializer):
        """
        Automatically set the logged-in user as the task creator.
        """
        serializer.save(assigned_by=self.request.user)



#view for create request and read request
class DeadlineExtensionRequestListCreateView(ListCreateAPIView):
    """
    List all deadline extension requests and allow creating new extension requests.
    """
    queryset = DeadlineExtensionLog.objects.all()
    serializer_class = DeadlineExtensionRequestSerializer
    permission_classes = [IsAuthenticated, CustomPermissions]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = DeadlineExtensionLogFilter

    def perform_create(self, serializer):
        """
        Automatically set the logged-in user as the requestor for deadline extension.
        """
        serializer.save(request_by=self.request.user)

#view for read requests
class DeadlineExtensionApprovalListView(ListAPIView):
    """
    List all deadline extension requests for Task Providers to approve or reject.
    """
    serializer_class = DeadlineExtensionApprovalSerializer
    permission_classes = [IsAuthenticated, CustomPermissions]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = DeadlineExtensionLogFilter

    def get_queryset(self):
        user = self.request.user
        return DeadlineExtensionLog.objects.filter(task__assigned_by=user)




#view for read and update a specific request
class DeadlineExtensionApprovalRetriveUpdateView(RetrieveUpdateAPIView):
    """
    Approve or reject a specific deadline extension request.
    """
    queryset = DeadlineExtensionLog.objects.all()
    serializer_class = DeadlineExtensionApprovalSerializer
    permission_classes = [IsAuthenticated, CustomPermissions]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        kwargs['partial'] = partial

        # Perform the update operation
        response = super().update(request, *args, **kwargs)

        # Extract the updated status from the response
        updated_status = response.data.get("status", "").upper()

        # Set a custom message based on the status
        if updated_status == "APPROVED":
            message = "The deadline extension request has been approved successfully."
        elif updated_status == "REJECTED":
            message = "The deadline extension request has been rejected successfully."
        else:
            message = "The deadline extension request has been updated."

        # Customize the response data
        response.data = {
            "status": "success",
            "message": message,
            "data": response.data,
        }

        return response

    


# class SignupAPIView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         email = request.data.get('email')

#         if not username or not password:
#             return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

#         if User.objects.filter(username=username).exists():
#             return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

#         user = User.objects.create_user(username=username, password=password, email=email)
#         token = Token.objects.create(user=user)

#         return Response({"message": "User created successfully", "token": token.key}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # Authenticate user using username and password
            user = authenticate(username=serializer.data['username'], password=serializer.data['password'])
            if user:
                # Generate JWT tokens (Access and Refresh)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'id': user.id,
                    'username':user.username,
                    'email':user.email,
                    'access_token': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'Message': 'Invalid Username or Password'}, status=status.HTTP_401_UNAUTHORIZED)