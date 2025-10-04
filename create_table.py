#!/usr/bin/env python3
import boto3

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='ap-northeast-2',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

table_name = 'dailydevq-dev-users'

try:
    # 기존 테이블 확인
    existing_tables = dynamodb.list_tables()['TableNames']

    if table_name in existing_tables:
        print(f'✅ 테이블이 이미 존재합니다: {table_name}')
    else:
        # 테이블 생성
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'email-index',
                    'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        print(f'✅ 테이블 생성 완료: {table_name}')
        print(f'   Status: {response["TableDescription"]["TableStatus"]}')

except Exception as e:
    print(f'❌ 오류: {str(e)}')
