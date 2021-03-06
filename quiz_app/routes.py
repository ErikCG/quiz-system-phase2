from flask import render_template, request, redirect, url_for, send_file, send_from_directory, flash
from flask_socketio import SocketIO
from quiz_app import app
from quiz_app import socketio
from quiz_app.forms import *

from datetime import datetime

import json

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home Page')


@app.route("/about")
def about():
    return render_template('about.html', title='About Page')


@app.route("/makequiz")
def makequiz():
    return render_template('makequiz.html', title='Make a Quiz')


@app.route("/takequiz")
def takequiz():
    return render_template('takequiz.html', title='Take a Quiz')

@app.route("/joinLobby", methods=['GET', 'POST'])
def joinLobby():
    form = QuestionTypesForm()
    return render_template('joinLobby.html', title='Join a quiz')
    
@app.route("/hostLobby", methods=['GET', 'POST'])
def hostLobby():
    form = QuestionTypesForm()
    return render_template('hostLobby.html', title='Host a Quiz')

@app.route("/hostPage", methods=['GET', 'POST'])
def hostPage():
    return render_template('hostPage.html', title='Hosting a Quiz')
    
#teacher result page
@app.route("/resultPageH", methods=['GET', 'POST'])
def resultPageT():
    return render_template('resultPageH.html', title='Hosting a Quiz')
#student result page
@app.route("/resultPageS", methods=['GET', 'POST'])
def resultPageS():
    return render_template('resultPageS.html', title='Hosting a Quiz')
    
@app.route("/questiontypes", methods=['GET', 'POST']) 
def questiontypes():
    # This function gets and returns the results of the QuestionTypesForm, which asks users
    # how many questions they want of each question type (multiple choice, true false, and matching)

    form = QuestionTypesForm()  # we create our form object
    if form.is_submitted():
        # Get the results of the form; these are stored as a dictionary, with the key
        # being the variable name of each field on our form (ex. for this one, the keys
        # would be 'multiple_choice', 'true_false', 'matching', and 'submit') and the
        # values being the actual number values the user inputs for those fields
        result = request.form

        # Extracting the values the user submitted in the form
        mc_num = result['multiple_choice']
        tf_num = result['true_false']
        fib_num = result['fill_in_blank']

        # Now we pass the numbers of question types the user entered to the createquiz page
        return redirect(url_for("createquiz", mc_num=mc_num, tf_num=tf_num, fib_num=fib_num))

    return render_template('questiontypes.html', title='Begin Building Your Quiz', form=form)


@app.route("/createquiz/<mc_num>_<tf_num>_<fib_num>", methods=['GET', 'POST'])
def createquiz(mc_num, tf_num, fib_num):
    # Now we can use the number of each question type the user wanted in order to
    # generate the form that actually lets them build the quiz

    # Converting these numbers to integer type:
    mc_num, tf_num, fib_num = int(mc_num), int(tf_num), int(fib_num)

    form = QuizBuilderForm()  # Generating the actual quiz building form
    # TO-DO: figure out what needs to be done once the final form gets submitted
    if form.is_submitted():
        #    do stuff...

        return create_file(form)

    # return redirect(url_for('home')) # redirect to home for now lol

    # NOTE: form.mc accesses the MultipleChoiceForm, form.tf accesses the TrueFalseForm, and
    #       form.match accesses MatchingForm; to access individual fields from each form in your HTML, just
    #       add another method call;
    #           ex. To access the "question" field of the MultipleChoiceForm, you'd do 'form.mc.question'

    return render_template('createquiz.html', title='Create Quiz Results', form=form,
                           mc_num=mc_num, tf_num=tf_num, fib_num=fib_num)


