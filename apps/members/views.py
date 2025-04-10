from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HelloWorldSerializer, NoteImageSerializer
# At the top of views.py, add this import
from .filters import HierarchicalSectionFilterBackend
import hashlib
from django.utils.http import quote_etag
from functools import wraps
# import time
# import json

# ETag decorator for REST API views
def etag_decorator(view_func):
    @wraps(view_func)
    def wrapped_view(self, request, *args, **kwargs):
        # Only apply ETags to GET requests
        if request.method != 'GET':
            return view_func(self, request, *args, **kwargs)
        
        # Print full request info for debugging
        # print(f"\n\n=== REQUEST INFO ===")
        # print(f"Path: {request.path}")
        # print(f"Method: {request.method}")
        # print(f"Query params: {request.GET}")
        # print(f"Headers: {json.dumps({k: v for k, v in request.META.items() if k.startswith('HTTP_')}, indent=2)}")
            
        # Execute the view to get the response
        response = view_func(self, request, *args, **kwargs)
        
        # Generate ETag from the response data
        if hasattr(response, 'data'):
            data_str = str(response.data).encode('utf-8')
            etag = quote_etag(hashlib.md5(data_str).hexdigest())
            
            # Set the ETag header
            response['ETag'] = etag
            #print(f"[ETag] Generated ETag: {etag} for {request.path}")
            
            # Check if the client sent an If-None-Match header
            if_none_match = request.META.get('HTTP_IF_NONE_MATCH')
            if if_none_match:
                #print(f"[ETag] Client sent If-None-Match: {if_none_match}")
                
                # Clean both ETags for comparison (remove W/ prefix and quotes)
                clean_server_etag = etag.replace('"', '')
                clean_client_etag = if_none_match.replace('W/', '').replace('"', '')
                
                #print(f"[ETag] Clean comparison - Server: {clean_server_etag}, Client: {clean_client_etag}")
                
                if clean_server_etag == clean_client_etag:
                    #print(f"\n$$$$$ CACHE BERHASIL: 304 Not Modified untuk {request.path} $$$$$")
                    #print(f"[ETag] 304 Not Modified returned for {request.path}")
                    # Return 304 Not Modified if the ETag matches
                    return Response(status=status.HTTP_304_NOT_MODIFIED)
                # else:
                    #print(f"\n$$$$$ CACHE GAGAL: Konten berubah untuk {request.path} $$$$$")
                    #print(f"[ETag] ETag changed, sending new content")
                    #print(f"[ETag] Server: {clean_server_etag}, Client: {clean_client_etag}")
                    # Add delay to simulate slow response when not cached
                    #print(f"[ETag] Sleeping for 5 seconds to simulate slow response...")
                    # time.sleep(5)  # Increased to 5 seconds to make it very noticeable
            # else:
                #print(f"\n$$$$$ CACHE TIDAK ADA: Request pertama atau ETag tidak dikirim untuk {request.path} $$$$$")
                # Add delay to simulate slow response when not cached
                #print(f"[ETag] Sleeping for 5 seconds to simulate slow response...")
                # time.sleep(5)  # Increased to 5 seconds to make it very noticeable
        
        return response
    return wrapped_view

