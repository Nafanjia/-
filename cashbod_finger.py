import shutil
import PyPDF2
from PIL import Image
import pytesseract
import time
import os
from pymongo import MongoClient
from multiprocessing import Pool

mongo_client = MongoClient()

path = 'image'


def sort_file(path):
    pdf_list = []
    image_list = []
    for root, dirs, files in os.walk(path):
        for i in range(len(files)):
            file_name, file_extension = os.path.splitext(f'{root}\\{files[i]}')
            file_name = file_name.split('\\')[-1]
            if file_extension == '.pdf':
                pdf_path = shutil.copy(f'{root}\\{files[i]}', f'{os.getcwd()}\\data_for_parse\\pdf\\')
                pdf = {
                    'file_name': file_name,
                    'pdf_path': pdf_path,
                    'file_type':file_extension
                }
                pdf_list.append(pdf)
            elif file_extension == '.jpg':
                image_path = shutil.copy(f'{root}\\{files[i]}', f'{os.getcwd()}\\data_for_parse\\image\\')
                image = {
                    'file_name': file_name,
                    'image_path': image_path,
                    'file_type': file_extension
                }
                image_list.append(image)
            else:
                pass
    return pdf_list, image_list


def extract_pdf_image(pdf_path):
    try:
        pdf_file = PyPDF2.PdfFileReader(open(pdf_path, 'rb'), strict=False)
    except PyPDF2.utils.PdfReadError as e:
        return None
    except FileNotFoundError as e:
        return None
    result = []

    for page_num in range(0, pdf_file.getNumPages()):
        page = pdf_file.getPage(page_num)
        page_obj = page['/Resources']['/XObject'].getObject()
        for key, value in page['/Resources']['/XObject'].getObject().items():
                if page_obj[f'{key}'].get('/Subtype') == '/Image':
                    size = (page_obj[f'{key}']['/Width'], page_obj[f'{key}']['/Height'])
                    data = page_obj[f'{key}']._data
                    if page_obj[f'{key}']['/ColorSpace'] == '/DeviceRGB':
                        mode = 'RGB'
                    else:
                        mode = 'P'

                    if page_obj[f'{key}']['/Filter'] == '/FlateDecode':
                        file_type = 'png'
                    elif page_obj[f'{key}']['/Filter'] == '/DCTDecode':
                        file_type = 'jpg'
                    elif page_obj[f'{key}']['/Filter'] == '/JPXDecode':
                        file_type = 'jp2'
                    else:
                        file_type = 'bmp'
                    result_strict = {
                        'page': page_num,
                        'size': size,
                        'data': data,
                        'mode': mode,
                        'file_type': file_type,
                    }
                    result.append(result_strict)
    return result



def save_pdf_image(file_name, f_path, *pdf_strict, image_list):
    for item in pdf_strict:
        name = f"{file_name}_#_{item['page']}.{item['file_type']}"
        image_name, file_extension = os.path.splitext(name)
        image_path = f"{os.getcwd()}\\{f_path}\\{name}"
        with open(image_path, "wb") as image:
            image.write(item['data'])
        image = {
            'file_name': image_name,
            'image_path': image_path,
            'file_type': '.pdf',
            'page': item['page']
        }
        image_list.append(image)
    return image_list


def extract_number(file_path):
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    img_obj = Image.open(file_path)
    text = pytesseract.image_to_string(img_obj, lang='rus')
    pattern = 'заводской (серийный) номер'
    pattern2 = 'заводской номер (номера)'
    pattern3 = 'заводской номер'
    result = []
    for idx, line in enumerate(text.split('\n')):
        if line.lower().find(pattern) + 1 or line.lower().find(pattern2) + 1 or line.lower().find(pattern3) + 1:
            eng_text = pytesseract.image_to_string(img_obj, 'eng')
            number = eng_text.split('\n')[idx].split(' ')[-1]
            result.append(number)
    return result


def process_item(item):
    database = mongo_client['image']
    collection = database['numbers']
    collection.insert_one(item)
    return item


def process_item_fail(item):
    database = mongo_client['image_fail']
    collection = database['image_error']
    collection.insert_one(item)
    return item


image_path = 'data_for_parse\\image'


if __name__ == '__main__':
    pdf_list, image_list = sort_file(path)
    for i in range(len(pdf_list)):
        pdf_result = extract_pdf_image(pdf_list[i]['pdf_path'])
        if pdf_result:
            save_pdf_image(pdf_list[i]['file_name'], image_path, *pdf_result, image_list=image_list)
        else:
            shutil.copy(pdf_list[i]['pdf_path'], f'{os.getcwd()}\\data_for_parse\\error\\')
    lists = []
    for i in range(len(image_list)):
        lists.append(image_list[i]['image_path'])
    for lis in lists:
        pool = Pool(processes=3)

        res = pool.apply_async(extract_number, (lis,))
        rek = res.get()
        if rek == [] and image_list[i]['file_type'] == '.pdf':
            shutil.copy(image_list[i]['image_path'], f'{os.getcwd()}\\data_for_parse\\error\\')
            item = {
                'file_name': image_list[i]['file_name'],
                'file_path': image_list[i]['image_path'].split(os.getcwd())[-1],
                'page': image_list[i]['page']
            }
            process_item_fail(item)
        elif rek == [] and image_list[i]['file_type'] != '.pdf':
            shutil.copy(image_list[i]['image_path'], f'{os.getcwd()}\\data_for_parse\\error\\')
            item = {
                'file_name': image_list[i]['file_name'],
                'file_path': image_list[i]['image_path'].split(os.getcwd())[-1]
            }
            process_item_fail(item)
        else:
            item = {
                'file_name': image_list[i]['file_name'],
                'numbers': rek
            }
            process_item(item)

