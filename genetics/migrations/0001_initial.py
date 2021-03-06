# Generated by Django 4.0.4 on 2022-05-03 07:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HgncGene',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hgnc_id', models.CharField(db_index=True, max_length=50)),
                ('approved_symbol', models.CharField(db_index=True, max_length=100)),
                ('alias_symbols', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('approved_name', models.CharField(max_length=250)),
                ('alias_names', models.CharField(blank=True, max_length=250, null=True)),
                ('chromosome_location', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ('orphanet_id', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ('mim_number', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OmimGene',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mim_number', models.CharField(db_index=True, max_length=50)),
                ('gene_symbols', models.CharField(db_index=True, max_length=100)),
                ('chromosome_location', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OmimTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ('preferred', models.TextField()),
                ('alternative', models.TextField()),
                ('omim_gene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genetics.omimgene')),
            ],
        ),
        migrations.CreateModel(
            name='OmimPhenotype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phenotype', models.CharField(max_length=250)),
                ('omim_gene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phenotypes', to='genetics.omimgene')),
            ],
        ),
    ]
