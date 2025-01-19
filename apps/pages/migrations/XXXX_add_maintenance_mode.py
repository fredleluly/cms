from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),  # Make sure this matches your last migration
    ]

    operations = [
        migrations.CreateModel(
            name='MaintenanceMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('message', models.TextField(default="We're currently performing maintenance. Please check back soon.", help_text='Message to display during maintenance')),
                ('allowed_ips', models.TextField(blank=True, help_text='Comma-separated list of IPs that can access the site during maintenance')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Maintenance Mode',
                'verbose_name_plural': 'Maintenance Mode',
            },
        ),
    ] 