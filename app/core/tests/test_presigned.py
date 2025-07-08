import unittest
import boto3
from moto import mock_s3
from ..helper import generate_presigned_urls


class TestGeneratePresignedUrls(unittest.TestCase):

    @mock_s3
    def setUp(self):
        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.bucket_name = 'test-bucket'
        self.s3.create_bucket(Bucket=self.bucket_name)

        # Populate the bucket with test objects
        self.object_names = [1, 2, 3]
        for obj_name in self.object_names:
            self.s3.put_object(Bucket=self.bucket_name, Key=f'image_{obj_name}.png', Body=b'content')

    @mock_s3
    def test_generate_presigned_urls(self):
        result = generate_presigned_urls(self.bucket_name, self.object_names)

        self.assertEqual(len(result), len(self.object_names))
        for url in result:
            self.assertIn('https://', url)
            self.assertIn(self.bucket_name, url)


if __name__ == '__main__':
    unittest.main()
