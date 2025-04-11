from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HelloWorldSerializer, NoteImageSerializer
from .filters import HierarchicalSectionFilterBackend
import time
import json
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

# Waktu cache default ( 2 jam)
CACHE_TTL = getattr(settings, 'CACHE_TTL', 60 * 60 * 2)

class HelloWorldAPIView(APIView):
    """
    A simple API view that returns a hello world message
    """
    
    def get(self, request, format=None):
        """
        Return a simple hello world message
        """
        # Gunakan cache untuk endpoint sederhana ini juga
        cache_key = "hello_world"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
            
        content = {'message': 'Hello, World!'}
        cache.set(cache_key, content, CACHE_TTL)
        return Response(content)
    
    def post(self, request, format=None):
        """
        Return a personalized hello message with the provided name
        """
        serializer = HelloWorldSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('your_name', 'World')
            content = {'message': f'Hello, {name}!'}
            return Response(content)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Add to the top of views.py
import django_filters
from .models import Element

class ElementFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    due_after = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='gte')
    due_before = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='lte')
    
    class Meta:
        model = Element
        fields = {
            'type': ['exact'],
            'section': ['exact'],
            'is_archived': ['exact'],
            'is_favorite': ['exact'],
            'is_completed': ['exact'],
        }


from rest_framework.pagination import PageNumberPagination

class FlexiblePagination(PageNumberPagination):
    page_size = 10
    max_page_size = 1000
    page_size_query_param = 'page_size'

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tag, Section, Element, StudySession, StudyRecord
from .serializers import (
    TagSerializer, SectionSerializer, ElementSerializer, ElementDetailSerializer,
    StudySessionSerializer, StudyRecordSerializer, FlashcardSerializer,
    QuestionSerializer, MultipleChoiceSerializer, TodoSerializer, NoteSerializer
)

class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, HierarchicalSectionFilterBackend]
    search_fields = ['name']
    ordering_fields = ['name']
    
    def get_queryset(self):
        # Only return tags created by the current user
        return Tag.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache terkait dengan tags
        cache_key = f"tags_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache terkait dengan tags
        cache_key = f"tags_list_{request.user.id}"
        cache.delete(cache_key)
        # Hapus cache detail tag
        detail_cache_key = f"tag_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait dengan tags
        cache_key = f"tags_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def list(self, request, *args, **kwargs):
        # Membuat cache_key yang unik berdasarkan user dan filter
        params = request.query_params.copy()
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"tags_list_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"tag_detail_{kwargs.get('pk')}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response

class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    pagination_class = FlexiblePagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend, HierarchicalSectionFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'order']
    filterset_fields = ['parent']
    
    def get_queryset(self):
        # Only return sections created by the current user
        return Section.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache list sections
        cache_key = f"sections_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache list dan detail
        cache_key = f"sections_list_{request.user.id}"
        cache.delete(cache_key)
        detail_cache_key = f"section_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        # Juga hapus cache elements dalam section
        elements_cache_key = f"section_elements_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(elements_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait
        cache_key = f"sections_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def list(self, request, *args, **kwargs):
        # Membuat cache_key yang unik berdasarkan user dan filter
        params = request.query_params.copy()
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"sections_list_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"section_detail_{kwargs.get('pk')}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    @action(detail=True, methods=['get'])
    def elements(self, request, pk=None):
        """Get all elements in this section"""
        cache_key = f"section_elements_{pk}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
            
        #print(f"Cache miss for {cache_key}")
        section = self.get_object()
        elements = Element.objects.filter(section=section, user=request.user)
        serializer = ElementSerializer(elements, many=True)
        cache.set(cache_key, serializer.data, CACHE_TTL)
        return Response(serializer.data)

class ElementViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ElementFilter
    pagination_class = FlexiblePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend, HierarchicalSectionFilterBackend]
    search_fields = ['title', 'content', 'additional_content']
    ordering_fields = ['title', 'created_at', 'updated_at', 'order']
    filterset_fields = ['type', 'section', 'tags', 'is_archived', 'is_favorite', 'is_completed']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            return ElementDetailSerializer
        return ElementSerializer
    
    def get_queryset(self):
        # Only return elements created by the current user
        return Element.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache element list
        self._invalidate_element_cache(request)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache detail dan list
        self._invalidate_element_cache(request)
        detail_cache_key = f"element_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait
        self._invalidate_element_cache(request)
        return response
    
    def _invalidate_element_cache(self, request):
        """Helper method to invalidate element caches"""
        element_types = ['element', 'flashcard', 'question', 'todo', 'note']
        for element_type in element_types:
            cache_key = f"{element_type}_list_{request.user.id}"
            cache.delete(cache_key)
            
        # Juga invalidate section_elements cache
        section_id = request.data.get('section')
        if section_id:
            cache_key = f"section_elements_{section_id}_{request.user.id}"
            cache.delete(cache_key)
    
    def list(self, request, *args, **kwargs):
        # Membuat cache_key yang unik berdasarkan user dan filter
        params = request.query_params.copy()
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"element_list_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"element_detail_{kwargs.get('pk')}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark an element as complete"""
        element = self.get_object()
        element.mark_as_complete()
        self._invalidate_element_cache(request)
        return Response({'status': 'Element marked as complete'})
    
    @action(detail=True, methods=['post'])
    def incomplete(self, request, pk=None):
        """Mark an element as incomplete"""
        element = self.get_object()
        element.mark_as_incomplete()
        self._invalidate_element_cache(request)
        return Response({'status': 'Element marked as incomplete'})
    
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related elements"""
        cache_key = f"element_related_{pk}_{request.user.id}"
        relationship_type = request.query_params.get('type', None)
        if relationship_type:
            cache_key += f"_{relationship_type}"
            
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
            
        #print(f"Cache miss for {cache_key}")
        element = self.get_object()
        related_elements = element.get_related_elements(relationship_type)
        serializer = ElementSerializer(related_elements, many=True)
        cache.set(cache_key, serializer.data, CACHE_TTL)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_related(self, request, pk=None):
        """Add a related element"""
        element = self.get_object()
        related_id = request.data.get('related_id')
        relationship_type = request.data.get('relationship_type', 'related')
        
        try:
            related_element = Element.objects.get(id=related_id, user=request.user)
            element.add_related_element(related_element, relationship_type)
            # Invalidate related cache
            cache_key = f"element_related_{pk}_{request.user.id}"
            cache.delete(cache_key)
            return Response({'status': 'Related element added'})
        except Element.DoesNotExist:
            return Response(
                {'error': 'Related element not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Update multiple elements at once"""
        element_ids = request.data.get('element_ids', [])
        update_data = request.data.get('update_data', {})
        
        if not element_ids or not update_data:
            return Response(
                {'error': 'Both element_ids and update_data are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get elements owned by the current user
        elements = Element.objects.filter(
            id__in=element_ids,
            user=request.user
        )
        
        # Validate that all requested elements exist
        if len(elements) != len(element_ids):
            return Response(
                {'error': 'One or more elements not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Only allow specific fields to be updated in bulk
        allowed_fields = [
            'section', 'is_archived', 'is_favorite', 
            'is_completed', 'order', 'due_date'
        ]
        
        update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        # Handle tag operations separately
        add_tags = request.data.get('add_tags', [])
        remove_tags = request.data.get('remove_tags', [])
        
        # Update elements
        updated_count = elements.update(**update_fields)
        
        # Handle tag operations
        if add_tags:
            tags_to_add = Tag.objects.filter(id__in=add_tags, user=request.user)
            for element in elements:
                element.tags.add(*tags_to_add)
        
        if remove_tags:
            tags_to_remove = Tag.objects.filter(id__in=remove_tags, user=request.user)
            for element in elements:
                element.tags.remove(*tags_to_remove)
        
        # Invalidate element caches
        self._invalidate_element_cache(request)
        
        return Response({
            'status': 'success',
            'updated_count': updated_count,
            'affected_elements': element_ids
        })

class FlashcardViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardSerializer
    pagination_class = FlexiblePagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend, HierarchicalSectionFilterBackend]
    search_fields = ['title', 'content', 'additional_content']
    ordering_fields = ['title', 'created_at', 'updated_at', 'order']
    filterset_fields = ['section', 'tags', 'is_archived', 'is_favorite']
    
    def get_queryset(self):
        # Only return flashcards created by the current user
        return Element.objects.filter(
            user=self.request.user,
            type=Element.FLASHCARD
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache list
        cache_key = f"flashcard_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache list dan detail
        cache_key = f"flashcard_list_{request.user.id}"
        cache.delete(cache_key)
        detail_cache_key = f"flashcard_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait
        cache_key = f"flashcard_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def list(self, request, *args, **kwargs):
        # Membuat cache_key yang unik berdasarkan user dan filter
        params = request.query_params.copy()
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"flashcard_list_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"flashcard_detail_{kwargs.get('pk')}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    @action(detail=True, methods=['get'])
    def next(self, request, pk=None):
        """Get the next flashcard after this one"""
        cache_key = f"flashcard_next_{pk}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
            
        #print(f"Cache miss for {cache_key}")
        current = self.get_object()
        next_flashcard = Element.objects.filter(
            user=request.user,
            type=Element.FLASHCARD,
            id__gt=current.id
        ).order_by('id').first()
        
        if not next_flashcard:
            next_flashcard = Element.objects.filter(
                user=request.user,
                type=Element.FLASHCARD
            ).order_by('id').first()
        
        if next_flashcard:
            serializer = FlashcardSerializer(next_flashcard)
            cache.set(cache_key, serializer.data, CACHE_TTL)
            return Response(serializer.data)
        
        return Response({'error': 'No flashcards available'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def previous(self, request, pk=None):
        """Get the previous flashcard before this one"""
        cache_key = f"flashcard_previous_{pk}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
            
        #print(f"Cache miss for {cache_key}")
        
        current = self.get_object()
        prev_flashcard = Element.objects.filter(
            user=request.user,
            type=Element.FLASHCARD,
            id__lt=current.id
        ).order_by('-id').first()
        
        if not prev_flashcard:
            return Response({'detail': 'No previous flashcard found'}, status=404)
        
        serializer = self.get_serializer(prev_flashcard)
        cache.set(cache_key, serializer.data, CACHE_TTL)
        return Response(serializer.data)

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    pagination_class = FlexiblePagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend, HierarchicalSectionFilterBackend]
    search_fields = ['title', 'content']
    ordering_fields = ['title', 'created_at', 'updated_at', 'order', 'due_date']
    filterset_fields = ['section', 'tags', 'is_archived', 'is_favorite', 'is_completed']
    
    def get_queryset(self):
        # Only return todos created by the current user
        return Element.objects.filter(
            user=self.request.user,
            type=Element.TODO
        )
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache todo list
        self._invalidate_todo_cache(request)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache detail dan list
        self._invalidate_todo_cache(request)
        detail_cache_key = f"todo_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait
        self._invalidate_todo_cache(request)
        return response
    
    def _invalidate_todo_cache(self, request):
        """Helper method to invalidate todo caches"""
        cache_key = f"todo_list_{request.user.id}"
        cache.delete(cache_key)
        cache_key = f"todo_by_section_{request.user.id}"
        cache.delete(cache_key)
    
    def list(self, request, *args, **kwargs):
        # Membuat cache_key yang unik berdasarkan user dan filter
        params = request.query_params.copy()
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"todo_list_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"todo_detail_{kwargs.get('pk')}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a todo as complete"""
        todo = self.get_object()
        todo.mark_as_complete()
        self._invalidate_todo_cache(request)
        return Response({'status': 'Todo marked as complete'})
    
    @action(detail=True, methods=['post'])
    def incomplete(self, request, pk=None):
        """Mark a todo as incomplete"""
        todo = self.get_object()
        todo.mark_as_incomplete()
        self._invalidate_todo_cache(request)
        return Response({'status': 'Todo marked as incomplete'})
    
    @action(detail=False, methods=['get'])
    def by_section(self, request):
        """Get todos grouped by section"""
        section_id = request.query_params.get('id')
        params = request.query_params.copy()
        
        # Create a unique cache key
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"todo_by_section_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
            
        #print(f"Cache miss for {cache_key}")
        
        if not section_id:
            return Response(
                {'error': 'Section ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            section = Section.objects.get(id=section_id, user=request.user)
        except Section.DoesNotExist:
            return Response(
                {'error': 'Section not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all subsection IDs
        section_ids = [section.id]
        
        def get_subsection_ids(parent_id):
            subsections = Section.objects.filter(parent_id=parent_id, user=request.user)
            for subsection in subsections:
                section_ids.append(subsection.id)
                get_subsection_ids(subsection.id)
        
        get_subsection_ids(section.id)
        
        # Get todos in all those sections
        is_completed = request.query_params.get('is_completed')
        todos = Element.objects.filter(
            user=request.user,
            type=Element.TODO,
            section_id__in=section_ids
        )
        
        if is_completed is not None:
            is_completed = is_completed.lower() == 'true'
            todos = todos.filter(is_completed=is_completed)
        
        # Group by section
        result = {}
        for section_id in section_ids:
            section_todos = todos.filter(section_id=section_id)
            if section_todos.exists():
                try:
                    section = Section.objects.get(id=section_id)
                    result[section_id] = {
                        'section': {
                            'id': section.id,
                            'title': section.title
                        },
                        'todos': TodoSerializer(section_todos, many=True).data
                    }
                except Section.DoesNotExist:
                    pass
        
        cache.set(cache_key, result, CACHE_TTL)
        return Response(result)

class StudySessionViewSet(viewsets.ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FlexiblePagination
    
    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache list
        cache_key = f"study_session_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache list dan detail
        cache_key = f"study_session_list_{request.user.id}"
        cache.delete(cache_key)
        detail_cache_key = f"study_session_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait
        cache_key = f"study_session_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def list(self, request, *args, **kwargs):
        # Membuat cache_key yang unik berdasarkan user dan filter
        params = request.query_params.copy()
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"study_session_list_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"study_session_detail_{kwargs.get('pk')}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a study session"""
        session = self.get_object()
        session.end_session()
        self._invalidate_study_session_cache(request)
        serializer = StudySessionSerializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_record(self, request, pk=None):
        """Add a study record to a session"""
        session = self.get_object()
        
        # Validate the session is not ended
        if session.ended_at:
            return Response(
                {'error': 'Cannot add records to an ended session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get required data
        element_id = request.data.get('element_id')
        result = request.data.get('result')
        time_spent = request.data.get('time_spent')
        notes = request.data.get('notes', '')
        
        # Validate required fields
        if not element_id or not result:
            return Response(
                {'error': 'element_id and result are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate the element exists and belongs to the user
        try:
            element = Element.objects.get(id=element_id, user=request.user)
        except Element.DoesNotExist:
            return Response(
                {'error': 'Element not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create the study record
        record = StudyRecord.objects.create(
            session=session,
            element=element,
            result=result,
            time_spent=time_spent,
            notes=notes
        )
        
        serializer = StudyRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the active study session for the current user"""
        active_session = StudySession.objects.filter(
            user=request.user,
            ended_at=None
        ).first()
        
        if not active_session:
            return Response(
                {'error': 'No active study session found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudySessionSerializer(active_session)
        return Response(serializer.data)

    def _invalidate_study_session_cache(self, request):
        """Helper method to invalidate study session caches"""
        cache_key = f"study_session_list_{request.user.id}"
        cache.delete(cache_key)
        cache_key = f"study_session_active_{request.user.id}"
        cache.delete(cache_key)

class StudyRecordViewSet(viewsets.ModelViewSet):
    serializer_class = StudyRecordSerializer
    pagination_class = FlexiblePagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['session', 'element', 'result']
    
    def get_queryset(self):
        # Make sure we filter by session__user to maintain proper access control
        return StudyRecord.objects.filter(session__user=self.request.user)
        
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache record list
        self._invalidate_record_cache(request)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache detail dan list
        self._invalidate_record_cache(request)
        detail_cache_key = f"study_record_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait
        self._invalidate_record_cache(request)
        return response
    
    def _invalidate_record_cache(self, request):
        """Helper method to invalidate study record caches"""
        cache_key = f"study_record_list_{request.user.id}"
        cache.delete(cache_key)

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        # if not query:
        #     return Response({'error': 'No search query provided'}, status=status.HTTP_400_BAD_REQUEST)
        elements = Element.objects.filter(
            Q(user=request.user) &
            (Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(additional_content__icontains=query))
        )
        
        # Optional filtering by type
        element_type = request.query_params.get('type', None)
        if element_type:
            elements = elements.filter(type=element_type)
        
        # Optional filtering by section
        # In the SearchView.get method in views.py
        section_id = request.query_params.get('section', None)
        if section_id:
            # Get the section and all its subsections
            section_ids = [section_id]
            subsections = Section.objects.filter(parent_id=section_id, user=request.user)
            
            # Recursively find all subsections
            def get_subsection_ids(parent_id):
                subsection_ids = []
                subs = Section.objects.filter(parent_id=parent_id, user=request.user)
                for sub in subs:
                    subsection_ids.append(sub.id)
                    subsection_ids.extend(get_subsection_ids(sub.id))
                return subsection_ids
            
            # Add all subsection IDs to our filter list
            section_ids.extend(get_subsection_ids(section_id))
            
            # Filter elements that belong to the section or any of its subsections
            elements = elements.filter(section_id__in=section_ids)
        
        # Optional filtering by tag
        tag_id = request.query_params.get('tag', None)
        if tag_id:
            elements = elements.filter(tags__id=tag_id)
        
        serializer = ElementSerializer(elements, many=True)
        return Response(serializer.data)
    

# Add to views.py inside NoteViewSet
from .models import NoteImage

@action(detail=True, methods=['post'])
def upload_image(self, request, pk=None):
    """Upload an image to a note"""
    note = self.get_object()
    
    # Check if this is actually a note
    if note.type != Element.NOTE:
        return Response(
            {'error': 'This element is not a note'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle file upload
    image = request.FILES.get('image')
    if not image:
        return Response(
            {'error': 'No image provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    note_image = NoteImage.objects.create(note=note, image=image)
    serializer = NoteImageSerializer(note_image)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@action(detail=True, methods=['get'])
def images(self, request, pk=None):
    """Get all images for a note"""
    note = self.get_object()
    
    # Check if this is actually a note
    if note.type != Element.NOTE:
        return Response(
            {'error': 'This element is not a note'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    images = NoteImage.objects.filter(note=note)
    serializer = NoteImageSerializer(images, many=True)
    
    return Response(serializer.data)

class QuestionViewSet(viewsets.ModelViewSet):
    pagination_class = FlexiblePagination
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend, HierarchicalSectionFilterBackend]
    search_fields = ['title', 'content', 'additional_content']
    ordering_fields = ['title', 'created_at', 'updated_at', 'order']
    filterset_fields = ['section', 'tags', 'is_archived', 'is_favorite']
    
    def get_queryset(self):
        # Only return questions created by the current user
        return Element.objects.filter(
            user=self.request.user,
            type=Element.QUESTION
        )
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache list
        cache_key = f"question_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache list dan detail
        cache_key = f"question_list_{request.user.id}"
        cache.delete(cache_key)
        detail_cache_key = f"question_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait
        cache_key = f"question_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def list(self, request, *args, **kwargs):
        # Membuat cache_key yang unik berdasarkan user dan filter
        params = request.query_params.copy()
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"question_list_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"question_detail_{kwargs.get('pk')}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response

class MultipleChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = MultipleChoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FlexiblePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend, HierarchicalSectionFilterBackend]
    search_fields = ['title', 'content']
    ordering_fields = ['title', 'created_at', 'updated_at', 'order']
    filterset_fields = ['section', 'tags', 'is_archived', 'is_favorite']
    
    def get_queryset(self):
        # Only return multiple choice questions created by the current user
        return Element.objects.filter(
            user=self.request.user,
            type=Element.MULTIPLE_CHOICE
        )
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache list
        cache_key = f"multiple_choice_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache list dan detail
        cache_key = f"multiple_choice_list_{request.user.id}"
        cache.delete(cache_key)
        detail_cache_key = f"multiple_choice_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait
        cache_key = f"multiple_choice_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def list(self, request, *args, **kwargs):
        # Membuat cache_key yang unik berdasarkan user dan filter
        params = request.query_params.copy()
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"multiple_choice_list_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"multiple_choice_detail_{kwargs.get('pk')}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    pagination_class = FlexiblePagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend, HierarchicalSectionFilterBackend]
    search_fields = ['title', 'content']
    ordering_fields = ['title', 'created_at', 'updated_at', 'order']
    filterset_fields = ['section', 'tags', 'is_archived', 'is_favorite']
    
    def get_queryset(self):
        # Only return notes created by the current user
        return Element.objects.filter(
            user=self.request.user,
            type=Element.NOTE
        )
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Hapus cache list
        cache_key = f"note_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Hapus cache list dan detail
        cache_key = f"note_list_{request.user.id}"
        cache.delete(cache_key)
        detail_cache_key = f"note_detail_{kwargs.get('pk')}_{request.user.id}"
        cache.delete(detail_cache_key)
        return response
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Hapus cache terkait
        cache_key = f"note_list_{request.user.id}"
        cache.delete(cache_key)
        return response
    
    def list(self, request, *args, **kwargs):
        # Membuat cache_key yang unik berdasarkan user dan filter
        params = request.query_params.copy()
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        cache_key = f"note_list_{request.user.id}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"note_detail_{kwargs.get('pk')}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
        
        #print(f"Cache miss for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response
        
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload an image to a note"""
        note = self.get_object()
        
        # Check if this is actually a note
        if note.type != Element.NOTE:
            return Response(
                {'error': 'This element is not a note'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle file upload
        image = request.FILES.get('image')
        if not image:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        note_image = NoteImage.objects.create(note=note, image=image)
        # Clear cache for this note
        cache_key = f"note_detail_{pk}_{request.user.id}"
        cache.delete(cache_key)
        cache_key = f"note_images_{pk}_{request.user.id}"
        cache.delete(cache_key)
        
        serializer = NoteImageSerializer(note_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        """Get all images for a note"""
        cache_key = f"note_images_{pk}_{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            #print(f"Cache hit for {cache_key}")
            return Response(cached_data)
            
        note = self.get_object()
        
        # Check if this is actually a note
        if note.type != Element.NOTE:
            return Response(
                {'error': 'This element is not a note'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        images = NoteImage.objects.filter(note=note)
        serializer = NoteImageSerializer(images, many=True)
        
        cache.set(cache_key, serializer.data, CACHE_TTL)
        return Response(serializer.data)

class CacheClearView(APIView):
    """
    An endpoint to clear all caches in the application
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        """
        Clear all caches
        """
        # Clear all caches completely
        cache.clear()
        return Response({'status': 'success', 'message': 'All caches have been cleared'})