import os
import shutil
import yaml

def move_files(file_names):
    move('train', file_names[:24])
    move('val', file_names[24:])

def move(folder, file_names):
    for file_name in file_names:
        source_path1 = os.path.join('data', 'images', file_name + '.jpg')
        source_path2 = os.path.join('data', 'labels', file_name + '.txt')
        destination_path1 = os.path.join('data', 'data', 'images', folder, file_name + '.jpg')
        destination_path2 = os.path.join('data', 'data', 'labels', folder, file_name + '.txt')

        # Di chuyển file
        try:
            shutil.move(source_path1, destination_path1)
            shutil.move(source_path2, destination_path2)
        except Exception as e:
            print(f"Lỗi khi di chuyển '{file_name}': {str(e)}")

def write_config(df):
    data = {
        'path': 'C:\\Users\\baam0\\OneDrive\\Documents\\MLproject\\yolov8\\data\\data',
        'train': 'images/train',  # train images (relative to 'path')
        'val': 'images/val',
        'names': df.set_index('ID')['MSSV'].to_dict()
    }

    with open('data.yaml', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)