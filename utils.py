
# Kill the broken files
import imghdr
import os

import tqdm


def check_images(s_dir, ext_list):
    bad_images = []
    bad_ext = []
    s_list = os.listdir(s_dir)
    tf_accepted_types = ['bmp', 'gif', 'jpeg', 'png']
    for klass in s_list:
        klass_path = os.path.join(s_dir, klass)
        if os.path.isdir(klass_path):
            file_list = os.listdir(klass_path)
            bad_files = 0
            pbar = tqdm.tqdm(file_list, position=1, desc=f'[{klass}/9]')
            for f in pbar:
                f_path = os.path.join(klass_path, f)
                index = f.rfind('.')
                ext = f[index + 1:].lower()
                pbar.set_description(f"{bad_files} Bad")
                if ext not in ext_list or imghdr.what(f_path) not in tf_accepted_types:
                    os.remove(f_path)
                    bad_files += 1
                    bad_ext.append(f_path)
                if os.path.isfile(f_path):
                    try:
                        img = cv2.imread(f_path)
                        shape = img.shape
                    except:
                        bad_files += 1
                        os.remove(f_path)
                        bad_images.append(f_path)
    return bad_images, bad_ext


def convert_file_name_format(classes_dir: str):
    pbar = tqdm.tqdm(os.listdir(classes_dir))
    renames = 0
    removes = 0
    for class_name in pbar:
        pbar.set_description(f"Rem={removes}, Ren={renames}")
        class_path = os.path.join(classes_dir, class_name)
        if os.path.isdir(class_path):
            for file_name in os.listdir(class_path):
                file_path = os.path.join(class_path, file_name)
                if "_" in file_name:
                    cnt_splits = file_name.split("_")
                    if len(cnt_splits) >= 3:
                        post_id = (file_name.split("_")[-1]).split('.')[0]
                        extension = file_name.split(".")[-1]
                        new_name = f'{post_id}.{extension}'
                        new_path = os.path.join(class_path, new_name)
                        if os.path.isfile(new_path):
                            removes += 1
                            os.remove(file_path)
                        else:
                            renames += 1
                            os.rename(file_path, new_path)

