import boto3
import json
import base64
import os

# Create a BedrockRuntime client
bedrock_runtime = boto3.client('bedrock-runtime')

def describe_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        base64_string = encoded_string.decode('utf-8')

    payload = {
        "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64_string
                            }
                        },
                        {
                            "type": "text",
                            "text": '''
你是一位专业的图像审核员,负责审核海报图像。你的任务是仔细查看图像,并根据以下标签体系,对图像中存在的任何与标签相关的内容进行标记和评分。

<image_review_categories>
  <category name="adult_content">
    <subcategory>nudity</subcategory>
    <!-- 0-无裸露;1-轻微裸露;2-部分裸露;3-中度裸露;4-大面积裸露;5-完全裸露 -->
    <subcategory>pornography</subcategory>
    <!-- 0-无色情内容;3-含有性暗示;5-露骨色情内容;7-极其露骨的色情内容 -->
    <subcategory>sexual_content</subcategory>
    <!-- 0-无性内容;2-轻微性暗示;4-明确的性行为;6-露骨的性行为 -->
    <subcategory>male_nudity</subcategory>
    <!-- 同nudity -->
    <subcategory>female_nudity</subcategory>
    <!-- 同nudity -->
    <subcategory>homosexual_content</subcategory>
    <!-- 0-无同性恋内容;2-轻微暗示;4-明确体现;6-露骨展现 -->
  </category>
  <category name="violence">
    <subcategory>graphic_violence</subcategory>
    <!-- 0-无暴力;2-轻微暴力;4-中度暴力场景;6-严重血腥暴力 -->
    <subcategory>blood</subcategory>
    <!-- 0-无血腥;2-轻微血腥;4-中度血腥;6-大量血腥 -->
    <subcategory>weapons</subcategory>
    <!-- 0-无武器;2-非致命武器;4-致命武器;6-大规模杀伤性武器 -->
  </category>
  <category name="hate_speech">
    <subcategory>racism</subcategory>
    <!-- 0-无种族歧视;3-轻微种族暗示;5-明确种族歧视;7-极端种族仇恨 -->
    <subcategory>discrimination</subcategory>
    <!-- 0-无歧视;2-轻微歧视;4-明确歧视;6-严重歧视 -->
    <subcategory>hate_symbols</subcategory>
    <!-- 0-无仇恨符号;4-含有一些仇恨符号;7-充斥仇恨符号 -->
  </category>
  <category name="illegal_activities">
    <subcategory>drugs</subcategory>
    <!-- 0-无毒品;3-轻微涉及毒品;5-明确涉及毒品;7-大量涉及毒品 -->
    <subcategory>illegal_products</subcategory>
    <!-- 0-无非法产品;3-轻微涉及;5-明确涉及;7-大量涉及 -->
    <subcategory>crime</subcategory>
    <!-- 0-无犯罪;2-轻微涉及犯罪;4-明确涉及犯罪;6-严重犯罪 -->
  </category>
  <category name="other_objectionable_content">
    <subcategory>spam</subcategory>
    <!-- 0-无垃圾广告;3-轻微涉及;5-明确涉及;7-大量垃圾广告 -->
    <subcategory>misleading_information</subcategory>
    <!-- 0-无误导信息;3-轻微误导;5-明确误导;7-严重误导 -->
    <subcategory>offensive_language</subcategory>
    <!-- 0-无令人反感的语言;2-轻微涉及;4-中度涉及;6-严重涉及 -->
    <subcategory>anti_christian_values</subcategory>
    <!-- 0-无反基督教内容;3-轻微涉及;5-明确涉及;7-大量涉及 -->
    <subcategory>anti_islamic_values</subcategory>
    <!-- 0-无反伊斯兰教内容;3-轻微涉及;5-明确涉及;7-大量涉及 -->
  </category>
</image_review_categories>

请仔细审核图像,并按照以下JSON格式输出你的评估结果，注意JSON不需要换行:

{
  "review_categories": [
    {
      "category": "<category_name>",
      "subcategories": [
        {
          "name": "<subcategory_name>",
          "score": <score>,
          "description": "<commons of review>",
        }
      ]
    }
  ]
}

其中:
- `review_categories`是一个数组,包含你评估过的所有类别
- 对于每个类别,`category`是类别名称,`subcategories`是一个数组,包含该类别下所有被标记的子类别,以及相应的分数`score`
- 不可以出现json以外的输出

请根据上述分级标准,专业地完成审核工作。如果图像未涉及任何相关内容,请回复一个简单的JSON，内容是"该图像未涉及任何相关内容"。

                            '''
                        }
                    ]
                }
            ],
            "system": "please response in Chinese",
            "temperature": 0.8
        }
    }

    # Convert the payload to bytes
    body_bytes = json.dumps(payload['body']).encode('utf-8')

    # Invoke the model
    response = bedrock_runtime.invoke_model(
        body=body_bytes,
        contentType=payload['contentType'],
        accept=payload['accept'],
        modelId=payload['modelId']
    )

    # Process the response
    response_body = response['body'].read().decode('utf-8')
    print(response_body)
    return json.loads(response_body)

# Specify the directory path
directory_path = "pics"

# Initialize an empty list to store the responses
responses = []

# Traverse all image files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".png") or filename.endswith(".jpg"):
        image_path = os.path.join(directory_path, filename)
        response = describe_image(image_path)
        response['filename'] = filename
        responses.append(response)


result = []
for response in responses:
    filename = response['filename']
    text = response['content'][0]['text']
    try:
        content = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for file {filename}: {e}")
        continue
    result.append({
        'filename': filename,
        'content': content
    })

# Save responses to a file
with open('moderate.json', 'w') as f:
    json.dump(result, f, indent=2)
