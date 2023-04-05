import json


def read_audited_ids_from_report(path):
        files = read_report(path)
        result = {}
        for key, value in files.items():
            if value["audited"]:
                result[key] = (value["apiId"])
            else:
                print(f"Skip false audited file {key}")
        return result

def read_report(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)

        files = data["audit"]["report"]
        return files
    except Exception as e:
        print(f"Error uploading audit report \"{path}\" : {e}")