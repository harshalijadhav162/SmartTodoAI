from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Task, Category, ContextEntry
from .ai_module import ai_manager


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (nested in Task serializer)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    """Main serializer for Task model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'due_date', 'created_at',
            'updated_at', 'completed_at', 'user', 'user_id'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    
    def validate_title(self, value):
        """Validate that title is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()
    
    def validate_due_date(self, value):
        """Validate that due_date is not in the past"""
        from django.utils import timezone
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
    
    def create(self, validated_data):
        """Override create to handle user assignment"""
        user_id = validated_data.pop('user_id', None)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                validated_data['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this ID does not exist.")
        else:
            # If no user_id provided, use the current user from request
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['user'] = request.user
            else:
                raise serializers.ValidationError("User is required.")
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Override update to handle status changes and completed_at field"""
        # If status is being changed to completed, set completed_at
        if 'status' in validated_data and validated_data['status'] == 'completed':
            from django.utils import timezone
            validated_data['completed_at'] = timezone.now()
        elif 'status' in validated_data and validated_data['status'] != 'completed':
            # If status is changed from completed to something else, clear completed_at
            validated_data['completed_at'] = None
        
        return super().update(instance, validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing tasks"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'status_display', 'priority', 
            'priority_display', 'due_date', 'created_at', 'user'
        ]
        read_only_fields = ['id', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'usage_frequency']


class ContextEntrySerializer(serializers.ModelSerializer):
    """Serializer for ContextEntry model"""
    class Meta:
        model = ContextEntry
        fields = ['id', 'content', 'source_type', 'source_title', 'processed_insights', 
                 'priority_score', 'keywords', 'sentiment_score', 'created_at']
        read_only_fields = ['processed_insights', 'priority_score', 'keywords', 'sentiment_score']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new tasks with AI integration"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 'category']
    
    def validate_title(self, value):
        """Validate that title is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """Create task with AI-powered enhancements"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        else:
            raise serializers.ValidationError("User is required.")
        
        # Get recent context entries for AI processing
        recent_context = ContextEntry.objects.filter(
            user=request.user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values('content', 'source_type')[:10]
        
        # AI-powered enhancements
        title = validated_data.get('title', '')
        description = validated_data.get('description', '')
        
        # Calculate priority score
        priority_score = ai_manager.prioritize_task(title, description, list(recent_context))
        validated_data['priority_score'] = priority_score
        
        # Suggest deadline
        current_workload = Task.objects.filter(user=request.user, status='pending').count()
        suggested_deadline = ai_manager.suggest_deadline(title, description, current_workload)
        if suggested_deadline:
            validated_data['suggested_deadline'] = suggested_deadline
        
        # Suggest category and tags
        category_name, tags = ai_manager.suggest_categories_and_tags(title, description)
        if category_name:
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'color': '#3B82F6'}
            )
            validated_data['category'] = category
            validated_data['tags'] = tags
        
        # Enhance description
        enhanced_description = ai_manager.enhance_task_description(title, description, list(recent_context))
        validated_data['ai_enhanced_description'] = enhanced_description
        
        return super().create(validated_data)
