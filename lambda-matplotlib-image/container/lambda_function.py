import json
import boto3
import matplotlib.pyplot as plt

def lambda_handler(event, context):
    metrics_bucket = 'default'
    metrics_filename = 'default'
    model_name = 'default'

    if 'metrics_bucket' in event:
        metrics_bucket = event['metrics_bucket']
        
    if 'metrics_filename' in event:
        metrics_filename = event['metrics_filename']

    if 'model_name' in event:
        model_name = event['model_name']
        
    s3_client = boto3.client('s3')
    s3_client.download_file(metrics_bucket, metrics_filename, '/tmp/metrics.json')
    
    with open('/tmp/metrics.json') as f:
        data = json.load(f)
    
    phase_list = data['metrics']
    metrics_list = ['box', 'obj', 'cls']

    train_list = {i: [] for i in metrics_list}
    valid_list = {i: [] for i in metrics_list}

    for i in phase_list:
        if i['phase'] == 'train':
            for metric in metrics_list:
                train_list[metric].append(i[metric])
        else:
            for metric in metrics_list:
                valid_list[metric].append(i[metric])
    
    filename_list = []

    for metric in metrics_list:
        plt.plot(range(len(train_list[metric])), train_list[metric])
        # naming the x axis
        plt.xlabel('time')
        # naming the y axis
        plt.ylabel('loss')
        # giving a title to my graph
        plt.title(metric)

        plt.savefig(f'/tmp/train_{metric}.png')
        plt.close()
        filename_list.append(f'train_{metric}.png')

        plt.plot(range(len(valid_list[metric])), valid_list[metric])
        # naming the x axis
        plt.xlabel('time')
        # naming the y axis
        plt.ylabel('loss')
        # giving a title to my graph
        plt.title(metric)

        plt.savefig(f'/tmp/valid_{metric}.png')
        plt.close()
        filename_list.append(f'valid_{metric}.png')

    for i in range(len(filename_list)):
        s3_client.upload_file(f'/tmp/{filename_list[i]}', metrics_bucket, f'{model_name}/{filename_list[i]}')
        filename_list[i] = f'{model_name}/{filename_list[i]}'
    
    event['filename'] = filename_list
    
    return event
