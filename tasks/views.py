from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Task, Category, ContextEntry
from .serializers import (
    TaskSerializer, TaskListSerializer, TaskCreateSerializer,
    CategorySerializer, ContextEntrySerializer
)
from .ai_module import ai_manager


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task model with full CRUD operations
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return tasks for the current user"""
        return Task.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a task"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        """Toggle task status between pending and completed"""
        task = self.get_object()
        if task.status == 'pending':
            task.status = 'completed'
        elif task.status == 'completed':
            task.status = 'pending'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get current user's tasks with filtering options"""
        queryset = self.get_queryset()
        
        # Filter by status
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = request.query_params.get('priority', None)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Search by title
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        serializer = TaskListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get task statistics for the current user"""
        queryset = self.get_queryset()
        
        total_tasks = queryset.count()
        completed_tasks = queryset.filter(status='completed').count()
        pending_tasks = queryset.filter(status='pending').count()
        in_progress_tasks = queryset.filter(status='in_progress').count()
        
        # AI-powered insights
        high_priority_tasks = queryset.filter(priority_score__gte=0.7).count()
        overdue_tasks = queryset.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        stats = {
            'total': total_tasks,
            'completed': completed_tasks,
            'pending': pending_tasks,
            'in_progress': in_progress_tasks,
            'high_priority': high_priority_tasks,
            'overdue': overdue_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        }
        
        return Response(stats)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        """Return categories for the current user's tasks"""
        user_categories = Category.objects.filter(
            task__user=self.request.user
        ).distinct()
        return user_categories


class ContextEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for ContextEntry model with AI processing"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContextEntrySerializer
    
    def get_queryset(self):
        """Return context entries for the current user"""
        return ContextEntry.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Process context entry with AI analysis"""
        context_entry = serializer.save(user=self.request.user)
        
        # AI processing
        analysis = ai_manager.analyze_context(
            context_entry.content, 
            context_entry.source_type
        )
        
        # Update with AI insights
        context_entry.processed_insights = analysis
        context_entry.keywords = analysis.get('keywords', [])
        context_entry.sentiment_score = self._calculate_sentiment_score(analysis.get('sentiment', 'neutral'))
        context_entry.priority_score = self._calculate_priority_score(analysis)
        context_entry.save()
    
    def _calculate_sentiment_score(self, sentiment: str) -> float:
        """Convert sentiment to numeric score"""
        sentiment_map = {
            'positive': 0.8,
            'negative': 0.2,
            'neutral': 0.5
        }
        return sentiment_map.get(sentiment.lower(), 0.5)
    
    def _calculate_priority_score(self, analysis: dict) -> float:
        """Calculate priority score from analysis"""
        priorities = analysis.get('priorities', [])
        if 'high' in priorities or 'urgent' in priorities:
            return 0.8
        elif 'important' in priorities:
            return 0.6
        else:
            return 0.4
    
    @action(detail=False, methods=['post'])
    def ai_suggestions(self, request):
        """Get AI-powered suggestions for task creation"""
        title = request.data.get('title', '')
        description = request.data.get('description', '')
        
        if not title:
            return Response({'error': 'Title is required'}, status=400)
        
        # Get recent context for AI processing
        recent_context = ContextEntry.objects.filter(
            user=request.user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values('content', 'source_type')[:10]
        
        # Generate AI suggestions
        suggestions = {
            'priority_score': ai_manager.prioritize_task(title, description, list(recent_context)),
            'suggested_deadline': None,
            'category': 'General',
            'tags': [],
            'enhanced_description': ''
        }
        
        # Suggest deadline
        current_workload = Task.objects.filter(user=request.user, status='pending').count()
        suggested_deadline = ai_manager.suggest_deadline(title, description, current_workload)
        if suggested_deadline:
            suggestions['suggested_deadline'] = suggested_deadline.isoformat()
        
        # Suggest category and tags
        category_name, tags = ai_manager.suggest_categories_and_tags(title, description)
        suggestions['category'] = category_name
        suggestions['tags'] = tags
        
        # Enhance description
        enhanced_description = ai_manager.enhance_task_description(title, description, list(recent_context))
        suggestions['enhanced_description'] = enhanced_description
        
        return Response(suggestions)
