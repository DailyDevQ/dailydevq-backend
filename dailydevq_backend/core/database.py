"""
DynamoDB 클라이언트 설정
"""

import boto3
from typing import Optional
from dailydevq_backend.core.config import settings


class DynamoDBClient:
    """DynamoDB 클라이언트 싱글톤"""

    _instance: Optional["DynamoDBClient"] = None
    _dynamodb = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._dynamodb is None:
            self._initialize_client()

    def _initialize_client(self):
        """DynamoDB 클라이언트 초기화"""
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

        # DynamoDB Resource (고수준 API)
        self._dynamodb = session.resource(
            "dynamodb",
            endpoint_url=settings.DYNAMODB_ENDPOINT,
        )

        # DynamoDB Client (저수준 API)
        self._client = session.client(
            "dynamodb",
            endpoint_url=settings.DYNAMODB_ENDPOINT,
        )

    @property
    def dynamodb(self):
        """DynamoDB Resource 반환"""
        if self._dynamodb is None:
            self._initialize_client()
        return self._dynamodb

    @property
    def client(self):
        """DynamoDB Client 반환"""
        if self._client is None:
            self._initialize_client()
        return self._client

    def get_table(self, table_name: str):
        """DynamoDB 테이블 반환"""
        full_table_name = f"{settings.DYNAMODB_TABLE_PREFIX}-{table_name}"
        return self.dynamodb.Table(full_table_name)


# 싱글톤 인스턴스
dynamodb_client = DynamoDBClient()
