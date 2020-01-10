import os
import random
import argparse
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from datacenter.models import Schoolkid, Mark, Chastisement, Commendation, Lesson

COMPLIMENTS = ['Молодец!', 'Отлично!', 'Хорошо!', 'Гораздо лучше, чем я ожидал!', 'Ты меня приятно удивил!',
               'Великолепно!', 'Прекрасно!', 'Ты меня очень обрадовал!', 'Именно этого я давно ждал от тебя!',
               'Сказано здорово – просто и ясно!', 'Ты, как всегда, точен!', 'Очень хороший ответ!',
               'Ты сегодня прыгнул выше головы!', 'Потрясающе!', 'Замечательно!']

def fix_marks(schoolkid):

    child = Schoolkid.objects.get(full_name__contains=schoolkid)

    bad_marks = Mark.objects.filter(schoolkid=child, points__lt=4)

    for mark in bad_marks:
        mark.points = 5
        mark.save()

def remove_chastisements(schoolkid):

    child = Schoolkid.objects.get(full_name__contains=schoolkid)

    chastisements = Chastisement.objects.filter(schoolkid=child)

    for chastisement in chastisements:
        chastisement.delete()

def create_commendation(schoolkid, subject):

    child = Schoolkid.objects.get(full_name__contains=schoolkid)

    lessons = Lesson.objects.filter(year_of_study=child.year_of_study, group_letter__contains=child.group_letter)

    subjec_lesson = lessons.filter(subject__title=subject).order_by('-date')[0]

    Commendation.objects.create(text=random.choice(COMPLIMENTS),
                                schoolkid=child,
                                subject=subjec_lesson.subject,
                                teacher=subjec_lesson.teacher,
                                created=subjec_lesson.date)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Скрипт для изменения оценок, удаления замечаний и добавления похвалы в базе данных учеников')
    parser.add_argument('name', help='ФИО ученика')
    parser.add_argument('-s', '--subject', help='Название предмета')
    args = parser.parse_args()

    try:
        fix_marks(args.name)
        remove_chastisements(args.name)
        print('Оценки исправлены, замечания удалены')

        if args.subject:
            create_commendation(args.name, args.subject)
            print(f'Добавлена похвала по предмету {args.subject}')

    except (Schoolkid.DoesNotExist, Schoolkid.MultipleObjectsReturned):
        print('Ученик не найден или найдено сразу несколько учеников')
        exit(0)
