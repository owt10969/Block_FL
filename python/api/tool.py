import os
import shutil

def copy_files_to_same_folder(folder_path):
    """
    將 folder_path 及其子資料夾中的所有檔案，
    複製到 folder_path 下新建的 all_files_copied 資料夾內。
    若有同名檔案，則會自動加上序號以避免覆蓋。
    """
    # 建立儲存全部檔案的目標資料夾
    new_folder = os.path.join(folder_path, "all_files_copied")
    os.makedirs(new_folder, exist_ok=True)

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # 若檔案已經在 new_folder (避免把複製後的檔案再重複複製一次)
            if root == new_folder:
                continue

            source_path = os.path.join(root, filename)
            destination_path = os.path.join(new_folder, filename)

            # 若目標檔案已存在，則在檔名後面加上序號以避免覆蓋
            if os.path.exists(destination_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while True:
                    new_filename = f"{base}_{counter}{ext}"
                    new_destination_path = os.path.join(new_folder, new_filename)
                    if not os.path.exists(new_destination_path):
                        destination_path = new_destination_path
                        break
                    counter += 1

            # 執行複製
            shutil.copy2(source_path, destination_path)

if __name__ == "__main__":
    # 替換成你要執行的路徑
    folder_path = r"H:/Workspace/Go-FederatedLearning"
    copy_files_to_same_folder(folder_path)
    print("檔案已全部複製到 all_files_copied 資料夾內。")
