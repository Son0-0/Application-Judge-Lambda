import boto3
import os
import subprocess
import json

BUCKET = os.environ['s3Bucket']
ID = os.environ['s3Id']
SECRET = os.environ['s3Secret']

s3 = boto3.client(
    's3',
    aws_access_key_id=ID,
    aws_secret_access_key=SECRET,
)

input_file = open('input.json', 'r')
input = json.load(input_file)

output_file = open('output.json', 'r')
output = json.load(output_file)

def download(file_name):
    try:
        local_file_name = '/tmp/' + file_name
        s3.download_file(BUCKET, file_name, local_file_name)
        print('local_file_name: ', local_file_name)
        return local_file_name
    except:
        return False


def create_file(file_name, code):
    try:
        local_file_name = '/tmp/' + file_name
        f = open(local_file_name, 'w')
        f.write(code)
        f.close()
        return local_file_name
    except:
        return False


def run_file(file_name, problem_id):

    msg = []
    result = []
    passRate = 0

    try:
        for idx in range(len(input[problem_id])):
            limit_size = len(output[problem_id][idx])

            try:
                child = subprocess.run([f'python3 {file_name} | head -c {limit_size * 2}'], text=True,
                                       input=input[problem_id][idx], capture_output=True, shell=True, timeout=3)

                if (child.stderr):
                    err_msg = child.stderr.split('\n')
                    result.append(False)
                    if 'Broken pipe' in err_msg[3]:
                        msg.append('출력초과')
                    else:
                        msg.append(err_msg[3])
                else:
                    if child.stdout.rstrip() == output[problem_id][idx].rstrip():
                        result.append(True)
                        msg.append(child.stdout.rstrip())
                    else:
                        result.append(False)
                        msg.append(child.stdout.rstrip())
            except Exception as e:
                result.append(False)
                msg.append('시간초과')
                continue

        passRate = int(sum(result) / len(result) * 100)

        payload = {
            'results': result,
            'msg': msg,
            'passRate': passRate
        }

        return payload
    except Exception as e:
        print('Exception: ', e)
        return False
