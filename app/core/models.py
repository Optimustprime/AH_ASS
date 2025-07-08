from django.db import models


class click_1(models.Model):
    click_id = models.IntegerField()
    banner_id = models.IntegerField()
    campaign_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_click_1'


class click_2(models.Model):
    click_id = models.IntegerField()
    banner_id = models.IntegerField()
    campaign_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_click_2'


class click_3(models.Model):
    click_id = models.IntegerField()
    banner_id = models.IntegerField()
    campaign_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_click_3'


class click_4(models.Model):
    click_id = models.IntegerField()
    banner_id = models.IntegerField()
    campaign_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_click_4'


class conversions_1(models.Model):
    conversion_id = models.IntegerField()
    click_id = models.IntegerField()
    revenue = models.TextField()

    class Meta:
        managed = False
        db_table = 'core_conversions_1'


class conversions_2(models.Model):
    conversion_id = models.IntegerField()
    click_id = models.IntegerField()
    revenue = models.TextField()

    class Meta:
        managed = False
        db_table = 'core_conversions_2'


class conversions_3(models.Model):
    conversion_id = models.IntegerField()
    click_id = models.IntegerField()
    revenue = models.TextField()

    class Meta:
        managed = False
        db_table = 'core_conversions_3'


class conversions_4(models.Model):
    conversion_id = models.IntegerField()
    click_id = models.IntegerField()
    revenue = models.TextField()

    class Meta:
        managed = False
        db_table = 'core_conversions_4'


class impressions_1(models.Model):
    banner_id = models.IntegerField()
    campaign_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_impressions_1'


class impressions_2(models.Model):
    banner_id = models.IntegerField()
    campaign_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_impressions_2'


class impressions_3(models.Model):
    banner_id = models.IntegerField()
    campaign_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_impressions_3'


class impressions_4(models.Model):
    banner_id = models.IntegerField()
    campaign_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_impressions_4'
