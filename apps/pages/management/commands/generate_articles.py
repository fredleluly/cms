from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.pages.models import Article, ArticleCategory
from django.utils.text import slugify
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generates sample academic articles with relevant content'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of articles to generate')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        
        # Buat atau dapatkan kategori
        categories_data = ['Akademik', 'Beasiswa', 'Prestasi', 'Event', 'Penelitian']
        categories = []
        for cat_name in categories_data:
            category, created = ArticleCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    'slug': slugify(cat_name),
                    'description': f'Kategori untuk artikel {cat_name.lower()}'
                }
            )
            categories.append(category)
        
        academic_titles = [
            "Matana University Menjalin Kerjasama dengan Industri Teknologi Terkemuka",
            "Program Beasiswa Unggulan Matana University 2024",
            "Prestasi Mahasiswa Matana di Kompetisi Nasional",
            "Seminar Internasional: Teknologi dan Bisnis di Era Digital",
            "Workshop Kewirausahaan: Dari Kampus Menuju Startup",
            "Matana University Membuka Program Studi Baru",
            "Kunjungan Industri: Mahasiswa Matana di Silicon Valley",
            "Penelitian Terbaru: Inovasi Teknologi Kampus",
            "Career Fair 2024: Peluang Karir Lulusan Matana",
            "Kuliah Umum: Transformasi Digital dalam Pendidikan",
        ]

        excerpts = [
            "Pengembangan kerjasama strategis untuk meningkatkan kualitas pendidikan dan peluang karir mahasiswa.",
            "Program beasiswa unggulan untuk mahasiswa berprestasi dengan berbagai fasilitas pendukung.",
            "Mahasiswa Matana meraih prestasi gemilang dalam kompetisi tingkat nasional.",
            "Menghadirkan pembicara internasional dalam seminar teknologi dan bisnis.",
            "Pelatihan intensif kewirausahaan untuk mahasiswa dengan mentor berpengalaman.",
            "Pembukaan program studi baru yang sesuai dengan kebutuhan industri.",
            "Program kunjungan industri ke perusahaan teknologi global.",
            "Hasil penelitian terbaru dalam pengembangan teknologi kampus.",
            "Membuka peluang karir dengan perusahaan mitra terkemuka.",
            "Kuliah umum dengan topik terkini tentang transformasi digital.",
        ]

        content_template = """
        {excerpt}

        Program ini merupakan bagian dari komitmen Matana University dalam:
        
        1. Meningkatkan kualitas pendidikan
        2. Mengembangkan kompetensi mahasiswa
        3. Memperkuat kerjasama dengan industri
        4. Mendukung inovasi dan penelitian
        
        Untuk informasi lebih lanjut, mahasiswa dapat menghubungi:
        - Email: info@matanauniversity.ac.id
        - Telepon: (021) XXX-XXXX
        - Website: www.matanauniversity.ac.id
        """
        
        for i in range(count):
            title = random.choice(academic_titles)
            excerpt = random.choice(excerpts)
            
            # Create article with relevant content
            article = Article.objects.create(
                title=title,
                slug=slugify(title),
                excerpt=excerpt,
                content=content_template.format(excerpt=excerpt),
                status='published',
                category=random.choice(categories),
                created_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                featured_image='articles/default-article-image.jpg'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created article: "{title}"')
            )
