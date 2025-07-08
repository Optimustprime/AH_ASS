import logging
import os
import random

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.db.models import Count

bucket = 'oladayotha'
access_key = os.environ.get('ACCESS_KEY')
secret_key = os.environ.get('AWS_SECRET_KEY')
env = os.environ.get('ENV')


def business_requirements(campaign_id, click_collection, conversion_collection):
    """
    Processes and retrieves the top performing banners for a given campaign based on revenue and clicks.

    Args:
        campaign_id (int): The ID of the campaign for which banners are to be selected.
        click_collection (QuerySet): Django QuerySet for accessing click data.
        conversion_collection (QuerySet): Django QuerySet for accessing conversion data.

    Returns:
        list: A list of presigned URLs for the top performing banners.

    This function implements the following business logic:
    - If there are 10 or more banners with conversions,
    show the top 10 banners based on revenue.
    - If there are between 5 and 9 banners with conversions,
    show all banners based on revenue.
    - If there are between 1 and 4 banners with conversions, show the top banners
    based on revenue, and add banners with the most clicks to make up a collection of 5 unique banners.
    - If there
    are no banners with conversions, show the top 5 banners based on clicks. If the number of banners with clicks is
    less than 5, add random banners to make up a collection of 5 unique banners.
    """
    distinct_click_ids = click_collection.objects.filter(campaign_id=campaign_id).values('click_id', 'banner_id',
                                                                                         'campaign_id').distinct()
    click_ids = [click['click_id'] for click in distinct_click_ids]
    distinct_revenues = conversion_collection.objects.filter(click_id__in=click_ids).values('conversion_id', 'click_id',
                                                                                            'revenue').distinct()
    top_banner_ids = None
    revenues = list(distinct_revenues)
    sorted_click_ids = sorted(revenues, key=lambda x: x['revenue'], reverse=True)
    if len(revenues) == 10 or len(revenues) > 10:
        top_banner_ids = first_business_case(sorted_click_ids=sorted_click_ids, click_collection=click_collection)

    elif 4 < len(revenues) < 10:
        top_banner_ids = second_business_case(sorted_click_ids=sorted_click_ids, click_collection=click_collection)

    elif 0 < len(revenues) < 5:
        top_banner_ids = third_business_case(sorted_click_ids=sorted_click_ids, click_collection=click_collection,distinct_click_ids=distinct_click_ids)
    elif len(revenues) == 0:
        top_banner_ids = forth_business_case(distinct_click_ids)
    urls = generate_presigned_urls(bucket, top_banner_ids)
    return urls


def first_business_case(sorted_click_ids, click_collection) -> list:
    top_click_ids = [click['click_id'] for click in sorted_click_ids[:10]]
    distinct_banner_ids = click_collection.objects.filter(click_id__in=top_click_ids).values('click_id', 'banner_id',
                                                                                             'campaign_id').distinct()
    top_banner_ids_list = [banner['banner_id'] for banner in distinct_banner_ids]

    return top_banner_ids_list


def second_business_case(sorted_click_ids, click_collection) -> list:
    all_click_ids = [click['click_id'] for click in sorted_click_ids]
    distinct_banner_ids = click_collection.objects.filter(click_id__in=all_click_ids).values('click_id',
                                                                                             'banner_id',
                                                                                             'campaign_id').distinct()
    top_banner_ids_list = [banner['banner_id'] for banner in distinct_banner_ids]

    return top_banner_ids_list


def third_business_case(sorted_click_ids, click_collection, distinct_click_ids) -> list:
    all_click_ids = [click['click_id'] for click in sorted_click_ids]
    distinct_banner_ids = click_collection.objects.filter(click_id__in=all_click_ids).values('click_id',
                                                                                             'banner_id',
                                                                                             'campaign_id').distinct()
    top_banner_ids = [banner['banner_id'] for banner in distinct_banner_ids]
    unique_banner_list = []
    for item in top_banner_ids:
        if item not in unique_banner_list:
            unique_banner_list.append(item)
    added_banners = 5 - len(unique_banner_list)
    banner_clicks = distinct_click_ids.values('banner_id').annotate(click_count=Count('click_id')).order_by(
        '-click_count')
    top_click_banner_ids_list = [banner['banner_id'] for banner in banner_clicks]
    for item in unique_banner_list:
        if item in top_click_banner_ids_list:
            top_click_banner_ids_list.remove(item)
    top_click_banner_ids = top_click_banner_ids_list[:added_banners]
    top_banner_ids = unique_banner_list + top_click_banner_ids
    return top_banner_ids


def forth_business_case(distinct_click_ids) -> list:
    banner_clicks = distinct_click_ids.values('banner_id').annotate(click_count=Count('click_id')).order_by(
        '-click_count')
    top_click_banner_ids_list = [banner['banner_id'] for banner in banner_clicks]
    unique_banner_list = []
    for item in top_click_banner_ids_list:
        if item not in unique_banner_list:
            unique_banner_list.append(item)
    if len(unique_banner_list) < 5:
        banner_all_ids = [click['banner_id'] for click in distinct_click_ids]
        for item in unique_banner_list:
            if item in banner_all_ids:
                banner_all_ids.remove(item)
        top_banner_ids = unique_banner_list + random.sample(banner_all_ids
                                                            , 5 - len(unique_banner_list))
    else:
        top_banner_ids = unique_banner_list[:5]
    return top_banner_ids


def generate_presigned_urls(bucket_name, object_names, expiration=3600):
    """
    Generate presigned URLs for the given S3 objects.

    :param bucket_name: The name of the S3 bucket
    :param object_names: A list of object names in the S3 bucket
    :param access_key: AWS access key
    :param secret_key: AWS secret key
    :param expiration: Time in seconds for the presigned URL to remain valid (default: 3600)
    :return: A list of presigned URLs
    """
    if env == 'local':
        s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    else:
        s3_client = boto3.client('s3')
    presigned_urls = []
    image_names = ["image_{}.png".format(num) for num in object_names]
    try:
        for object_name in image_names:
            object_name_str = str(object_name)
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_name_str},
                ExpiresIn=expiration
            )
            presigned_urls.append(presigned_url)

    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error("Error with AWS credentials: %s", e)
        return None
    except Exception as e:
        logging.error("Error generating presigned URLs: %s", e)
        return None

    return presigned_urls


def randomize_list(lst) -> list:
    """
   Shuffle a list and ensure no consecutive items are the same.

   This function shuffles the input list and then iterates through it to prevent
   any consecutive items from being the same. If consecutive items are the same,
   it swaps the current item with a random item from the remaining list.

   Args:
       lst (list): The list to be randomized.

   Returns:
       list: The shuffled list with no consecutive items being the same.
   """
    random.shuffle(lst)

    for i in range(len(lst) - 1):
        if lst[i] == lst[i + 1]:
            j = i + 2
            while j < len(lst) and lst[i] == lst[j]:
                j += 1
            if j < len(lst):
                lst[i + 1], lst[j] = lst[j], lst[i + 1]
            else:
                break

    return lst
