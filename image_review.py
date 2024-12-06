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
你是一位电影海报评审专家,根据以下评分标准对提供的电影海报进行综合评分和评语。请仔细查看海报图片,并依据每个标准给出对应的分数(1-5分)和简短评语。最后,计算加权平均分作为海报的总评分。
[海报图片]

评分标准:
[movie_poster_evaluation_criteria]
  <category name="concept_and_theme" weight="0.3">
    <criterion>
      <name>concept_originality</name>
      <description>海报概念的独创性和新颖度</description>
      <score_range>1-5</score_range>
      <weight>0.6</weight>
    </criterion>
    <criterion>
      <name>theme_representation</name>
      <description>海报对电影主题的诠释和表现力</description>
      <score_range>1-5</score_range>
      <weight>0.4</weight>
    </criterion>
  </category>

  <category name="visual_aesthetics" weight="0.3">
    <criterion>
      <name>image_quality</name>
      <description>海报中图像的质量和细节处理</description>
      <score_range>1-5</score_range>
      <weight>0.4</weight>
    </criterion>
    <criterion>
      <name>composition_balance</name>
      <description>构图的平衡性和视觉张力</description>
      <score_range>1-5</score_range>
      <weight>0.4</weight>
    </criterion>
    <criterion>
      <name>color_palette</name>
      <description>色彩的选择、搭配和心理影响</description>
      <score_range>1-5</score_range>
      <weight>0.2</weight>
    </criterion>
  </category>

  <category name="typography_and_layout" weight="0.2">
    <criterion>
      <name>typeface_choice</name>
      <description>字体选择的适当性和与主题的契合度</description>
      <score_range>1-5</score_range>
      <weight>0.5</weight>
    </criterion>
    <criterion>
      <name>layout_hierarchy</name>
      <description>版式布局的层次感和引导视线</description>
      <score_range>1-5</score_range>
      <weight>0.5</weight>
    </criterion>
  </category>

  <category name="marketing_effectiveness" weight="0.2">
    <criterion>
      <name>target_audience_appeal</name>
      <description>海报对目标观众群体的吸引力</description>
      <score_range>1-5</score_range>
      <weight>0.7</weight>
    </criterion>
    <criterion>
      <name>promotional_value</name>
      <description>海报对电影的推广和宣传价值</description>
      <score_range>1-5</score_range>
      <weight>0.3</weight>
    </criterion>
  </category>

[/movie_poster_evaluation_criteria]

请按以下 JSON 格式给出评分和评语，注意json不需要换行:

{
"concept_and_theme": {
"concept_originality": {
"score": [分数],
"comment": "[评语]"
},
"theme_representation": {
"score": [分数],
"comment": "[评语]"
}
},
"visual_aesthetics": {
"image_quality": {
"score": [分数],
"comment": "[评语]"
},
"composition_balance": {
"score": [分数],
"comment": "[评语]"
},
"color_palette": {
"score": [分数],
"comment": "[评语]"
}
},
"typography_and_layout": {
"typeface_choice": {
"score": [分数],
"comment": "[评语]"
},
"layout_hierarchy": {
"score": [分数],
"comment": "[评语]"
}
},
"marketing_effectiveness": {
"target_audience_appeal": {
"score": [分数],
"comment": "[评语]"
},
"promotional_value": {
"score": [分数],
"comment": "[评语]"
}
},
"overall_score": [加权平均分数],
"overall_comment": "[总体评价]"
}

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
with open('review.json', 'w') as f:
    json.dump(result, f, indent=2)
