import emoji


class Emoji:
    rainbow = emoji.emojize(':rainbow:')
    robot = emoji.emojize(':robot_face:')
    exclamation_mark = emoji.emojize(':exclamation_mark:')
    red_light = emoji.emojize(':police_car_light:')
    smile = emoji.emojize(':smiling_face_with_smiling_eyes:')
    sad = emoji.emojize(':disappointed_face:')
    angry = emoji.emojize(':pouting_face:')

if __name__ == "__main__":
    print(emoji.demojize('😊'))
