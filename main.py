import pytesseract
import cv2
from pdf2image import convert_from_path
from datetime import datetime
import json

file_path = "atlas.pdf"
pytesseract.pytesseract.tesseract_cmd = "Tesseract-OCR/tesseract.exe"

exception = {
    "sel": "scl"
}


def convert_pdf_page(page_number):
    print("Convert start")
    images = convert_from_path(file_path, poppler_path=r"C:\poppler-0.68.0\bin", last_page=page_number,
                               first_page=page_number)
    print("Convert end")
    return images[0]


def save_image_from_popler(image, name):
    image.save(str(name) + ".png")
    print("image: " + str(name) + " saved")


def open_image_with_open_cv(name):
    image = cv2.imread(str(name) + ".png")
    print("image is open")
    return image


def cut_image(image, is_save=False):
    y = 230
    x = 0
    height = image.shape[0] - y - 100
    width = image.shape[1] - x
    image = image[y:y + height, x:x + width]
    if is_save:
        cv2.imwrite("C:\Projects\starpy\cut_image.png", image)
    print("image cutted")
    return image


def change_image(image):
    image_changed = cv2.resize(image, None, fx=2, fy=2)
    print("image resized")
    image_changed = cv2.cvtColor(image_changed, cv2.COLOR_BGR2GRAY)
    print("image color changed")
    return image_changed


def get_text_from_image(image):
    config = '--oem 1 --psm 6'
    txt = pytesseract.image_to_string(image, config=config, lang='eng')
    return txt


def create_list_of_stars():
    image_one = open_image_with_open_cv("stars_name1")
    image_one = change_image(image_one)
    image_two = open_image_with_open_cv("stars_name2")
    image_two = change_image(image_two)
    txt1 = get_text_from_image(image_one)
    txt2 = get_text_from_image(image_two)
    my_file = open("star_names.txt", "w+", encoding="utf-8")
    my_file.write(str(txt1))
    my_file.write(str(txt2))
    my_file.close()


def get_list_of_star_names():
    file1 = open("star_names.txt", "r")
    star_list = []
    while True:
        line = file1.readline()
        if not line:
            break
        line = line.strip()
        line = line.split()
        if len(line) != 0:
            star_list.append(line[0])
    file1.close()
    return star_list


def create_table_of_stars_txt():
    my_file = open("star_table.txt", "w+", encoding="utf-8")
    for i in range(34):
        image = convert_pdf_page(i + 8)
        save_image_from_popler(image, "image")
        image = open_image_with_open_cv("image")
        image = cut_image(image)
        image = change_image(image)
        txt = get_text_from_image(image)
        print(txt)
        txt = txt.replace('|', ' ')
        txt = txt.replace('[', ' ')
        txt = txt.replace(']', ' ')
        txt = txt.replace('/', ' ')
        txt = txt.replace('{', ' ')
        txt = txt.replace('}', ' ')
        txt = txt.replace('°', ' ')
        txt = txt.replace("'", ' ')
        txt = txt.replace("=", ' ')
        my_file.write("\n")
        my_file.write("_page_" + str(i))
        my_file.write("\n")
        my_file.write(str(txt))
    my_file.close()


