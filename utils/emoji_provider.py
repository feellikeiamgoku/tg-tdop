import emoji


class Emoji:
    rainbow = emoji.emojize(':rainbow:')
    robot = emoji.emojize(':robot_face:')
    exclamation_question_mark_selector = emoji.emojize(':exclamation_question_mark_selector:')
    exclamation_mark = emoji.emojize(':exclamation_mark:')
    red_light = emoji.emojize(':police_car_light:')
    smile = emoji.emojize(':smiling_face_with_smiling_eyes:')


if __name__ == "__main__":
    print(emoji.demojize('😊'))
