from app import app, db
from flask import render_template, redirect, url_for, request, flash, g
from datetime import datetime
from werkzeug.utils import secure_filename
from .models import Pet, Note
from flask_login import current_user
import os
import random




ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
# check the file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_uuid():
    nowTime = datetime.now().strftime("%Y%m%d%H%M%S")
    randomNum = random.randint(0, 100)
    if randomNum <= 10:
        randomNum = str(0) + str(randomNum)
    uniqueNum = str(nowTime) + str(randomNum)
    return uniqueNum



@app.route('/note/<int:pet_id>')
def note(pet_id):
    return render_template("addNote.html", pet_id=pet_id)


@app.route('/addNote/<int:pet_id>', methods=['GET', 'POST'])
def addNote(pet_id):
    pet = Pet.query.filter_by(id=pet_id).first()

    date = request.form.get('date')
    date = datetime.strptime(date, "%Y-%m-%d").date()
    today = date.today()

    if( date > today):
        flash('Do not enter future dates', 'warning')
        return redirect(url_for('note', pet_id=pet.id))

    title = request.form.get('title')

    content = request.form.get('content')
    content = content.strip()
    if content == '':
        flash('Please enter the content', 'warning')
        return redirect(url_for('note', pet_id=pet.id))

    file = request.files['file']
    if file:
        if allowed_file(file.filename):
            fname = secure_filename(file.filename)
            ext = fname.rsplit('.', 1)[1]
            newfname = create_uuid() + '.' + ext
            filePath = os.path.join(app.config['UPLOAD_FOLDER'], newfname)
            if(len(filePath) <= 50):
                file.save(filePath)
                note = Note(title=title, content=content, date=date, filePath=filePath)
                note.author = g.user
                note.protagonist = pet
                db.session.add(note)
                db.session.commit()
                message = "Add note successfully!"
                flash(message, 'success')
                app.logger.info('%s: %s for %s' %(message, current_user.username, pet.name))
                return redirect(url_for('showPet'))
            flash('Please make sure that the full path of the file is less \
                than 50 letters', 'warning')
            return redirect(url_for('note', pet_id=pet.id))
        flash('Supported file type: png, jpg, jpeg', 'warning')
        return redirect(url_for('note', pet_id=pet.id))
    
    note = Note(title=title, content=content, date=date, filePath='')

    note.author = g.user
    note.protagonist = pet

    db.session.add(note)
    db.session.commit()

    flash("Add note successfully!", 'success')
    return redirect(url_for('showPet'))
        

@app.route('/showNote/<int:note_id>')
def showNote(note_id):
    note = Note.query.filter_by(id=note_id).first()
    return render_template('showNote.html', note=note)


@app.route('/deleteNote/<int:note_id>')
def deleteNote(note_id):
    note = Note.query.filter_by(id=note_id).first()
    message = 'Delete note successfully'
    app.logger.info('%s: %s for %s' %(message, current_user.username, note.protagonist.name))
    db.session.delete(note)
    db.session.commit()
    flash(message, 'success')

    return redirect(url_for('showPet'))