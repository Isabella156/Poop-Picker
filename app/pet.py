from app import app, db
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required
from .models import Pet, User
from datetime import datetime, date

env = app.jinja_env

def week(dateString):
    return datetime.strptime(dateString, "%Y%m%d").strftime('%A')

env.filters['week'] = week



@app.route('/pet')
@login_required
def pet():
    return render_template("addPet.html")


@app.route('/addPet', methods=['POST'])
@login_required
def addPet():
    # get information for pet
    name = request.form.get('petName')
    if name == '':
        flash('Please input pet name', 'warning')
        return redirect(url_for('pet'))

    type = request.form.get("petType")

    petBreed = request.form.get('petBreed')
    if petBreed == '':
        flash('Please enter the pet breed', 'warning')
        return redirect(url_for('pet'))

    gender = request.form.get('petGender')
    if gender == 'male':
        gender = False
    else:
        gender = True

    sterilization = request.form.get('sterilization')
    if sterilization == 'neutered':
        sterilization = True
    else:
        sterilization = False

    weight = request.form.get('weight')
    if weight == '':
        flash('Please enter the weight', 'warning')
        return redirect(url_for('pet'))

    birthday = request.form.get('birthday')
    birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
    commemorationDay = request.form.get('commemorationDay')
    commemorationDay = datetime.strptime(commemorationDay, "%Y-%m-%d").date()
    today = date.today()
    if birthday > today or commemorationDay > today:
        flash('Do not enter future dates', 'warning')
        return redirect(url_for('pet'))
    
    pet = Pet(name=name, type=type, breed=petBreed, gender=gender, sterilization=sterilization, 
        birthday=birthday,commemorationDay=commemorationDay, weight=weight)
    db.session.add(pet)
    # add families for 
    pet.families.append(current_user)
    
    db.session.commit()
    message = 'Add pet successfully'
    app.logger.info('%s: %s for %s' %(message, current_user.username, pet.name))

    return redirect(url_for('showPet'))


@app.route('/showPet')
@login_required
def showPet():
    pet = current_user.pets
    if pet == []:
        flash('You have no pet, please add to view pet', 'warning')
        return redirect(url_for('pet'))
    return render_template('showPet.html', user=current_user)

    

@app.route('/addFamily/<int:pet_id>', methods=['POST'])
def addFamily(pet_id):
    pet = Pet.query.filter_by(id=pet_id).first()
    data = request.get_json()
    username = data['username']
    if len(username) < 4:
        return jsonify({'error': 'At least 4 letters for username'})

    code = data['code']
    if len(code) < 4:
        return jsonify({'error': 'At least 4 letters for code'})

    user = User.query.filter_by(username=username).first()
    if user:
        if(user.code == code):
            pet.families.append(user)
            db.session.commit()
            message = 'Successfully add family for ' + pet.name
            app.logger.info('%s: %s' %(message, user.username))
            return jsonify({'success': message})
        else:
            return jsonify({'error': 'Wrong code'})
    else:
        return jsonify({'error': 'No such user'})



@app.route('/deletePet/<int:pet_id>')
def deletePet(pet_id):
    pet = Pet.query.filter_by(id=pet_id).first()
    message = 'Successfully delete pet'
    app.logger.info('%s: %s' %(message, pet.name))
    db.session.delete(pet)
    db.session.commit()
    flash(message, 'success')
    return redirect(url_for('dashboard'))