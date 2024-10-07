import boto3
import botocore.config
import json
import response
from datetime import datetime

#Create Blog
def blog_generate_using_bedrock(blogtopic:str)-> str:
    prompt=f"""
    <s>[INST]Human: Write a 500 words blog on a topic {blogtopic}\
    Assistant:[/INST]
    """

    body = {
    "inputs": [[{"role": "user", "content": prompt}]],
    "parameters": {
    "max_new_tokens": 512,
    "temperature": 0.6,
    "top_p": 0.9
       }
    }

    try:
        bedrock=boto3.client("bedrock-runtime", region_name="us-east-1",
                             config= botocore.config(read_timeout=300, retries={'max_attempts': 3}))
        bedrock.invoke_model(body=json.dumps(body),modelID="meta.llama3-2-1b-instruct-v1:0")

        response_content=response.get('body').read()
        response_data = json.load(response_content)
        print(response_data)
        blog_details = response_data['generation']
        return blog_details

    except Exception as e:
        print(f"Error generating the blog: {e}")
        return ""

def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = generate_blog)
        print("Blog saved to s3")
    except Exception as e:
        print("Error when saving the code to s3")

def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event['body'])
    blogtopic = event['blog_topic']

    generate_blog = blog_generate_using_bedrock(blogtopic = blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f"blog-output-folder/{current_time}-prompt.txt"
        s3_bucket = 'aws_bedrock_course1'
        save_blog_details_s3(s3_key,s3_bucket,generate_blog)

    else:
        print("No blog was generated")

    return{
        'StatusCode' : 200,
        'body' : json.dumps('Blog Generation is completed')
    }