class HelloWorldAPIView(APIView):
    """
    A simple API view that returns a hello world message
    """
    
    @etag_decorator
    def get(self, request, format=None):
        """
        Return a simple hello world message
        """
        content = {'message': 'Hello, World!'}
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
        
    @etag_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @etag_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

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
    
    @etag_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @etag_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @etag_decorator
    @action(detail=True, methods=['get'])
    def elements(self, request, pk=None):
        """Get all elements in this section"""
        section = self.get_object()
        elements = Element.objects.filter(section=section, user=request.user)
        serializer = ElementSerializer(elements, many=True)
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
    
    @etag_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @etag_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark an element as complete"""
        element = self.get_object()
        element.mark_as_complete()
        return Response({'status': 'Element marked as complete'})
    
    @action(detail=True, methods=['post'])
    def incomplete(self, request, pk=None):
        """Mark an element as incomplete"""
        element = self.get_object()
        element.mark_as_incomplete()
        return Response({'status': 'Element marked as incomplete'})
    
    @etag_decorator
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related elements"""
        element = self.get_object()
        relationship_type = request.query_params.get('type', None)
        related_elements = element.get_related_elements(relationship_type)
        serializer = ElementSerializer(related_elements, many=True)
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
            return Response({'status': 'Related element added'})
        except Element.DoesNotExist:
            return Response(
                {'error': 'Related element not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    # Add to ElementViewSet
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

    @etag_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @etag_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @etag_decorator
    @action(detail=True, methods=['get'])
    def next(self, request, pk=None):
        """Get the next flashcard after this one"""
        current = self.get_object()
        next_flashcard = Element.objects.filter(
            user=request.user,
            type=Element.FLASHCARD,
            id__gt=current.id
        ).order_by('id').first()
        
        if not next_flashcard:
            return Response({'detail': 'No next flashcard found'}, status=404)
        
        serializer = self.get_serializer(next_flashcard)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def previous(self, request, pk=None):
        """Get the previous flashcard before this one"""
        current = self.get_object()
        prev_flashcard = Element.objects.filter(
            user=request.user,
            type=Element.FLASHCARD,
            id__lt=current.id
        ).order_by('-id').first()
        
        if not prev_flashcard:
            return Response({'detail': 'No previous flashcard found'}, status=404)
        
        serializer = self.get_serializer(prev_flashcard)
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
        
    @etag_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @etag_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

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
        
    @etag_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @etag_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a todo as complete"""
        todo = self.get_object()
        todo.mark_as_complete()
        return Response({'status': 'Todo marked as complete'})
    
    @action(detail=True, methods=['post'])
    def incomplete(self, request, pk=None):
        """Mark a todo as incomplete"""
        todo = self.get_object()
        todo.mark_as_incomplete()
        return Response({'status': 'Todo marked as incomplete'})

    @etag_decorator
    @action(detail=False, methods=['get'])
    def by_section(self, request):
        """Get todos grouped by section"""
        section_id = request.query_params.get('id')
        if not section_id:
            return Response(
                {'error': 'Section ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all subsection IDs
        section_ids = [section_id]
        
        def get_subsection_ids(parent_id):
            subsection_ids = []
            subsections = Section.objects.filter(parent_id=parent_id, user=request.user)
            for sub in subsections:
                subsection_ids.append(sub.id)
                subsection_ids.extend(get_subsection_ids(sub.id))
            return subsection_ids
        
        section_ids.extend(get_subsection_ids(section_id))
        
        # Filter todos
        todos = Element.objects.filter(
            user=request.user,
            type=Element.TODO,
            section_id__in=section_ids
        )
        
        # Apply any other filters
        if 'is_completed' in request.query_params:
            is_completed = request.query_params.get('is_completed').lower() == 'true'
            todos = todos.filter(is_completed=is_completed)
        
        # Pagination
        page = self.paginate_queryset(todos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(todos, many=True)
        return Response(serializer.data)


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
        
    @etag_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @etag_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class StudySessionViewSet(viewsets.ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FlexiblePagination
    
    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user)
    
    @etag_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @etag_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a study session"""
        session = self.get_object()
        session.end_session()
        serializer = StudySessionSerializer(session)
        return Response(serializer.data)

    # Add to StudySessionViewSet
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

class StudyRecordViewSet(viewsets.ModelViewSet):
    serializer_class = StudyRecordSerializer
    pagination_class = FlexiblePagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['session', 'element', 'result']
    
    def get_queryset(self):
        # Make sure we filter by session__user to maintain proper access control
        return StudyRecord.objects.filter(session__user=self.request.user)
        
    @etag_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @etag_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @etag_decorator
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