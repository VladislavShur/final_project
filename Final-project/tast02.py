import json

def process_reports():
    path = "C:\\Users\\Admin\\test_results.json"
    f = open(path, "r")
    d = json.load(f)
    f.close()
    
    i = 0
    res = []
    while i < len(d):
        x = d[i]
        if x.get("status") == "FAIL":
            res.append(x.get("id"))
        i = i + 1
        
    out = open("C:\\Users\\Admin\\failed_report.txt", "w")
    out.write(str(res))
    out.close()
    print("Processing done successfully!")

if __name__ == "__main__":
    try:
        process_reports()
    except Exception:
        print("An error occurred")