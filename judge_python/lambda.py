import json
import judge

success_payload = {
    'statusCode': 200,
}

error_payload = {
    'statusCode': 409,
}


def lambda_handler(event, context):
    try:
        file_name = event['fileName']
        problem_id = event['problemId']

        if event['submit']:
            download_file_name = judge.download(file_name)

            if download_file_name != False:
                payload = judge.run_file(download_file_name, problem_id)
                if payload:
                    success_payload['body'] = json.dumps(payload)
                    return success_payload
                else:
                    error_payload['body'] = json.dumps('Error from lambda')
                    return error_payload
        else:
            code = event['code']
            create_file_name = judge.create_file(file_name, code)
            if create_file_name != False:
                payload = judge.run_file(create_file_name, problem_id)
                if payload:
                    success_payload['body'] = json.dumps(payload)
                    return success_payload
                else:
                    error_payload['body'] = json.dumps('Error from lambda')
                    return error_payload
    except Exception as e:
        error_payload['body'] = json.dumps(e)
        return error_payload
