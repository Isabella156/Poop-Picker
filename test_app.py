import unittest
from io import BytesIO

import werkzeug
from werkzeug.datastructures import FileStorage

from app import app, db
from app.models import User, Note, Pet
from werkzeug import datastructures


class appTestCase(unittest.TestCase):


  def setUp(self):
    app.config.update(
      TESTING=True,
      WTF_CSRF_ENABLED=False,
      SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
      )
    db.create_all()
    self.client = app.test_client()
    self.runner = app.test_cli_runner()


  def tearDown(self):
    db.session.remove()
    db.drop_all()
  

  def create_user(self):
    response = self.client.post('/register', data=dict(
        username='bamboo',
        email='1749553911@qq.com',
        password='tz20081103',
        code='XJEL 2938'
        ), follow_redirects=True)

    data = response.get_data(as_text=True)
    return data

  
  def test_home_page(self):
    response = self.client.get('/')
    data = response.get_data(as_text=True)
    self.assertIn('video', data)


  def test_register_page(self):
    response = self.client.get('/register')
    data = response.get_data(as_text=True)
    self.assertIn('Sign up', data)

    self.create_user()
    self.client.get('/register')
    response = self.client.get('/dashboard')
    data = response.get_data(as_text=True)
    self.assertIn('You are already logged in, please log out to register another account', data)
  

  def test_register_form_validation(self):
    response = self.client.post('/register', data=dict(
      username='111',
      email='1749553911@qq.com',
      password='tz20081103',
      code='XJEL 2938'
      ))
    data = response.get_data(as_text=True)
    self.assertIn('At least 4 letters for username', data)

    response = self.client.post('/register', data=dict(
      username='1111',
      email='1749553911@qq.com',
      password='tz',
      code='XJEL 2938'
      ))
    data = response.get_data(as_text=True)
    self.assertIn('At least 8 letters for password', data)

    response = self.client.post('/register', data=dict(
      username='1111',
      email='1749553911@qq.com',
      password='tz20081103',
      code='XJ'
      ))
    data = response.get_data(as_text=True)
    self.assertIn('At least 4 letters for code', data)


  def test_create_user(self):
    data = self.create_user()
    self.assertIn('bamboo', data)
    # test database
    user = User.query.filter_by(username='bamboo').first()
    self.assertIsNotNone(user)
    self.assertEqual(user.email, '1749553911@qq.com')

  
  def test_duplicate_username(self):
    self.create_user()
    self.client.get('/logout')
    response = self.client.post('/register', data=dict(
        username='bamboo',
        email='1749553911@qq.com',
        password='tz20081103',
        code='XJEL 2938'
        ), follow_redirects=True)
    data = response.get_data(as_text=True)
    self.assertIn('Username already exists', data)


  def test_duplicate_email(self):
    self.create_user()
    self.client.get('/logout')
    response = self.client.post('/register', data=dict(
        username='bambooo',
        email='1749553911@qq.com',
        password='tz20081103',
        code='XJEL 2938'
        ), follow_redirects=True)
    data = response.get_data(as_text=True)
    self.assertIn('Email has been already registered', data)


  def test_login(self):
    self.create_user()
    self.client.get('/logout')
    self.client.post('/login', data=dict(
      username='bamboo',
      password='tz20081103',
      remember=False
      ))
    response = self.client.get('/dashboard')
    data = response.get_data(as_text=True)
    self.assertIn('Hey bamboo', data)
    self.client.get('/login')
    response = self.client.get('/dashboard')
    data = response.get_data(as_text=True)
    self.assertIn('You are already logged in, please log out to login another account', data)


  def test_login_form_validation(self):
    response = self.client.post('/login', data=dict(
      username='bam',
      password='tz20081103',
      remember=False
      ))
    data = response.get_data(as_text=True)
    self.assertIn('At least 4 letters for username', data)

    response = self.client.post('/login', data=dict(
      username='bamboo',
      password='tz',
      remember=False
      ))
    data = response.get_data(as_text=True)
    self.assertIn('At least 8 letters for password', data)


  def test_invalid_username(self):
    response = self.client.post('/login', data=dict(
      username='bamboo',
      password='tz20081103',
      remember=False
      ))
    data = response.get_data(as_text=True)
    self.assertIn('Invalid username!', data)


  def test_incorrect_password(self):
    self.create_user()
    response = self.client.get('/logout')
    response = self.client.post('/login', data=dict(
      username='bamboo',
      password='tz2008110',
      remember=False
      ))
    data = response.get_data(as_text=True)
    self.assertIn('Wrong password!', data)


  def test_log_out(self):
    self.create_user()
    response = self.client.get('/logout',  follow_redirects=True)
    data = response.get_data(as_text=True)
    self.assertIn('video', data)


  def test_changePassword_page(self):
    self.create_user()
    response = self.client.get('/changePassword')
    data = response.get_data(as_text=True)
    self.assertIn('Please Enter your old password', data)

  def test_changePassword(self):
    self.create_user()
    self.client.post('/changePass', data=dict(
      username='bamboo',
      oldpass='tz20081103',
      newPass='tz2008110303'
      ))
    response = self.client.get('/dashboard')
    data = response.get_data(as_text=True)
    self.assertIn('bamboo', data)

  def test_changePassword_form_validation(self):
    self.create_user()
    response = self.client.post('/changePass', data=dict(
      username='bam',
      oldpass='tz20081103',
      newPass='tz2008110303'
      ))
    response = self.client.get('/changePassword')
    data = response.get_data(as_text=True)
    self.assertIn('At least 4 letters for username', data)

    response = self.client.post('/changePass', data=dict(
      username='bamboo',
      oldpass='tz',
      newPass='tz2008110303'
      ))
    response = self.client.get('/changePassword')
    data = response.get_data(as_text=True)
    self.assertIn('At least 8 letters for password', data)

    response = self.client.post('/changePass', data=dict(
      username='bamboo',
      oldpass='tz20081103',
      newPass='tz'
      ))
    response = self.client.get('/changePassword')
    data = response.get_data(as_text=True)
    self.assertIn('At least 8 letters for password', data)


  def test_changePassword_invalid_username(self):
    self.create_user()
    response = self.client.post('/changePass', data=dict(
      username='bambooo',
      oldpass='tz20081103',
      newPass='tz20081103'
      ))
    response = self.client.get('/changePassword')
    data = response.get_data(as_text=True)
    self.assertIn('Wrong username', data)


  def test_changePassword_incorrect_password(self):
    self.create_user()
    response = self.client.post('/changePass', data=dict(
      username='bamboo',
      oldpass='tz200811',
      newPass='tz20081103'
      ))
    response = self.client.get('/changePassword')
    data = response.get_data(as_text=True)
    self.assertIn('Wrong password', data)


  def test_addPet_page(self):
    self.create_user()
    response = self.client.get('/pet')
    data = response.get_data(as_text=True)
    self.assertIn('Whether or not be sterilized', data)
  

  def test_addPet_form_validation(self):
    self.create_user()
    response = self.client.post('/addPet', data=dict(
      petName='',
      petType='dog',
      petBreed='Chinese Rural Dog',
      petGender='male',
      sterilization='neutered',
      weight=8.8,
      birthday='2021-11-30',
      commemorationDay='2021-12-1'
      ))
    response = self.client.get('/pet')
    data = response.get_data(as_text=True)
    self.assertIn('Please input pet name', data)

    response = self.client.post('/addPet', data=dict(
      petName='Max',
      petType='dog',
      petBreed='',
      petGender='male',
      sterilization='neutered',
      weight=8.8,
      birthday='2021-11-30',
      commemorationDay='2021-12-1'
      ))
    response = self.client.get('/pet')
    data = response.get_data(as_text=True)
    self.assertIn('Please enter the pet breed', data)

    response = self.client.post('/addPet', data=dict(
      petName='Max',
      petType='dog',
      petBreed='Chinese Rural Dog',
      petGender='female',
      sterilization='Notneutered',
      birthday='2021-11-30',
      commemorationDay='2021-12-1',
      weight=''
      ))
    response = self.client.get('/pet')
    data = response.get_data(as_text=True)
    self.assertIn('Please enter the weight', data)

    response = self.client.post('/addPet', data=dict(
      petName='Max',
      petType='dog',
      petBreed='Chinese Rural Dog',
      petGender='male',
      sterilization='neutered',
      weight=8.8,
      birthday='2024-11-30',
      commemorationDay='2021-12-1'
      ))
    response = self.client.get('/pet')
    data = response.get_data(as_text=True)
    self.assertIn('Do not enter future dates', data)

    response = self.client.post('/addPet', data=dict(
      petName='Max',
      petType='dog',
      petBreed='Chinese Rural Dog',
      petGender='male',
      sterilization='neutered',
      weight=8.8,
      birthday='2021-11-30',
      commemorationDay='2024-12-1'
      ))
    response = self.client.get('/pet')
    data = response.get_data(as_text=True)
    self.assertIn('Do not enter future dates', data)
  
  
  def add_pet(self):
    response = self.client.post('/addPet', data=dict(
      petName='Max',
      petType='dog',
      petBreed='Chinese Rural Dog',
      petGender='male',
      sterilization='neutered',
      weight=8.8,
      birthday='2021-11-30',
      commemorationDay='2021-12-1'
      ))
    response = self.client.get('/showPet')
    data = response.get_data(as_text=True)
    return data
  
  
  def test_addpet_showPet(self):
    self.create_user()
    data = self.add_pet()
    self.assertIn('Max', data)
    self.assertIn('Chinese Rural Dog', data)
    # database
    pets = Pet.query.all()
    for pet in pets:
      self.assertIsNotNone(pet)
      self.assertEqual(pet.name, 'Max')




  def test_showPet(self):
    self.create_user()
    response = self.client.get('/showPet')
    response = self.client.get('/pet')
    data = response.get_data(as_text=True)
    self.assertIn('You have no pet, please add to view pet', data)
  

  def test_addFamily_form_validation(self):
    self.create_user()
    self.add_pet()

    response = self.client.post('/addFamily/1', json=dict(
      username='alb',
      code='XJCO',
      ))
    data = response.get_json()
    self.assertEqual(data['error'], 'At least 4 letters for username')


    response = self.client.post('/addFamily/1', json=dict(
      username='albert',
      code='XJC',
      ))
    data = response.get_json()
    self.assertEqual(data['error'], 'At least 4 letters for code')
  

  def test_addFamily(self):
    self.client.post('/register', data=dict(
        username='albert',
        email='174955391@qq.com',
        password='tz20081103',
        code='XJEL 2938'
        ), follow_redirects=True)
    self.create_user()
    self.add_pet()
    response = self.client.post('/addFamily/1', json=dict(
      username='albert',
      code='XJEL 2938',
      ))
    data = response.get_json()
    self.assertEqual(data['success'], 'Successfully add family for Max')

    # database
    user = User.query.filter_by(username='albert').first()
    for pet in user.pets:
      self.assertIsNotNone(pet)
      self.assertEqual(pet.name, 'Max')
    
    pet = Pet.query.filter_by(name='Max').first()
    for family in pet.families:
      if family.username == 'albert':
        self.assertEqual(family.username, 'albert')


  def test_addFamily_invalid_username(self):
    self.create_user()
    self.add_pet()
    response = self.client.post('/addFamily/1', json=dict(
      username='albert',
      code='XJEL 2938',
      ))
    data = response.get_json()
    self.assertEqual(data['error'], 'No such user')


  def test_addFamily_incorrect_code(self):
    self.client.post('/register', data=dict(
        username='albert',
        email='174955391@qq.com',
        password='tz20081103',
        code='XJEL 2938'
        ), follow_redirects=True)
    self.create_user()
    self.add_pet()
    response = self.client.post('/addFamily/1', json=dict(
      username='albert',
      code='XJEL 293',
      ))
    data = response.get_json()
    self.assertEqual(data['error'], 'Wrong code')
  

  def test_deletePet(self):
    self.client.post('/register', data=dict(
        username='albert',
        email='174955391@qq.com',
        password='tz20081103',
        code='XJEL 2938'
        ), follow_redirects=True)
    self.client.get('/logout')
    self.create_user()
    self.add_pet()
    self.client.post('/addFamily/1', json=dict(
      username='albert',
      code='XJEL 2938',
      ))
    self.client.get('/deletePet/1')
    response = self.client.get('/dashboard')
    data = response.get_data(as_text=True)
    self.assertIn('Successfully delete pet', data)

    # database
    a = []
    pet = Pet.query.all()
    self.assertEqual(a, pet)

    user = User.query.filter_by(username='albert').first()
    pets = user.pets
    self.assertEqual(a, pets)

    user = User.query.filter_by(username='bamboo').first()
    pets = user.pets
    self.assertEqual(a, pets)

  
  def add_note(self):
    filename = 'ball.jpg'

    with open('../puppyImage/ball.jpg', 'rb') as f:
      stream = BytesIO(f.read())

    file = FileStorage(stream=stream, filename=filename)

    response = self.client.post('/addNote/1', data=dict(
        title='Ball',
        date='2019-10-09',
        content='Pick the ball for the first time',
        file=file
        ), follow_redirects=True)

    data = response.get_data(as_text=True)
    return data
  
  
  def test_add_note(self):
    self.create_user()
    self.add_pet()
    data = self.add_note()
    self.assertIn('Add note successfully!', data)

    # database
    pet = Pet.query.filter_by(id=1).first()
    user = User.query.filter_by(id=1).first()
    for note in pet.notes:
      self.assertEqual(user, note.author)
      if note.title == 'Ball':
        self.assertEqual('Pick the ball for the first time', note.content)

      
  
  def test_addNote_form_validation(self):
    self.create_user()
    self.add_pet()

    response = self.client.post('/addNote/1', data=dict(
        title='Ball',
        date='2025-10-09',
        content='Pick the ball for the first time'
        ), follow_redirects=True)
    data = response.get_data(as_text=True)
    self.assertIn('Do not enter future dates', data)

    
    response = self.client.post('/addNote/1', data=dict(
        title='Ball',
        date='2019-10-09',
        content=''
        ), follow_redirects=True)
    data = response.get_data(as_text=True)
    self.assertIn('Please enter the content', data)

    file_loc = open('../puppyImage/1.txt')
    file = werkzeug.datastructures.FileStorage(file_loc)
    response = self.client.post('/addNote/1', data=dict(
        title='Ball',
        date='2019-10-09',
        content='Pick the ball for the first time',
        file=file
        ), follow_redirects=True)
    data = response.get_data(as_text=True)
    self.assertIn('Supported file type: png, jpg, jpeg', data)
  

  def test_showNote(self):
    self.create_user()
    self.add_pet()
    filename = 'ball.jpg'

    with open('../puppyImage/ball.jpg', 'rb') as f:
      stream = BytesIO(f.read())

    file = FileStorage(stream=stream, filename=filename)

    self.client.post('/addNote/1', data=dict(
        title='Ball',
        date='2019-10-09',
        content='Pick the ball for the first time',
        file=file
        ), follow_redirects=True)

    response = self.client.get('/showNote/1')
    data = response.get_data(as_text=True)
    self.assertIn('bamboo', data)
    self.assertIn('Ball', data)
  

  def test_deleteNote(self):
    self.create_user()
    self.add_pet()
    self.add_note()
    response = self.client.get('/deleteNote/1')
    response = self.client.get('/showPet')
    data = response.get_data(as_text=True)
    self.assertIn('Delete note successfully', data)

    # database
    empty = []
    note = Note.query.all()
    self.assertEqual(empty, note)
  

    

    
    


  













