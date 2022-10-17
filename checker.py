import cv2 as cv
import pytesseract as tess
import numpy as np

CHOICES = {"a": 0, "A": 0, "b": 1, "B": 1, "c": 2, "C": 2, "d": 3, "D": 3}
TOTAL_ITEMS = 20

# load answers
f = open("answer.txt", "r")
answers = []
line = f.readline().replace("\n", "")
answers.append(line)

while line != "":
    line = f.readline().replace("\n", "")
    answers.append(line)
answers = answers[:-1]

# if statements for wrong inputs
if len(answers) != 20:
    print("answer.txt has wrong inputs pls recheck.")
else:
    # load image
    image = cv.imread("images/sample02.png")
    copy_image = image.copy()

    # crop image to isolate ocr and checking
    cropped_lower = copy_image[180:-1, 0:-1]
    cropped_upper = copy_image[0:180, 0:-1]

    # process image: threshold and grayscale
    lower_image_gray = cv.cvtColor(cropped_lower, cv.COLOR_BGR2GRAY)
    upper_image_gray = cv.cvtColor(cropped_upper, cv.COLOR_BGR2GRAY)

    lower_ret, lower_thresh = cv.threshold(lower_image_gray, 180, 255, 0)
    upper_ret, upper_thresh = cv.threshold(upper_image_gray, 180, 255, 0)

    lower_contours, lower_hierarchy = cv.findContours(lower_thresh,
                                                      cv.RETR_LIST,
                                                      cv.CHAIN_APPROX_NONE)
    upper_contours, upper_hierarchy = cv.findContours(upper_thresh,
                                                      cv.RETR_LIST,
                                                      cv.CHAIN_APPROX_NONE)

    student_answer = {}
    student_left = {}
    student_right = {}
    stud_list = []
    left = {}
    right = {}
    coordinates = {}
    temp = []
    count = 1
    i = 0
    left_count = 10
    right_count = 20
    h = 0
    w = 0
    # store coordinates of all circles
    for cont in lower_contours:
        area = cv.contourArea(cont)
        if 1000 > area > 900:
            x, y, w, h = cv.boundingRect(cont)
            shaded = cv.mean(cropped_lower[y:y + h, x:x + h])
            if count <= 20:
                if count % 2 != 0:
                    if i < 3:
                        temp.append(x)
                        i += 1
                        if 100 > shaded[0] > 75:
                            coor = (x, y)
                            stud_list.append(coor)
                    else:
                        temp.append(x)
                        temp = temp[::-1]
                        temp.append(y)
                        right[right_count] = temp
                        if 100 > shaded[0] > 75:
                            coor = (x, y)
                            stud_list.append(coor)
                        student_right[right_count] = stud_list
                        temp = []
                        i = 0
                        count += 1
                        right_count -= 1
                        stud_list = []
                else:
                    if i < 3:
                        temp.append(x)
                        i += 1
                        if 100 > shaded[0] > 75:
                            coor = (x, y)
                            stud_list.append(coor)
                    else:
                        temp.append(x)
                        temp = temp[::-1]
                        temp.append(y)
                        left[left_count] = temp
                        if 100 > shaded[0] > 75:
                            coor = (x, y)
                            stud_list.append(coor)
                        student_left[left_count] = stud_list
                        temp = []
                        i = 0
                        count += 1
                        left_count -= 1
                        stud_list = []
            if 100 > shaded[0] > 75:
                cv.drawContours(cropped_lower, [cont], -1,
                                (255, 0, 255), 2, cv.LINE_AA)
    coordinates = left | right
    student_answer = student_left | student_right
    coordinates["w"] = w
    coordinates["h"] = h

    text = tess.image_to_string(cropped_upper)
    text = text.replace("\n", "")
    text = text.replace("ANSWER SHEET", "")
    text = text.replace("Name:", "")
    text = text.replace("_", "")
    text = text.replace("Score", "")
    text = text.replace("_", "")
    text = text.replace("Date:", "")
    text = text.replace("ate:", "")
    text = text.replace(":", "")

    # get answer key coordinates
    j = 1
    coord_answer_key = []
    for ans in answers:
        x = coordinates[j][CHOICES[ans[-1]]]
        y = coordinates[j][-1]
        coords = (x, y)
        cropped_lower = cv.rectangle(cropped_lower, (x, y),
                                     (x + coordinates['w'],
                                      y + coordinates['h']),
                                     (0, 255, 0), 2)
        coord_answer_key.append(coords)
        j += 1

    # coord_answer_key
    # student_answer
    score = 0
    for key, value in student_answer.items():
        if len(student_answer[key]) == 1:
            if (coord_answer_key[key-1])[0] == (student_answer[key])[0][0]:
                score += 1

    text = text[:-8]
    print(score)
    print(text)

full = np.concatenate((cropped_upper, cropped_lower), axis=0)
cv.putText(full, f'{score}/20', (480, 115), cv.FONT_HERSHEY_SIMPLEX,
           0.6, (16, 10, 240), 2)
cv.putText(full, f'Name: {text}', (15, 30),
           cv.FONT_HERSHEY_SIMPLEX, 0.6, (16, 10, 240), 2)

cv.imshow("Answer Sheet", full)
cv.waitKey(0)
cv.destroyAllWindows()