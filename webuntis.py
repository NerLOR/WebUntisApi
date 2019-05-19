#!/usr/bin/python3.7
from typing import Dict
from typing import Any
import requests
import time
import json
import datetime


def date_to_untis(date: datetime.date) -> int:
    return int(datetime.date.strftime(date, '%Y%m%d'))


def untis_to_date(date: int) -> datetime.date:
    date = str(date)
    return datetime.date(int(date[0:4]), int(date[4:6]), int(date[6:8]))


class Schoolyear:
    def __init__(self, schoolyear_id: int, name: str, start_date: int, end_date: int):
        self._id = schoolyear_id
        self._name = name
        self._start_date = untis_to_date(start_date)
        self._end_date = untis_to_date(end_date)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def start_date(self) -> datetime.date:
        return self._start_date

    @property
    def end_date(self) -> datetime.date:
        return self._end_date

    def __str__(self) -> str:
        return f'{{schoolyear#{self.id}:{self.name}}}'


class Department:
    def __init__(self, department_id: int, nr: int, name: str):
        self._id = department_id
        self._nr = nr
        self._name = name

    @property
    def id(self) -> int:
        return self._id

    @property
    def nr(self) -> int:
        return self._nr

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return f'{{department#{self.id}:{self.nr}:{self.name}}}'


class Student:
    def __init__(self):
        pass


class Klasse:
    def __init__(self, klasse_id: int, name: str, description: str,
                 department_id: int, teacher1_id: int, teacher2_id: int):
        self._id = klasse_id
        self._name = name
        self._description = description
        self._department_id = department_id
        self._teacher1_id = teacher1_id
        self._teacher2_id = teacher2_id

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def department_id(self) -> int:
        return self._department_id

    @property
    def teacher1_id(self) -> int:
        return self._teacher1_id

    @property
    def teacher2_id(self) -> int:
        return self._teacher2_id

    def __str__(self) -> str:
        return f'{{klasse#{self.id}:{self.name}}}'


class Teacher:
    def __init__(self):
        pass


class Room:
    def __init__(self, room_id: int, room_nr: str, name: str):
        self._id = room_id
        self._nr = room_nr
        self._name = name

    @property
    def id(self) -> int:
        return self._id

    @property
    def nr(self) -> str:
        return self._nr

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return f'{{room#{self.id}:{self.nr}:{self.name}}}'


class Subject:
    def __init__(self, subject_id: int, uid: str, name: str):
        self._id = subject_id
        self._uid = uid
        self._name = name

    @property
    def id(self) -> int:
        return self._id

    @property
    def uid(self) -> str:
        return self._uid

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return f'{{subject#{self.id}:{self.uid}:{self.name}}}'


class Session:
    def __init__(self, server: str, school: str):
        self._session = requests.session()
        self._server = server
        self._school = school
        self._username = None
        self._password = None
        self._useragent = None
        self._user = None

    def _request(self, method: str, params: Dict[str, Any] = None):
        headers = {
            'User-Agent': self._useragent,
            'Content-Type': 'application/json;charset=UTF-8'
        }
        request_body = {
            'id': time.time(),
            'method': method,
            'params': params if params is not None else {},
            'jsonrpc': '2.0'
        }
        response = self._session.post(f'https://{self._server}/WebUntis/jsonrpc.do?school={self._school}',
                                      data=json.dumps(request_body), headers=headers)

        if response.status_code != 200:
            raise ConnectionError('Invalid Response')

        try:
            result = json.loads(response.text)
        except ValueError:
            raise ValueError('Invalid JSON Response')
        else:
            if result.get('error', False):
                raise NameError(f'{result["error"]["message"]}: {method}')
            return result.get('result', {})

    def authenticate(self, username: str, password: str, useragent: str) -> bool:
        if self._user is not None:
            raise AssertionError('Already logged in')
        self._username = username
        self._password = password
        self._useragent = useragent
        res = self._request('authenticate', {
            'user': self._username,
            'password': self._password,
            'client': self._useragent
        })
        self._user = res
        return True

    def get_departments(self) -> [Department]:
        return [Department(department['id'], int(department['name']), department['longName'])
                for department in self._request('getDepartments')]

    def get_holidays(self) -> [Dict[str, Any]]:
        return self._request('getHolidays')

    def get_klassen(self, schoolyear_id: int = None) -> [Dict[str, Any]]:
        params = {}
        if schoolyear_id is not None:
            params['schoolyearId'] = schoolyear_id
        return [Klasse(klasse['id'], klasse['name'], klasse['longName'], klasse.get('did', None),
                       klasse.get('teacher1', None), klasse.get('teacher2', None))
                for klasse in self._request('getKlassen', params=params)]

    def get_timetable(self, start_date: datetime.date, end_date: datetime.date):
        pass

    def get_rooms(self) -> [Room]:
        return [Room(room['id'], room['name'], room['longName'])
                for room in self._request('getRooms')]

    def get_schoolyears(self) -> [Schoolyear]:
        return [Schoolyear(schoolyear['id'], schoolyear['name'], schoolyear['startDate'], schoolyear['endDate'])
                for schoolyear in self._request('getSchoolyears')]

    def get_subjects(self) -> [Subject]:
        return [Subject(subject['id'], subject['name'], subject['longName'])
                for subject in self._request('getSubjects')]

    def get_teachers(self) -> [Dict[str, Any]]:
        return self._request('getTeachers')

    def get_status_data(self) -> [Dict[str, Any]]:
        return self._request('getStatusData')

    def get_last_import_time(self) -> [Dict[str, Any]]:
        return self._request('getLatestImportTime')

    def get_substitutions(self, start_date: datetime.date, end_date: datetime.date, department_id: int = 0) -> [Dict[str, Any]]:
        return self._request('getSubstitutions')

    def get_timegrid_untis(self) -> [Dict[str, Any]]:
        return self._request('getTimegridUntis')

    def get_students(self) -> [Dict[str, Any]]:
        return self._request('getStudents')

    def get_exam_types(self) -> [Dict[str, Any]]:
        return self._request('getExamTypes')

    def get_exams(self, start_date: datetime.date, end_date: datetime.date, exam_type_id: int = 0) -> [Dict[str, Any]]:
        return self._request('getExams', {
            'startDate': date_to_untis(start_date),
            'endDate': date_to_untis(end_date),
            'examTypeId': exam_type_id
         })

    def get_timetable_with_absences(self, start_date: datetime.date, end_date: datetime.date):
        pass

    def get_class_register_events(self):
        pass

    def search(self):
        pass


if __name__ == '__main__':
    session = Session(server='urania.webuntis.com', school='htl3r')
    session.authenticate(username='htl3r', password='htl3r', useragent='Necronda')

    for obj in session.get_teachers():
        print(obj)