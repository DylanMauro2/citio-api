from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('condominio_gestion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mantencionprogramada',
            name='mantencion_programada_descripcion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
