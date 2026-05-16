import json
import os

def clean_creds():
    creds_path = "credentials.json"
    if not os.path.exists(creds_path):
        return
        
    with open(creds_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    pk = data["private_key"]
    # Thay thế các kiểu xuống dòng khác nhau về chuẩn \n
    pk = pk.replace("\\n", "\n").replace("\r\n", "\n").replace("\r", "\n")
    
    # Đảm bảo không có khoảng trắng thừa ở đầu/cuối
    pk = pk.strip()
    
    data["private_key"] = pk
    
    with open("credentials_cleaned.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Created credentials_cleaned.json")

if __name__ == "__main__":
    clean_creds()
