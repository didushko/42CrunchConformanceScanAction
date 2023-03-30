import json


def read_audited_ids_from_report(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)



        files = data["audit"]["report"]
        result=[]


        for key, value in files.items():
            if value["audited"]:
                result.append(value["apiId"])
            else:
                print("Skip false audited file {}".format(key))
        return result
    except Exception as e:
        print(f"Error uploading audit report: {e}")