def create_intermediate_table_of_star():
    file = open("star_table.txt", "r", encoding="utf-8")
    ist_file = open("intermediate_star_table.txt", "w+", encoding="utf-8")
    star_list = get_list_of_star_names()
    intermediate_table_of_star = []
    digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    while True:
        line = file.readline()
        if not line:
            break
        line = line.strip()
        line = line.lower()
        line = line.split()
        if len(line) == 1 and "_page_" in line[0]:
            ist_file.write("\n")
            ist_file.write(line[0])
            print(line[0])
            ist_file.write("\n")
        else:
            for i in range(4):
                star_is_find = False
                for s in range(len(line)):
                    for j in range(len(star_list)):
                        if not star_is_find:
                            if "sel" in line[s].lower():
                                line[s] = line[s].replace("sel", 'scl')
                            if "pse" in line[s].lower():
                                line[s] = line[s].replace("pse", 'psc')
                            if "det" in line[s].lower():
                                line[s] = line[s].replace("det", 'oct')
                            if str(star_list[j].lower()) in str(line[s].lower()):
                                index = s
                                star_string = ''
                                star_is_find = True
                                digits_find = False
                                if s + 1 < len(line):
                                    for k in range(len(digits)):
                                        if digits[k] in line[s + 1]:
                                            digits_find = True
                                if not digits_find and s + 1 < len(line):
                                    index = s + 1
                                for m in range(index + 1):
                                    star_string += line[m]
                                    star_string += " "
                                intermediate_table_of_star.append(star_string)
                                ist_file.write(star_string)
                                ist_file.write("\n")
                                for n in range(index + 1):
                                    line.pop(0)
    ist_file.close()
    file.close()


page_number = 0


def create_json_table_of_star():
    file = open("intermediate_star_table.txt", "r", encoding="utf-8")
    list_of_star_info = []
    while True:
        line = file.readline()
        if not line:
            break
        line = line.strip()
        line = line.lower()
        line = line.split()
        if len(line) == 1 and "_page_" in line[0]:
            global page_number
            print("page_number")
            page_number = line[0][6:]
            list_of_star_info.append({
                "page": page_number,
                "stars": []
            })
            print(page_number)
        elif len(line) > 1:
            star_info = {"alpha": line[0], "sigma": 0, "mag": 0, "sp": "", "const": ""}
            line.pop(0)
            for i in range(len(line)):
                if "." in line[i]:
                    if len(line[i]) > 3:
                        star_info["mag"] = line[i][-3:]
                        if line[i][len(line[i]) - 4] == "1":
                            line[i] = line[i][:-4]
                    else:
                        star_info["mag"] = line[i]
                        line.pop(i)
                    break

            for i in range(len(line)):
                if "+" in line[i] or "-" in line[i]:
                    if i+1<len(line):
                        if 1 < len(line[i]) < 4 and "." not in line[i + 1]:
                            star_info["sigma"] = line[i] + " " + line[i + 1]
                            line[i] = ""
                            line[i + 1] = ""
                    elif len(line[i]) == 1:
                        if i != len(line) - 1:
                            if 1 <= len(line[i + 1]) < 3:
                                if 1 <= len(line[i + 2]) < 3:
                                    star_info["sigma"] = line[i] + "" + line[i + 1] + " " + line[i + 2]
                                    line[i] = ""
                                    line[i + 1] = ""
                                    line[i + 2] = ""
                            elif len(line[i + 1]) > 2:
                                star_info["sigma"] = line[i] + "" + line[i + 1][0] + " " + line[i + 1][1:]
                    elif 3 < len(line[i]) < 6 and (line[i][0] == "-" or line[i][0] == "+"):
                        if len(line[i]) == 5:
                            star_info["sigma"] = line[i][:-2] + " " + line[i][3:]
                            line[i] = ""
                        if len(line[i]) == 4:
                            star_info["sigma"] = line[i][0] + line[i][1] + " " + line[i][2:]
                            line[i] = ""

            for i in range(len(line)):
                if len(line[i]) == 2:
                    if line[i][0].isalpha() or line[i][1].isalpha():
                        star_info["sp"] = line[i]
                        line[i] = ""

            for i in range(len(line)):
                const = ""
                if len(line[i]) > 0:
                    const += line[i]
                    line[i] = ''
                    const += " "
                star_info["const"] = const
            list_of_star_info[len(list_of_star_info) - 1]["stars"].append(star_info)
        list_of_star_info
    file.close()
    return list_of_star_info


def serialization_in_json(table_of_star):
    with open("data_file.json", "w") as write_file:
        json.dump(table_of_star, write_file)


def main():
    start_time = datetime.now()
    serialization_in_json(create_json_table_of_star())
    print(datetime.now() - start_time)


if __name__ == '__main__':
    main()