def create_file(form):
    mc_q_list = request.form.getlist('mc-question')
    mc_c1_list = request.form.getlist('mc-c1')
    mc_c2_list = request.form.getlist('mc-c2')
    mc_c3_list = request.form.getlist('mc-c3')
    mc_c4_list = request.form.getlist('mc-c4')
    mc_ans_list = request.form.getlist('mc-answer')

    tf_q_list = request.form.getlist('tf-question')
    tf_ans_list = request.form.getlist('tf-answer')

    fib_q_list = request.form.getlist('fib-question')
    fib_ans_list = request.form.getlist('fib-answer')

    q_dict = dict()

    # NOTE: 'q_dict' is a dictionary of questions that follows the following format:
    #    question-type_question-number : ('question', 'option1', 'option2', 'answer')

    if mc_q_list:
        mc_dict = dict()
        for q in range(len(mc_q_list)):
            mc_dict["q%d"%(q+1)] = [mc_q_list[q], mc_c1_list[q], mc_c2_list[q], mc_c3_list[q], mc_c4_list[q], mc_ans_list[q]]      
        q_dict["mc"] = mc_dict

    if tf_q_list:
        tf_dict = dict()
        for q in range(len(tf_q_list)):
            tf_dict["q%d"%(q+1)] = [tf_q_list[q], tf_ans_list[q]]
        q_dict["tf"] = tf_dict
    
    if fib_q_list:
        fib_dict = dict()
        for q in range(len(fib_q_list)):
            fib_dict["q%d"%(q+1)] = [fib_q_list[q], fib_ans_list[q]]
        q_dict["fib"] = fib_dict
    
    """ # NOTE: 'q_dict' is a dictionary of questions that follows the following format:
        #    question-type: { question-number : ['question', 'option1', 'option2', 'answer'] }
        # 
        # Here's an example output:
        # { 'mc': {
                'q1': ['What color is a banana?', 'Purple', 'Green', 'Yellow', 'Red', 'c']
                }, 
            'tf': {
                'q1': ['Computer mice are mammals. ', 'f'], 
                'q2': ['Today is Wednesday.', 't']
                }, 
            'fib': {
                'q1': ['The best OS is', 'Linux']
                }
            }

    with open("quiz_app/static/quiz.csv", mode="w", newline='') as quiz_file:

        print("writing csv file")

        quiz_writer = csv.writer(quiz_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        if mc_q_list:
            for q in range(len(mc_q_list)):
                quiz_writer.writerow(
                    ["mc_q%d" % (q + 1), mc_q_list[q], mc_c1_list[q], mc_c2_list[q], mc_c3_list[q], mc_c4_list[q],
                     mc_ans_list[q]])

        if tf_q_list:
            for q in range(len(tf_q_list)):
                quiz_writer.writerow(["tf_q%d" % (q + 1), tf_q_list[q], tf_ans_list[q]])

        if fib_q_list:
            for q in range(len(fib_q_list)):
                quiz_writer.writerow(["fib_q%d" % (q + 1), fib_q_list[q], fib_ans_list[q]])

    curr_time = datetime.now().strftime("%c")
    print(curr_time)

    FILEPATH = 'static/quiz.csv'

    # return send_from_directory(app.config["QUIZ_FILE"], "quiz_%s.csv"%(curr_time), as_attachment=True)

    # THE NEXT LINE IS GOOD
    # return send_file('static/quiz.csv', mimetype='text/csv', attachment_filename='quiz_04152020.csv', as_attachment=True)

                quiz_writer.writerow(["fib_q%d"%(q+1), fib_q_list[q], fib_ans_list[q]])

    FILEPATH = 'static/quiz.csv' """
   
   # THE NEXT LINE IS GOOD 
   # return send_file('static/quiz.csv', mimetype='text/csv', attachment_filename='quiz_04152020.csv', as_attachment=True)

    with open('quiz_app/static/quiz.json', 'w') as f:
        json.dump(q_dict, f)

    return redirect(url_for('download_quiz'))

@app.route("/download_quiz")
def download_quiz():
    return render_template('download_quiz.html')


@app.route("/return_file")
def return_file():
    FILEPATH = 'static/quiz.json'

    curr_time = datetime.now().strftime("%m-%d-%Y_%H-%M")
    attach_name = 'quiz_'+curr_time+'.json'

    flash("Your quiz has been downloaded!", 'success')

    return send_file(FILEPATH, attachment_filename=attach_name, as_attachment=True, cache_timeout=0)


@app.route("/host_quiz")
def host_quiz():
    return render_template('host_quiz.html')


@app.route("/find_quiz")
def find_quiz():
    return render_template('find_quiz.html')


@socketio.on('connect')
def test_connect():
    print('User connected')


@socketio.on('host_connect')
def host_connect():
    print('Host connected')
    socketio.emit('host_connect')


@socketio.on('client_connect')
def client_connect():
    print('Client connected')
    clients.append(request.sid)


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    clients.remove(request.sid)


@socketio.on('start_quiz')
def start_quiz(quiz_json):
    socketio.emit('quiz_start', quiz_json)

