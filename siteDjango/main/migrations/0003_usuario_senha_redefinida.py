from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_rename_data_criacao_anexo_datacriacao_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='senha_redefinida',
            field=models.BooleanField(default=False),
        ),
    ]
