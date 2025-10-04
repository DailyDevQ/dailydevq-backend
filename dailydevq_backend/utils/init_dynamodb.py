"""
DynamoDB 테이블 초기화 스크립트
"""

import boto3
from dailydevq_backend.core.config import settings


def create_users_table():
    """Users 테이블 생성"""
    dynamodb = boto3.client(
        "dynamodb",
        endpoint_url=settings.DYNAMODB_ENDPOINT,
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    table_name = f"{settings.DYNAMODB_TABLE_PREFIX}-{settings.DYNAMODB_USERS_TABLE}"

    try:
        # 기존 테이블 확인
        existing_tables = dynamodb.list_tables()["TableNames"]
        if table_name in existing_tables:
            print(f"✅ 테이블이 이미 존재합니다: {table_name}")
            return

        # 테이블 생성
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "email-index",
                    "KeySchema": [
                        {"AttributeName": "email", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5,
                    },
                }
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5,
            },
        )

        print(f"✅ 테이블 생성 완료: {table_name}")
        print(f"   Status: {response['TableDescription']['TableStatus']}")

    except Exception as e:
        print(f"❌ 테이블 생성 실패: {str(e)}")
        raise


def init_all_tables():
    """모든 테이블 초기화"""
    print("🚀 DynamoDB 테이블 초기화 시작...")
    print(f"   Endpoint: {settings.DYNAMODB_ENDPOINT}")
    print(f"   Prefix: {settings.DYNAMODB_TABLE_PREFIX}")
    print()

    create_users_table()

    print()
    print("✨ 테이블 초기화 완료!")


if __name__ == "__main__":
    init_all_tables()
