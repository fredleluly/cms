"""
Django management command untuk membuat Maven Course Pages secara otomatis
Jalankan: python manage.py create_maven_courses
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.pages.models import Page, ContentBlock


class Command(BaseCommand):
    help = 'Automatically create Maven course pages with default content blocks'

    def handle(self, *args, **options):
        """Create 3 Maven courses if they don't exist"""
        
        courses_data = [
            {
                'title': 'Maven Fundamentals_course',
                'slug': 'maven-fundamentals',
                'level': 'Beginner',
                'price': 'Rp 1.700.000',
                'price_original': 'Rp 2.500.000',
                'duration': '8 Weeks',
                'description': 'Learn the basics of Maven including project setup, dependencies, build lifecycle, and plugins. Perfect for beginners who want to master build automation fundamentals.',
                'image_url': 'https://source.unsplash.com/featured/?coding'
            },
            {
                'title': 'Maven Advanced_course',
                'slug': 'maven-advanced',
                'level': 'Advanced',
                'price': 'Rp 2.800.000',
                'price_original': 'Rp 3.500.000',
                'duration': '10 Weeks',
                'description': 'Master advanced Maven concepts including custom plugins, multi-module projects, and CI/CD integration. Take your Maven skills to the next level.',
                'image_url': 'https://source.unsplash.com/featured/?technology'
            },
            {
                'title': 'Maven Enterprise_course',
                'slug': 'maven-enterprise',
                'level': 'Enterprise',
                'price': 'Rp 4.200.000',
                'price_original': 'Rp 5.000.000',
                'duration': '12 Weeks',
                'description': 'Enterprise-grade Maven solutions including repository management, security, and scalability. Designed for large-scale enterprise deployments.',
                'image_url': 'https://source.unsplash.com/featured/?business'
            }
        ]

        created_count = 0
        updated_count = 0

        for course in courses_data:
            try:
                # Check if course already exists
                page, created = Page.objects.get_or_create(
                    slug=course['slug'],
                    defaults={
                        'title': course['title'],
                        'template': 'maven_course_detail.html',
                        'status': Page.PUBLISHED,
                        'metadata': {
                            'meta_description': f"{course['level']} Maven course at Matana University",
                            'meta_keywords': f"Maven, {course['level']}, Training, Course"
                        }
                    }
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created: {course["title"]}')
                    )
                    created_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Already exists: {course["title"]}')
                    )
                    updated_count += 1

                # Create or update content blocks
                self._create_content_blocks(page, course)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creating {course["title"]}: {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(
            f'✅ Created: {created_count} new courses'
        ))
        self.stdout.write(self.style.WARNING(
            f'⚠️  Already existed: {updated_count} courses'
        ))
        self.stdout.write(self.style.SUCCESS(
            '✅ Maven courses setup complete!\n'
        ))

    def _create_content_blocks(self, page, course_data):
        """Create comprehensive content blocks for a course page"""
        
        blocks_to_create = [
            # Hero Section - Title + Description + Duration
            {
                'identifier': 'hero_section',
                'order': 1,
                'content_type': 'rich_text',
                'content': {
                    'title': course_data['title'].replace('_course', ''),
                    'subtitle': 'Master the fundamentals and advanced concepts through hands-on learning',
                    'background_image': course_data['image_url'],
                    'items': [
                        {
                            'title': 'Level',
                            'description': course_data['level']
                        },
                        {
                            'title': 'Duration',
                            'description': course_data['duration']
                        },
                        {
                            'title': 'Price',
                            'description': course_data['price']
                        }
                    ]
                }
            },
            # Course Overview - Description
            {
                'identifier': 'course_overview',
                'order': 2,
                'content_type': 'rich_text',
                'content': {
                    'title': 'Course Description',
                    'description': course_data['description'],
                    'items': []
                }
            },
            # Course Features/Benefits
            {
                'identifier': 'course_features',
                'order': 3,
                'content_type': 'rich_text',
                'content': {
                    'title': 'What You\'ll Learn',
                    'subtitle': 'Comprehensive learning experience with hands-on projects',
                    'items': [
                        {
                            'title': 'Video Content',
                            'description': '20 hours on-demand video'
                        },
                        {
                            'title': 'Resources',
                            'description': '15 downloadable resources'
                        },
                        {
                            'title': 'Lifetime Access',
                            'description': 'Full lifetime access'
                        },
                        {
                            'title': 'Multi-Device',
                            'description': 'Access on mobile and desktop'
                        },
                        {
                            'title': 'Certificate',
                            'description': 'Certificate of completion'
                        }
                    ]
                }
            },
            # Pricing Section
            {
                'identifier': 'pricing_section',
                'order': 4,
                'content_type': 'rich_text',
                'content': {
                    'title': 'Investment in Your Future',
                    'items': [
                        {
                            'title': 'Original Price',
                            'description': course_data['price_original']
                        },
                        {
                            'title': 'Current Price',
                            'description': course_data['price']
                        },
                        {
                            'title': 'Savings',
                            'description': 'Limited time offer - Register now!'
                        }
                    ]
                }
            },
            # Instructor Section
            {
                'identifier': 'instructor_section',
                'order': 5,
                'content_type': 'rich_text',
                'content': {
                    'title': 'Meet Your Instructor',
                    'items': [
                        {
                            'title': 'Michelle E. Lapian, S.Sn., MM., M.Ds.',
                            'description': 'Visual Communication Design practitioner and instructor with over five years of experience. A graduate of Binus University and Trisakti University, specialized in graphic design, branding, typography, and visual communication strategy.',
                            'image': 'https://source.unsplash.com/featured/?instructor,professional'
                        }
                    ]
                }
            },
            # Instructor Stats
            {
                'identifier': 'instructor_stats',
                'order': 6,
                'content_type': 'rich_text',
                'content': {
                    'title': 'Why Learn From Us',
                    'items': [
                        {
                            'title': '4.9',
                            'description': 'Instructor Rating'
                        },
                        {
                            'title': '1,200+',
                            'description': 'Students'
                        },
                        {
                            'title': '15',
                            'description': 'Courses'
                        }
                    ]
                }
            },
            # Course Level (for API)
            {
                'identifier': 'course_level',
                'order': 7,
                'content_type': 'text',
                'content': course_data['level']
            },
            # Course Price (for API)
            {
                'identifier': 'course_price',
                'order': 8,
                'content_type': 'text',
                'content': course_data['price']
            },
            # Course Price Original (for API)
            {
                'identifier': 'course_price_original',
                'order': 9,
                'content_type': 'text',
                'content': course_data['price_original']
            },
            # Course Duration (for API)
            {
                'identifier': 'course_duration',
                'order': 10,
                'content_type': 'text',
                'content': course_data['duration']
            },
            # Course Description (for API)
            {
                'identifier': 'course_description',
                'order': 11,
                'content_type': 'text',
                'content': course_data['description']
            },
            # Course Image URL (for API)
            {
                'identifier': 'course_image_url',
                'order': 12,
                'content_type': 'text',
                'content': course_data['image_url']
            }
        ]

        for block_data in blocks_to_create:
            try:
                # Get or create block - only pass valid model fields
                block, created = ContentBlock.objects.get_or_create(
                    page=page,
                    identifier=block_data['identifier'],
                    defaults={
                        'content': block_data.get('content', ''),
                        'order': block_data['order'],
                        'content_type': block_data.get('content_type', 'rich_text')
                    }
                )

                # If block exists, update content
                if not created:
                    block.content = block_data.get('content', '')
                    block.order = block_data['order']
                    block.content_type = block_data.get('content_type', 'rich_text')
                    block.save()

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creating block {block_data["identifier"]}: {str(e)}')
                )

        return True
